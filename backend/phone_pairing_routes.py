"""
Phone Pairing API Routes for Q-IDE
Handles QR code generation, device pairing, and microphone streaming
"""

from fastapi import APIRouter, HTTPException, WebSocket, BackgroundTasks
from pydantic import BaseModel
from typing import List
from phone_pairing import phone_pairing_manager
import asyncio
import json

# Create router
router = APIRouter(prefix="/api/phone", tags=["phone-pairing"])


# ============================================================================
# Models
# ============================================================================

class PairingCodeResponse(BaseModel):
    """Response with pairing code and QR code"""
    pairing_code: str
    qr_code_base64: str
    device_id: str
    expires_in_seconds: int = 300
    instructions: str = "Scan this QR code with your phone or enter the pairing code"


class PairingVerifyRequest(BaseModel):
    """Phone app sends pairing code to verify"""
    pairing_code: str
    device_name: str


class PairingVerifyResponse(BaseModel):
    """Server confirms pairing"""
    status: str = "paired"
    session_token: str
    device_id: str
    message: str = "Phone successfully paired with Q-IDE"


class PairedDevice(BaseModel):
    """Information about a paired device"""
    device_id: str
    name: str
    paired_at: str
    last_active: str
    mic_enabled: bool


class MicrophoneToggleRequest(BaseModel):
    """Request to enable/disable microphone"""
    device_id: str
    enable: bool


# ============================================================================
# Endpoints - Desktop (Q-IDE main app)
# ============================================================================

@router.post("/start-pairing", response_model=PairingCodeResponse)
async def start_pairing():
    """
    Start phone pairing process
    Desktop app calls this to get QR code and pairing code
    
    Returns:
        QR code (base64) and 6-character pairing code
    """
    pairing_code, qr_base64, device_id = phone_pairing_manager.generate_pairing_code()
    
    return PairingCodeResponse(
        pairing_code=pairing_code,
        qr_code_base64=qr_base64,
        device_id=device_id
    )


@router.get("/paired-devices", response_model=List[PairedDevice])
async def get_paired_devices():
    """Get list of all paired devices"""
    return phone_pairing_manager.get_paired_devices()


@router.post("/unpair")
async def unpair_device(device_id: str):
    """Unpair a device"""
    if phone_pairing_manager.unpair_device(device_id):
        return {"status": "success", "message": f"Device {device_id} unpaired"}
    else:
        raise HTTPException(status_code=404, detail="Device not found")


@router.get("/active-mics")
async def get_active_microphones():
    """Get list of devices with active microphone"""
    return {
        "active_devices": phone_pairing_manager.get_active_microphones(),
        "count": len(phone_pairing_manager.get_active_microphones())
    }


@router.post("/toggle-mic")
async def toggle_microphone(request: MicrophoneToggleRequest):
    """Enable or disable microphone for a device"""
    device_id = request.device_id
    
    if request.enable:
        phone_pairing_manager.enable_microphone(device_id, "")  # Token validation would happen here
        return {"status": "enabled", "device_id": device_id}
    else:
        phone_pairing_manager.disable_microphone(device_id)
        return {"status": "disabled", "device_id": device_id}


# ============================================================================
# Endpoints - Mobile App
# ============================================================================

@router.post("/verify-pairing", response_model=PairingVerifyResponse)
async def verify_pairing(request: PairingVerifyRequest):
    """
    Phone app calls this to verify pairing code
    
    Args:
        pairing_code: 6-character code user entered
        device_name: Name of phone (e.g., "iPhone 15", "Samsung Galaxy")
        
    Returns:
        Session token if successful
    """
    session_token, device_id = phone_pairing_manager.verify_pairing_code(
        request.pairing_code,
        request.device_name
    )
    
    return PairingVerifyResponse(
        session_token=session_token,
        device_id=device_id,
        message=f"Successfully paired with {request.device_name}"
    )


@router.post("/mic/enable/{device_id}")
async def enable_mic(device_id: str):
    """Phone requests to enable microphone"""
    phone_pairing_manager.enable_microphone(device_id, "")
    
    return {
        "status": "enabled",
        "message": "Microphone activated on phone",
        "device_id": device_id
    }


@router.post("/mic/disable/{device_id}")
async def disable_mic(device_id: str):
    """Phone requests to disable microphone"""
    phone_pairing_manager.disable_microphone(device_id)
    
    return {
        "status": "disabled",
        "message": "Microphone deactivated",
        "device_id": device_id
    }


@router.get("/status/{device_id}")
async def get_device_status(device_id: str):
    """Get status of a paired device"""
    devices = phone_pairing_manager.paired_devices
    
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = devices[device_id]
    
    return {
        "device_id": device_id,
        "name": device["device_name"],
        "mic_enabled": device["mic_enabled"],
        "paired_at": device["paired_at"].isoformat(),
        "last_active": device["last_active"].isoformat()
    }


# ============================================================================
# WebSocket - Real-time Audio Streaming
# ============================================================================

@router.websocket("/ws/audio/{device_id}")
async def websocket_audio_stream(websocket: WebSocket, device_id: str):
    """
    WebSocket endpoint for real-time audio streaming from phone microphone
    Phone connects here to send audio chunks
    Desktop receives audio stream
    """
    await websocket.accept()
    
    devices = phone_pairing_manager.paired_devices
    if device_id not in devices:
        await websocket.close(code=4000, reason="Device not found")
        return
    
    try:
        while True:
            # Receive audio chunk from phone
            data = await websocket.receive_bytes()
            
            # Record the audio chunk
            phone_pairing_manager.record_audio_chunk(device_id, data)
            
            # Broadcast to connected clients (desktop app listening)
            # This would integrate with the chat/voice processing system
            await websocket.send_json({
                "status": "received",
                "bytes": len(data),
                "device_id": device_id
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Check if phone pairing service is running"""
    return {
        "status": "online",
        "paired_devices": len(phone_pairing_manager.paired_devices),
        "active_microphones": len(phone_pairing_manager.get_active_microphones())
    }
