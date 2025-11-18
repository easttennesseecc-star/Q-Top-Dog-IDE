"""
Phone Pairing Service for Secure Device Authentication

Handles QR-code based pairing, JWT token generation, and device management.
Supports both Kubernetes deployment and local $400/seat licensing.

Security:
- QR code contains one-time pairing token (expires in 5 minutes)
- After pairing, issues long-lived JWT token (30 days)
- Tokens signed with RS256 (asymmetric encryption)
- Device fingerprinting for security
"""

import asyncio
import os
import json
import logging
import secrets
import uuid
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List, Set
from pathlib import Path
import base64

try:
    import qrcode
    from qrcode.image.pure import PyPNGImage
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logging.warning("qrcode package not installed. Install: pip install qrcode[pil]")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not installed. Install: pip install pyjwt[crypto]")

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from backend.services.pairing_session_store import get_pairing_session_store

logger = logging.getLogger(__name__)


class PairingStatus(str, Enum):
    """Device pairing status"""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class DeviceType(str, Enum):
    """Types of devices"""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    UNKNOWN = "unknown"


@dataclass
class PairingToken:
    """One-time pairing token for QR code"""
    token: str
    user_id: str
    expires_at: datetime
    created_at: datetime
    ip_address: Optional[str] = None
    otp_code: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if token has expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_qr_payload(self) -> Dict[str, Any]:
        """Convert to QR code payload"""
        payload = {
            "token": self.token,
            "expires": self.expires_at.isoformat(),
            "server": "mqtt.topdog-ide.com",  # MQTT broker URL
            "version": "1.0"
        }
        # Optionally embed OTP into QR payload for simplified demo flows
        if os.getenv("PAIRING_QR_EMBED_OTP", "0").lower() in {"1", "true", "yes"} and self.otp_code:
            payload["otp"] = self.otp_code
        return payload


