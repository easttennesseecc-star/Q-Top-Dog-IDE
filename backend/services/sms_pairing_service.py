"""
SMS-Based Phone Pairing Service

Easy phone pairing via phone number and SMS link.
User enters phone number, receives text with link, clicks to pair instantly.
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import json
from backend.services.pairing_session_store import get_pairing_session_store

logger = logging.getLogger(__name__)

# SMS Provider integrations (graceful degradation if not installed)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS pairing will use mock mode. Install: pip install twilio")

try:
    import boto3
    AWS_SNS_AVAILABLE = True
except ImportError:
    AWS_SNS_AVAILABLE = False
    logger.warning("AWS SNS not available. Install: pip install boto3")


@dataclass
class PairingInvite:
    """SMS pairing invite sent to phone"""
    invite_code: str
    phone_number: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    pairing_link: str
    status: str = "pending"  # pending, accepted, expired, cancelled
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    otp_code: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if invite has expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "invite_code": self.invite_code,
            "phone_number": self.phone_number,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "pairing_link": self.pairing_link,
            "status": self.status,
            "device_info": self.device_info,
            "ip_address": self.ip_address
        }


class SMSPairingService:
    """
    SMS-based phone pairing service
    
    Makes phone pairing extremely easy:
    1. User enters phone number in IDE
    2. IDE sends SMS with pairing link
    3. User clicks link on phone
    4. Phone opens pairing page in browser/app
    5. User taps "Accept" - done!
    
    No QR scanning, no manual token entry, just click and done.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        invite_expiry_minutes: int = 15,
        base_url: str = "https://pair.topdog-ide.com"
    ):
        """
        Initialize SMS pairing service
        
        Args:
            storage_path: Directory to store invites (default: ~/.q-ide/pairing)
            invite_expiry_minutes: Minutes before invite expires (default: 15)
            base_url: Base URL for pairing links
        """
        if storage_path is None:
            storage_path = os.path.join(os.path.expanduser("~"), ".q-ide", "pairing")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.invite_expiry_minutes = invite_expiry_minutes
        self.base_url = base_url

        # Store active invites
        self.invites_file = self.storage_path / "pairing_invites.json"
        self.invites: Dict[str, PairingInvite] = {}
        self._load_invites()
        
        # Initialize SMS providers
        self._init_sms_providers()
        
        logger.info(f"SMS Pairing Service initialized (expiry: {invite_expiry_minutes}min)")
    
    def _init_sms_providers(self):
        """Initialize SMS service providers"""
        # Twilio setup
        # Use broad Any typing to avoid optional third-party typing requirements at import time
        from typing import Any as _Any  # local alias to avoid polluting module namespace
        self.twilio_client: _Any = None
        self.twilio_phone: Optional[str] = None
        if TWILIO_AVAILABLE:
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
            
            if account_sid and auth_token and self.twilio_phone:
                try:
                    self.twilio_client = TwilioClient(account_sid, auth_token)
                    logger.info("✓ Twilio SMS provider configured")
                except Exception as e:
                    logger.warning(f"Twilio initialization failed: {e}")
        
        # AWS SNS setup
        self.sns_client: _Any = None
        if AWS_SNS_AVAILABLE:
            try:
                self.sns_client = boto3.client('sns')
                logger.info("✓ AWS SNS provider configured")
            except Exception as e:
                logger.warning(f"AWS SNS initialization failed: {e}")
        
        if not self.twilio_client and not self.sns_client:
            logger.warning("⚠ No SMS providers configured - using MOCK mode")
            logger.warning("   Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
            logger.warning("   Or configure AWS SNS credentials")
    
    def _load_invites(self):
        """Load invites from storage"""
        if not self.invites_file.exists():
            return
        
        try:
            with open(self.invites_file, 'r') as f:
                data = json.load(f)
            
            for invite_code, invite_data in data.items():
                # Convert ISO datetime strings back to datetime objects
                invite_data['created_at'] = datetime.fromisoformat(invite_data['created_at'])
                invite_data['expires_at'] = datetime.fromisoformat(invite_data['expires_at'])
                self.invites[invite_code] = PairingInvite(**invite_data)
            
            # Clean up expired invites
            self._cleanup_expired_invites()
            
            logger.info(f"Loaded {len(self.invites)} active pairing invites")
        
        except Exception as e:
            logger.error(f"Failed to load invites: {e}")
            self.invites = {}
    
    def _save_invites(self):
        """Save invites to storage"""
        try:
            data = {
                code: invite.to_dict()
                for code, invite in self.invites.items()
            }
            
            with open(self.invites_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save invites: {e}")
    
    def _cleanup_expired_invites(self):
        """Remove expired invites"""
        expired = [
            code for code, invite in self.invites.items()
            if invite.is_expired()
        ]
        
        for code in expired:
            del self.invites[code]
        
        if expired:
            self._save_invites()
            logger.info(f"Cleaned up {len(expired)} expired invites")
    
    def send_pairing_invite(
        self,
        phone_number: str,
        user_id: str,
        user_name: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Optional[PairingInvite]:
        """
        Send SMS pairing invite to phone number
        
        Args:
            phone_number: Phone number (E.164 format: +1234567890)
            user_id: User ID requesting pairing
            user_name: Optional user name for personalization
            ip_address: IP address of request
        
        Returns:
            PairingInvite if successful, None if failed
        """
        # Validate phone number format
        if not phone_number.startswith('+'):
            logger.error(f"Phone number must be in E.164 format (+1234567890): {phone_number}")
            return None
        
        # Generate unique invite code
        invite_code = secrets.token_urlsafe(32)
        
        # Create pairing link
        pairing_link = f"{self.base_url}/pair?code={invite_code}"
        
        # Create invite
        otp_code = f"{secrets.randbelow(1000000):06d}"
        invite = PairingInvite(
            invite_code=invite_code,
            phone_number=phone_number,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=self.invite_expiry_minutes),
            pairing_link=pairing_link,
            ip_address=ip_address,
            otp_code=otp_code
        )
        
        # Compose SMS message
        greeting = f"Hi {user_name}! " if user_name else "Hi! "
        message = (
            f"{greeting}Click to pair your phone with Q-IDE:\n\n"
            f"{pairing_link}\n\n"
            f"Security code: {otp_code}\n"
            f"Link expires in {self.invite_expiry_minutes} minutes."
        )
        
        # Send SMS
        success = self._send_sms(phone_number, message)
        
        if success:
            # Store invite
            self.invites[invite_code] = invite
            self._save_invites()
            # Record unified session
            try:
                get_pairing_session_store().create_sms_session(
                    user_id=user_id,
                    invite_code=invite_code,
                    expires_at=invite.expires_at,
                    otp_code=otp_code,
                    phone=phone_number,
                    ip=ip_address,
                )
            except Exception:
                logger.debug("Failed to record SMS pairing session")
            
            logger.info(f"✓ Sent pairing invite to {phone_number}")
            return invite
        else:
            logger.error(f"Failed to send pairing invite to {phone_number}")
            return None
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS via available provider
        
        Priority: Twilio > AWS SNS > Mock (dev mode)
        """
        # Try Twilio first
        if self.twilio_client:
            try:
                msg = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=phone_number
                )
                logger.info(f"Twilio SMS sent: {msg.sid}")
                return True
            except Exception as e:
                logger.error(f"Twilio SMS failed: {e}")
        
        # Try AWS SNS
        if self.sns_client:
            try:
                response = self.sns_client.publish(
                    PhoneNumber=phone_number,
                    Message=message
                )
                logger.info(f"AWS SNS sent: {response['MessageId']}")
                return True
            except Exception as e:
                logger.error(f"AWS SNS failed: {e}")
        
        # Mock mode for development
        logger.warning("=" * 60)
        logger.warning("MOCK SMS (Development Mode)")
        logger.warning(f"To: {phone_number}")
        logger.warning(f"Message:\n{message}")
        logger.warning("=" * 60)
        logger.warning("To enable real SMS:")
        logger.warning("  Option 1 - Twilio: pip install twilio")
        logger.warning("    Set: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        logger.warning("  Option 2 - AWS SNS: pip install boto3")
        logger.warning("    Configure AWS credentials")
        logger.warning("=" * 60)
        
        # In mock mode, still return True so dev can test
        return True
    
    def verify_invite(self, invite_code: str) -> Optional[PairingInvite]:
        """
        Verify pairing invite code
        
        Args:
            invite_code: Invite code from SMS link
        
        Returns:
            PairingInvite if valid, None if invalid/expired
        """
        invite = self.invites.get(invite_code)
        
        if not invite:
            logger.warning(f"Invalid invite code: {invite_code}")
            return None
        
        if invite.is_expired():
            logger.warning(f"Expired invite code: {invite_code}")
            invite.status = "expired"
            self._save_invites()
            return None
        
        if invite.status != "pending":
            logger.warning(f"Invite already {invite.status}: {invite_code}")
            return None
        
        return invite
    
    def accept_invite(
        self,
        invite_code: str,
        device_id: str,
        device_name: str,
        device_type: str,
        os_version: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> bool:
        """
        Accept pairing invite (user clicked link and tapped accept)
        
        Args:
            invite_code: Invite code from SMS link
            device_id: Unique device identifier
            device_name: User-friendly device name
            device_type: Device type (ios/android/web)
            os_version: OS version
            app_version: App version
        
        Returns:
            True if accepted successfully
        """
        invite = self.verify_invite(invite_code)
        
        if not invite:
            return False
        
        # Store device info
        invite.device_info = {
            "device_id": device_id,
            "device_name": device_name,
            "device_type": device_type,
            "os_version": os_version,
            "app_version": app_version
        }
        
        invite.status = "accepted"
        self._save_invites()
        # Mark session accepted
        try:
            get_pairing_session_store().mark_accepted(invite_code, device_id, device_name, device_type)
        except Exception:
            logger.debug("Failed to mark SMS session accepted")
        
        logger.info(f"✓ Invite accepted: {invite_code} -> {device_name}")
        return True
    
    def cancel_invite(self, invite_code: str) -> bool:
        """Cancel a pending invite"""
        invite = self.invites.get(invite_code)
        
        if not invite:
            return False
        
        invite.status = "cancelled"
        self._save_invites()
        
        logger.info(f"Cancelled invite: {invite_code}")
        return True
    
    def get_invite(self, invite_code: str) -> Optional[PairingInvite]:
        """Get invite by code"""
        return self.invites.get(invite_code)
    
    def get_user_invites(self, user_id: str) -> list:
        """Get all invites for a user"""
        return [
            invite for invite in self.invites.values()
            if invite.user_id == user_id
        ]
    
    def resend_invite(self, invite_code: str) -> bool:
        """
        Resend SMS for existing invite
        
        Useful if user didn't receive first SMS
        """
        invite = self.invites.get(invite_code)
        
        if not invite:
            logger.error(f"Cannot resend - invite not found: {invite_code}")
            return False
        
        if invite.status != "pending":
            logger.error(f"Cannot resend - invite is {invite.status}")
            return False
        
        # Extend expiry
        invite.expires_at = datetime.utcnow() + timedelta(minutes=self.invite_expiry_minutes)
        self._save_invites()
        
        # Resend SMS
        message = (
            f"Q-IDE Pairing Link (Resent):\n\n"
            f"{invite.pairing_link}\n\n"
            f"Link expires in {self.invite_expiry_minutes} minutes."
        )
        
        success = self._send_sms(invite.phone_number, message)
        
        if success:
            logger.info(f"✓ Resent invite to {invite.phone_number}")
        
        return success


# Singleton instance
_sms_pairing_service: Optional[SMSPairingService] = None


def get_sms_pairing_service() -> SMSPairingService:
    """Get singleton SMS pairing service instance"""
    global _sms_pairing_service
    
    if _sms_pairing_service is None:
        _sms_pairing_service = SMSPairingService()
    
    return _sms_pairing_service


def initialize_sms_pairing_service(
    storage_path: Optional[str] = None,
    invite_expiry_minutes: int = 15,
    base_url: str = "https://pair.topdog-ide.com"
) -> SMSPairingService:
    """Initialize SMS pairing service with custom settings"""
    global _sms_pairing_service
    
    _sms_pairing_service = SMSPairingService(
        storage_path=storage_path,
        invite_expiry_minutes=invite_expiry_minutes,
        base_url=base_url
    )
    
    return _sms_pairing_service
