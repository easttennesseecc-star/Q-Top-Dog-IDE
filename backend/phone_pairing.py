"""
Phone Pairing System for Q-IDE
Enables seamless pairing between desktop Q-IDE and mobile devices for microphone access
"""

import json
import uuid
import secrets
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from fastapi import HTTPException

class PhonePairingManager:
    """Manages phone device pairing with Q-IDE"""
    
    def __init__(self):
        self.paired_devices: Dict[str, dict] = {}
        self.pairing_codes: Dict[str, dict] = {}
        self.active_sessions: Dict[str, dict] = {}
        
    def generate_pairing_code(self) -> tuple[str, str]:
        """
        Generate a pairing code and QR code for phone connection
        
        Returns:
            tuple: (pairing_code, qr_code_base64)
        """
        # Generate unique pairing code (6 digits)
        pairing_code = secrets.token_hex(3)  # 6 character hex
        
        # Generate device ID
        device_id = str(uuid.uuid4())
        
        # Store pairing request
        self.pairing_codes[pairing_code] = {
            "device_id": device_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=5),
            "verified": False,
            "device_name": None
        }
        
        # Generate QR code data
        qr_data = {
            "pairing_code": pairing_code,
            "device_id": device_id,
            "server_url": "http://127.0.0.1:8000",
            "version": "1.0"
        }
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        qr_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return pairing_code, qr_base64, device_id
    
    def verify_pairing_code(self, pairing_code: str, device_name: str) -> str:
        """
        Verify a pairing code from phone
        
        Args:
            pairing_code: The 6-character code from phone
            device_name: Name of the phone device
            
        Returns:
            str: Session token for this paired device
        """
        if pairing_code not in self.pairing_codes:
            raise HTTPException(status_code=400, detail="Invalid pairing code")
        
        code_data = self.pairing_codes[pairing_code]
        
        # Check if expired
        if datetime.now() > code_data["expires_at"]:
            del self.pairing_codes[pairing_code]
            raise HTTPException(status_code=400, detail="Pairing code expired")
        
        # Mark as verified
        code_data["verified"] = True
        code_data["device_name"] = device_name
        
        # Create device session
        device_id = code_data["device_id"]
        session_token = secrets.token_urlsafe(32)
        
        self.paired_devices[device_id] = {
            "pairing_code": pairing_code,
            "device_name": device_name,
            "session_token": session_token,
            "paired_at": datetime.now(),
            "last_active": datetime.now(),
            "mic_enabled": False,
            "audio_stream": None
        }
        
        # Remove used pairing code
        del self.pairing_codes[pairing_code]
        
        return session_token, device_id
    
    def get_paired_devices(self) -> List[dict]:
        """Get list of all paired devices"""
        return [
            {
                "device_id": device_id,
                "name": data["device_name"],
                "paired_at": data["paired_at"].isoformat(),
                "last_active": data["last_active"].isoformat(),
                "mic_enabled": data["mic_enabled"]
            }
            for device_id, data in self.paired_devices.items()
        ]
    
    def enable_microphone(self, device_id: str, session_token: str) -> bool:
        """Enable microphone for a paired device"""
        if device_id not in self.paired_devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = self.paired_devices[device_id]
        
        if device["session_token"] != session_token:
            raise HTTPException(status_code=403, detail="Invalid session token")
        
        device["mic_enabled"] = True
        device["last_active"] = datetime.now()
        
        return True
    
    def disable_microphone(self, device_id: str) -> bool:
        """Disable microphone for a paired device"""
        if device_id not in self.paired_devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = self.paired_devices[device_id]
        device["mic_enabled"] = False
        
        return True
    
    def unpair_device(self, device_id: str) -> bool:
        """Unpair a device"""
        if device_id in self.paired_devices:
            del self.paired_devices[device_id]
            return True
        return False
    
    def get_active_microphones(self) -> List[str]:
        """Get list of devices with active microphone"""
        return [
            device_id 
            for device_id, data in self.paired_devices.items()
            if data["mic_enabled"]
        ]
    
    def record_audio_chunk(self, device_id: str, audio_data: bytes) -> bool:
        """
        Record audio chunk from phone microphone
        
        Args:
            device_id: ID of paired device
            audio_data: Raw audio bytes
        """
        if device_id not in self.paired_devices:
            return False
        
        device = self.paired_devices[device_id]
        device["last_active"] = datetime.now()
        
        # Audio data would be stored/processed here
        # For now, just mark as received
        return True


# Global instance
phone_pairing_manager = PhonePairingManager()