@dataclass
class PairedDevice:
    """Paired mobile device"""
    device_id: str
    user_id: str
    device_name: str
    device_type: DeviceType
    device_fingerprint: str  # Hash of device characteristics
    jwt_token: str
    status: PairingStatus
    paired_at: datetime
    last_seen: datetime
    expires_at: datetime
    
    # Optional device details
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_token: Optional[str] = None  # For push notifications
    ip_address: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if device pairing is active"""
        return (
            self.status == PairingStatus.ACTIVE and
            datetime.utcnow() < self.expires_at
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime to ISO format
        data['paired_at'] = self.paired_at.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data


class PhonePairingService:
    """
    Manages secure phone pairing and device authentication
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        token_expiry_days: int = 30,
        pairing_token_expiry_minutes: int = 5,
        revoked_jti_filename: str = "revoked_jti.json",
    ):
        """
        Initialize phone pairing service
        
        Args:
            storage_path: Path to store pairing data (default: ~/.q-ide/pairing/)
            token_expiry_days: Days until JWT token expires
            pairing_token_expiry_minutes: Minutes until pairing token expires
        """
        self.storage_path = storage_path or Path.home() / ".q-ide" / "pairing"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.token_expiry_days = token_expiry_days
        self.pairing_token_expiry_minutes = pairing_token_expiry_minutes
        
        # RSA keys for JWT signing
        self.private_key_path = self.storage_path / "private_key.pem"
        self.public_key_path = self.storage_path / "public_key.pem"
        
        # Generate or load RSA keys
        self._initialize_keys()
        
        # Active pairing tokens (token -> PairingToken)
        self.pairing_tokens: Dict[str, PairingToken] = {}

        # Paired devices storage file
        self.devices_file = self.storage_path / "paired_devices.json"

        # Load paired devices
        self.paired_devices: Dict[str, PairedDevice] = self._load_devices()
        # Revoked JWT jti values for immediate invalidation (persisted)
        self.revoked_jti: Set[str] = set()
        self.revoked_jti_file = self.storage_path / revoked_jti_filename
        self._load_revoked_jti()

        logger.info(f"PhonePairingService initialized: {self.storage_path}")
        # Audit file path
        self.audit_file = self.storage_path / "pairing_audit.jsonl"
    
    def _initialize_keys(self):
        """Generate or load RSA key pair"""
        if self.private_key_path.exists() and self.public_key_path.exists():
            # Load existing keys
            with open(self.private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(self.public_key_path, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            logger.info("Loaded existing RSA keys")
        else:
            # Generate new keys
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
            # Save keys
            with open(self.private_key_path, 'wb') as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            with open(self.public_key_path, 'wb') as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            
            # Set restrictive permissions
            self.private_key_path.chmod(0o600)
            self.public_key_path.chmod(0o644)
            
            logger.info("Generated new RSA keys")
    
    def _load_devices(self) -> Dict[str, PairedDevice]:
        """Load paired devices from storage"""
        if not self.devices_file.exists():
            return {}
        
        try:
            with open(self.devices_file, 'r') as f:
                data = json.load(f)
            
            devices = {}
            for device_id, device_data in data.items():
                # Convert ISO strings back to datetime
                device_data['paired_at'] = datetime.fromisoformat(device_data['paired_at'])
                device_data['last_seen'] = datetime.fromisoformat(device_data['last_seen'])
                device_data['expires_at'] = datetime.fromisoformat(device_data['expires_at'])
                device_data['status'] = PairingStatus(device_data['status'])
                device_data['device_type'] = DeviceType(device_data['device_type'])
                
                devices[device_id] = PairedDevice(**device_data)
            
            logger.info(f"Loaded {len(devices)} paired devices")
            return devices
        
        except Exception as e:
            logger.error(f"Failed to load paired devices: {e}")
            return {}
    
    def _save_devices(self):
        """Save paired devices to storage"""
        try:
            data = {
                device_id: device.to_dict()
                for device_id, device in self.paired_devices.items()
            }
            
            with open(self.devices_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.paired_devices)} paired devices")
        
        except Exception as e:
            logger.error(f"Failed to save paired devices: {e}")

    def audit(self, event: str, details: Dict[str, Any]) -> None:
        """Append a JSON line to the pairing audit log."""
        try:
            record = {
                "ts": datetime.utcnow().isoformat(),
                "event": event,
                **details,
            }
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write audit record: {e}")

    def _load_revoked_jti(self) -> None:
        """Load revoked JTI entries from disk (best-effort)."""
        if not self.revoked_jti_file.exists():
            return
        try:
            data = json.loads(self.revoked_jti_file.read_text(encoding="utf-8"))
            # Optional format: {"revoked": [..]} or a simple list
            if isinstance(data, dict) and "revoked" in data:
                entries = data.get("revoked", [])
            elif isinstance(data, list):
                entries = data
            else:
                entries = []
            now = datetime.utcnow()
            keep: Set[str] = set()
            for entry in entries:
                if isinstance(entry, dict):
                    jti = entry.get("jti")
                    exp = entry.get("exp")
                    if jti and exp:
                        try:
                            if datetime.fromisoformat(exp) > now:
                                keep.add(jti)
                        except Exception:
                            continue
                elif isinstance(entry, str):
                    keep.add(entry)
            self.revoked_jti = keep
            logger.info(f"Loaded {len(self.revoked_jti)} revoked JTI entries")
        except Exception as e:
            logger.warning(f"Failed loading revoked JTI list: {e}")

    def _persist_revoked_jti(self) -> None:
        """Persist revoked JTI entries as JSON with optional expiry pruning."""
        try:
            # Attempt to decode tokens for expiry hints; store exp when possible.
            entries: List[Dict[str, Any]] = []
            for device in self.paired_devices.values():
                try:
                    payload = jwt.decode(
                        device.jwt_token,
                        self.public_key,
                        algorithms=["RS256"],
                        audience="topdog-mobile",
                        issuer="topdog-ide",
                        options={"verify_exp": False},
                    )
                    jti = payload.get("jti")
                    exp = payload.get("exp")
                    if jti and jti in self.revoked_jti:
                        # Convert numeric exp to ISO when present
                        if isinstance(exp, (int, float)):
                            exp_dt = datetime.utcfromtimestamp(exp)
                            entries.append({"jti": jti, "exp": exp_dt.isoformat()})
                        else:
                            entries.append({"jti": jti, "exp": None})
                except Exception:
                    # Skip tokens we can't parse
                    continue
            # Fallback: if no entries collected but we have revoked_jti, store plain list
            if not entries and self.revoked_jti:
                entries = [{"jti": j, "exp": None} for j in self.revoked_jti]
            serialized = json.dumps({"revoked": entries}, indent=2)
            self.revoked_jti_file.write_text(serialized, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed persisting revoked JTI list: {e}")
    
    def generate_pairing_token(
        self,
        user_id: str,
        ip_address: Optional[str] = None
    ) -> PairingToken:
        """
        Generate one-time pairing token for QR code
        
        Args:
            user_id: User requesting pairing
            ip_address: Optional IP address for security
        
        Returns:
            Pairing token with expiry
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Create pairing token
        # Optionally require an OTP for QR flow (not SMS), configurable via env
        require_qr_otp = os.getenv("PAIRING_QR_REQUIRE_OTP", "0").lower() in {"1", "true", "yes"}
        otp_code = f"{secrets.randbelow(1000000):06d}" if require_qr_otp else None

        pairing_token = PairingToken(
            token=token,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(minutes=self.pairing_token_expiry_minutes),
            created_at=datetime.utcnow(),
            ip_address=ip_address,
            otp_code=otp_code,
        )
        
        # Store token
        self.pairing_tokens[token] = pairing_token

        # Record session for observability
        try:
            get_pairing_session_store().create_qr_session(
                user_id=user_id,
                pairing_token=token,
                expires_at=pairing_token.expires_at,
                otp_code=otp_code,
                ip=ip_address,
            )
        except Exception:
            logger.debug("Failed to record QR pairing session")
        
        logger.info(f"Generated pairing token for user {user_id} (expires in {self.pairing_token_expiry_minutes} minutes)")
        
        return pairing_token
    
    def generate_qr_code(
        self,
        pairing_token: PairingToken,
        output_path: Optional[Path] = None
    ) -> Optional[bytes]:
        """
        Generate QR code image for pairing
        
        Args:
            pairing_token: Pairing token to encode
            output_path: Optional path to save QR code image
        
        Returns:
            QR code image bytes (PNG format)
        """
        if not QRCODE_AVAILABLE:
            logger.error("qrcode package not available")
            return None
        
        try:
            # Create QR code payload
            payload = json.dumps(pairing_token.to_qr_payload())
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(payload)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save if output path provided
            if output_path:
                img.save(output_path)
                logger.info(f"QR code saved to {output_path}")
            
            # Return image bytes
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return None
    
    def verify_pairing_token(self, token: str) -> Optional[PairingToken]:
        """
        Verify pairing token validity
        
        Args:
            token: Pairing token to verify
        
        Returns:
            PairingToken if valid, None otherwise
        """
        pairing_token = self.pairing_tokens.get(token)
        
        if not pairing_token:
            logger.warning(f"Pairing token not found: {token[:8]}...")
            return None
        
        if pairing_token.is_expired():
            logger.warning(f"Pairing token expired: {token[:8]}...")
            # Remove expired token
            del self.pairing_tokens[token]
            return None
        
        return pairing_token
    
    def _generate_device_fingerprint(
        self,
        device_id: str,
        device_type: DeviceType,
        os_version: Optional[str],
        app_version: Optional[str]
    ) -> str:
        """Generate unique device fingerprint"""
        data = f"{device_id}|{device_type.value}|{os_version}|{app_version}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _generate_jwt_token(
        self,
        user_id: str,
        device_id: str,
        device_fingerprint: str,
        jti: Optional[str] = None
    ) -> str:
        """Generate JWT token for device"""
        if not JWT_AVAILABLE:
            raise RuntimeError("PyJWT package required")
        
        if jti is None:
            jti = str(uuid.uuid4())
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "fingerprint": device_fingerprint,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=self.token_expiry_days),
            "jti": jti,
            "iss": "topdog-ide",
            "aud": "topdog-mobile"
        }
        
        # Sign with RSA private key
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm="RS256"
        )
        
        return token
    
    def pair_device(
        self,
        pairing_token_str: str,
        device_id: str,
        device_name: str,
        device_type: DeviceType,
        os_version: Optional[str] = None,
        app_version: Optional[str] = None,
        push_token: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Optional[PairedDevice]:
        """
        Pair a new device using pairing token
        
        Args:
            pairing_token_str: One-time pairing token from QR code
            device_id: Unique device identifier
            device_name: User-friendly device name
            device_type: Type of device (iOS/Android/Web)
            os_version: Operating system version
            app_version: App version
            push_token: Push notification token
            ip_address: Device IP address
        
        Returns:
            Paired device with JWT token
        """
        # Verify pairing token
        pairing_token = self.verify_pairing_token(pairing_token_str)
        if not pairing_token:
            logger.error("Invalid or expired pairing token")
            return None
        
        # Check if device already paired
        if device_id in self.paired_devices:
            existing_device = self.paired_devices[device_id]
            if existing_device.is_active():
                logger.warning(f"Device already paired: {device_id}")
                return existing_device
        
        # Generate device fingerprint
        fingerprint = self._generate_device_fingerprint(
            device_id, device_type, os_version, app_version
        )
        
        # Generate JWT token
        jti = str(uuid.uuid4())
        jwt_token = self._generate_jwt_token(
            pairing_token.user_id,
            device_id,
            fingerprint,
            jti=jti
        )
        
        # Create paired device
        paired_device = PairedDevice(
            device_id=device_id,
            user_id=pairing_token.user_id,
            device_name=device_name,
            device_type=device_type,
            device_fingerprint=fingerprint,
            jwt_token=jwt_token,
            status=PairingStatus.ACTIVE,
            paired_at=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=self.token_expiry_days),
            os_version=os_version,
            app_version=app_version,
            push_token=push_token,
            ip_address=ip_address
        )
        
        # Store device
        self.paired_devices[device_id] = paired_device
        self._save_devices()
        
        # Remove used pairing token
        del self.pairing_tokens[pairing_token_str]

        # Update session status
        try:
            get_pairing_session_store().mark_accepted(pairing_token_str, device_id, device_name, device_type.value)
        except Exception:
            logger.debug("Failed to update session to accepted")

        logger.info(f"Device paired successfully: {device_name} ({device_id}) jti={jti}")

        return paired_device
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload
        
        Args:
            token: JWT token to verify
        
        Returns:
            Token payload if valid, None otherwise
        """
        if not JWT_AVAILABLE:
            logger.error("PyJWT package not available")
            return None
        
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                audience="topdog-mobile",
                issuer="topdog-ide"
            )
            jti = payload.get("jti")
            if jti and jti in self.revoked_jti:
                logger.warning(f"JWT jti revoked: {jti}")
                return None
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def get_device(self, device_id: str) -> Optional[PairedDevice]:
        """Get paired device by ID"""
        return self.paired_devices.get(device_id)
    
    def get_user_devices(self, user_id: str) -> List[PairedDevice]:
        """Get all paired devices for a user"""
        return [
            device for device in self.paired_devices.values()
            if device.user_id == user_id
        ]
    
    def update_last_seen(self, device_id: str):
        """Update device last seen timestamp"""
        device = self.paired_devices.get(device_id)
        if device:
            device.last_seen = datetime.utcnow()
            self._save_devices()
    
    def revoke_device(self, device_id: str) -> bool:
        """Revoke device pairing and invalidate JWT immediately."""
        device = self.paired_devices.get(device_id)
        if device:
            device.status = PairingStatus.REVOKED
            # Extract jti from existing token if possible
            if JWT_AVAILABLE:
                try:
                    payload = jwt.decode(
                        device.jwt_token,
                        self.public_key,
                        algorithms=["RS256"],
                        audience="topdog-mobile",
                        issuer="topdog-ide",
                        options={"verify_exp": False}
                    )
                    jti = payload.get("jti")
                    if jti:
                        self.revoked_jti.add(jti)
                        logger.info(f"Added jti to revocation list: {jti}")
                except Exception as e:
                    logger.warning(f"Failed to decode JWT for revocation: {e}")
            self._save_devices()
            self._persist_revoked_jti()
            logger.info(f"Device revoked: {device_id}")
            try:
                get_pairing_session_store().mark_revoked(device_id)
            except Exception:
                logger.debug("Failed to mark session revoked")
            return True
        return False
    
    def suspend_device(self, device_id: str) -> bool:
        """Temporarily suspend device"""
        device = self.paired_devices.get(device_id)
        if device:
            device.status = PairingStatus.SUSPENDED
            self._save_devices()
            logger.info(f"Device suspended: {device_id}")
            return True
        return False
    
    def reactivate_device(self, device_id: str) -> bool:
        """Reactivate suspended device"""
        device = self.paired_devices.get(device_id)
        if device:
            device.status = PairingStatus.ACTIVE
            self._save_devices()
            logger.info(f"Device reactivated: {device_id}")
            return True
        return False


# Singleton instance
_pairing_service: Optional[PhonePairingService] = None


def get_pairing_service() -> PhonePairingService:
    """Get singleton pairing service instance"""
    global _pairing_service
    if _pairing_service is None:
        _pairing_service = PhonePairingService()
    return _pairing_service
