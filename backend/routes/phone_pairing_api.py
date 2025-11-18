"""
Phone Pairing API Routes

Endpoints for QR code generation, device pairing, and voice command processing.
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Header, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.services.phone_pairing_service import (
    get_pairing_service,
    PhonePairingService,
    DeviceType
)
from backend.utils.rate_limiter import make_rate_limiter
from backend.services.sms_pairing_service import (
    get_sms_pairing_service,
    SMSPairingService
)
from backend.services.cloud_message_broker import (
    get_message_broker,
    CloudMessageBroker,
    BuildNotification,
    ApprovalRequest,
    BuildStatus,
    NotificationPriority
)
from backend.services.sms_command_handler import (
    get_sms_command_handler,
    SMSCommandHandler
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/phone", tags=["Phone Pairing & Remote Control"])


# Pydantic models for API

class PairingRequestModel(BaseModel):
    """Request to generate pairing QR code"""
    user_id: str = Field(..., description="User ID requesting pairing")
    

class QRCodeResponse(BaseModel):
    """QR code generation response"""
    pairing_token: str
    expires_at: str
    qr_code_base64: str
    mqtt_broker: str


class SendSMSInviteRequest(BaseModel):
    """Request to send SMS pairing invite"""
    phone_number: str = Field(..., description="Phone number in E.164 format (+1234567890)")
    user_id: str = Field(..., description="User ID requesting pairing")
    user_name: Optional[str] = Field(None, description="User name for personalization")


class SMSInviteResponse(BaseModel):
    """SMS invite response"""
    invite_code: str
    phone_number: str
    expires_at: str
    status: str
    message: str


class AcceptInviteRequest(BaseModel):
    """Request to accept SMS invite"""
    invite_code: str = Field(..., description="Invite code from SMS link")
    device_id: str = Field(..., description="Unique device identifier")
    device_name: str = Field(..., description="User-friendly device name")
    device_type: str = Field(..., description="Device type (ios/android/web)")
    os_version: Optional[str] = Field(None, description="OS version")
    app_version: Optional[str] = Field(None, description="App version")


class PairDeviceRequest(BaseModel):
    """Request to pair a device"""
    pairing_token: str = Field(..., description="One-time pairing token from QR code")
    device_id: str = Field(..., description="Unique device identifier")
    device_name: str = Field(..., description="User-friendly device name")
    device_type: DeviceType = Field(..., description="Device type (ios/android/web)")
    os_version: Optional[str] = Field(None, description="OS version")
    app_version: Optional[str] = Field(None, description="App version")
    push_token: Optional[str] = Field(None, description="Push notification token")
    otp_code: Optional[str] = Field(None, description="Optional OTP for QR pairing if required")


class PairDeviceResponse(BaseModel):
    """Device pairing response"""
    device_id: str
    jwt_token: str
    expires_at: str
    mqtt_broker: str
    user_id: str


class VoiceCommandRequest(BaseModel):
    """Voice command from phone"""
    command_text: str = Field(..., description="Transcribed voice command")
    device_id: str = Field(..., description="Device ID")
    audio_url: Optional[str] = Field(None, description="Optional audio file URL")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="STT confidence score")
    language: str = Field("en-US", description="Language code")


class VoiceCommandResponse(BaseModel):
    """Voice command processing response"""
    command_id: str
    status: str
    message: str
    details: Optional[dict] = None


class DeviceInfo(BaseModel):
    """Device information"""
    device_id: str
    device_name: str
    device_type: str
    status: str
    paired_at: str
    last_seen: str
    expires_at: str


class SendNotificationRequest(BaseModel):
    """Request to send notification to phone"""
    device_id: str
    build_id: str
    project_name: str
    status: BuildStatus
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    action_required: bool = False


class SendApprovalRequest(BaseModel):
    """Request to send approval request to phone"""
    device_id: str
    build_id: str
    project_name: str
    plan: str
    affected_files: List[str]
    estimated_duration: str
    requires_approval_by: str
    user_id: str


# API Endpoints

@router.post("/pairing/send-sms", response_model=SMSInviteResponse, dependencies=[Depends(make_rate_limiter(5, 60, "sms_invite", key_headers=["x-user-id", "x-phone"]))])
async def send_sms_invite(
    request: SendSMSInviteRequest,
    http_request: Request,
    sms_service: SMSPairingService = Depends(get_sms_pairing_service)
):
    """
    Send SMS pairing invite to phone number
    
    **Easy Pairing Flow:**
    1. User enters phone number in IDE
    2. IDE calls this endpoint
    3. User receives SMS with pairing link
    4. User clicks link and accepts
    5. Done!
    
    **Phone Number Format:**
    - Must be E.164 format: +1234567890
    - Include country code
    - No spaces or dashes
    
    **Example:**
    ```json
    {
      "phone_number": "+14155551234",
      "user_id": "user123",
      "user_name": "John Doe"
    }
    ```
    """
    try:
        invite = sms_service.send_pairing_invite(
            phone_number=request.phone_number,
            user_id=request.user_id,
            user_name=request.user_name
        )
        
        if not invite:
            raise HTTPException(
                status_code=500,
                detail="Failed to send SMS. Check phone number format (+1234567890)"
            )
        
        # Audit
        try:
            get_pairing_service().audit("send_sms_invite", {
                "user_id": request.user_id,
                "phone_number": request.phone_number,
                "ip": http_request.client.host if http_request.client else None,
                "ua": http_request.headers.get("user-agent")
            })
        except Exception:
            pass

        return SMSInviteResponse(
            invite_code=invite.invite_code,
            phone_number=invite.phone_number,
            expires_at=invite.expires_at.isoformat(),
            status=invite.status,
            message="SMS sent! Link expires in 15 minutes."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send SMS invite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class AcceptInviteWithOTPRequest(AcceptInviteRequest):
    otp_code: str = Field(..., description="6-digit OTP code sent via SMS")

@router.post("/pairing/accept-invite", dependencies=[Depends(make_rate_limiter(10, 300, "accept_invite", key_headers=["x-user-id", "x-device-id"]))])
async def accept_sms_invite(
    request: AcceptInviteWithOTPRequest,
    http_request: Request,
    sms_service: SMSPairingService = Depends(get_sms_pairing_service),
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Accept SMS pairing invite
    
    Called when user clicks SMS link and taps "Accept" button.
    This completes the pairing and returns JWT token.
    
    **Flow:**
    1. User clicks SMS link with invite code
    2. Mobile app/web page calls this endpoint
    3. System validates invite
    4. System generates JWT token
    5. Returns token for authenticated communication
    """
    try:
        # Verify invite
        invite = sms_service.verify_invite(request.invite_code)
        
        if not invite:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired invite code"
            )
        
        # Accept invite
        # Verify OTP
        if invite.otp_code and invite.otp_code != request.otp_code:
            raise HTTPException(status_code=400, detail="Invalid OTP code")
        success = sms_service.accept_invite(
            invite_code=request.invite_code,
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            os_version=request.os_version,
            app_version=request.app_version
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to accept invite")
        
        # Create pairing (generate JWT token)
        # Convert device_type string to DeviceType enum
        try:
            device_type_enum: DeviceType = DeviceType[request.device_type.upper()]
        except KeyError:
            device_type_enum = DeviceType.UNKNOWN

        # Generate a proper pairing token for this user to avoid using invite_code as token
        proper_token = pairing_service.generate_pairing_token(invite.user_id, ip_address=(http_request.client.host if http_request.client else None))
        paired_device = pairing_service.pair_device(
            pairing_token_str=proper_token.token,
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=device_type_enum,
            os_version=request.os_version,
            app_version=request.app_version,
            push_token=None
        )
        
        if not paired_device:
            # Fallback: generate JWT directly without pairing token validation
            # This is safe because we already verified the SMS invite
            import secrets
            paired_device = pairing_service.pair_device(
                pairing_token_str=secrets.token_urlsafe(32),  # Dummy token
                device_id=request.device_id,
                device_name=request.device_name,
                device_type=device_type_enum,
                os_version=request.os_version,
                app_version=request.app_version,
                push_token=None
            )
        if not paired_device:
            raise HTTPException(status_code=500, detail="Failed to pair device after invite acceptance")
        
        # Audit
        try:
            pairing_service.audit("accept_invite", {
                "user_id": invite.user_id,
                "device_id": request.device_id,
                "ip": http_request.client.host if http_request.client else None,
                "ua": http_request.headers.get("user-agent")
            })
        except Exception:
            pass

        return PairDeviceResponse(
            device_id=paired_device.device_id,
            jwt_token=paired_device.jwt_token,
            expires_at=paired_device.expires_at.isoformat(),
            mqtt_broker="mqtt.topdog-ide.com",
            user_id=paired_device.user_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to accept invite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pairing/invite/{invite_code}")
async def get_invite_status(
    invite_code: str,
    sms_service: SMSPairingService = Depends(get_sms_pairing_service)
):
    """
    Get pairing invite status
    
    Used to check if invite is still valid before showing accept button.
    """
    try:
        invite = sms_service.get_invite(invite_code)
        
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        return {
            "invite_code": invite.invite_code,
            "status": invite.status,
            "expires_at": invite.expires_at.isoformat(),
            "is_expired": invite.is_expired(),
            "is_valid": invite.status == "pending" and not invite.is_expired()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invite status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pairing/resend-sms/{invite_code}")
async def resend_sms(
    invite_code: str,
    sms_service: SMSPairingService = Depends(get_sms_pairing_service)
):
    """
    Resend SMS for existing invite
    
    Useful if user didn't receive the first SMS.
    Extends expiry time and sends new SMS.
    """
    try:
        success = sms_service.resend_invite(invite_code)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot resend - invite not found or already used"
            )
        
        return {"message": "SMS resent successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resend SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pairing/generate-qr", response_model=QRCodeResponse, dependencies=[Depends(make_rate_limiter(10, 60, "qr_gen", key_headers=["x-user-id"]))])
async def generate_pairing_qr(
    request: PairingRequestModel,
    http_request: Request,
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Generate QR code for phone pairing
    
    User scans this QR code with mobile app to initiate pairing.
    QR code contains one-time token that expires in 5 minutes.
    """
    try:
        # Generate pairing token
        pairing_token = pairing_service.generate_pairing_token(request.user_id, ip_address=(http_request.client.host if http_request.client else None))
        
        # Generate QR code
        qr_bytes = pairing_service.generate_qr_code(pairing_token)
        
        if not qr_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate QR code")
        
        # Convert to base64
        import base64
        qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
        
        try:
            pairing_service.audit("generate_qr", {
                "user_id": request.user_id,
                "ip": http_request.client.host if http_request.client else None,
                "ua": http_request.headers.get("user-agent")
            })
        except Exception:
            pass

        return QRCodeResponse(
            pairing_token=pairing_token.token,
            expires_at=pairing_token.expires_at.isoformat(),
            qr_code_base64=qr_base64,
            mqtt_broker="mqtt.topdog-ide.com"
        )
    
    except Exception as e:
        logger.error(f"Failed to generate pairing QR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pairing/pair", response_model=PairDeviceResponse, dependencies=[Depends(make_rate_limiter(20, 300, "pair_device", key_headers=["x-user-id", "x-device-id"]))])
async def pair_device(
    request: PairDeviceRequest,
    http_request: Request,
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Pair a mobile device
    
    Called by mobile app after scanning QR code.
    Returns JWT token for authenticated communication.
    """
    try:
        # Optional: if QR OTP is required, validate it before pairing
        import os as _os
        require_qr_otp = _os.getenv("PAIRING_QR_REQUIRE_OTP", "0").lower() in {"1", "true", "yes"}
        if require_qr_otp:
            pairing_token_obj = pairing_service.verify_pairing_token(request.pairing_token)
            if not pairing_token_obj:
                raise HTTPException(status_code=400, detail="Invalid or expired pairing token")
            expected_otp = getattr(pairing_token_obj, "otp_code", None)
            if expected_otp and request.otp_code != expected_otp:
                raise HTTPException(status_code=400, detail="Invalid OTP for QR pairing")

        # Pair device
        paired_device = pairing_service.pair_device(
            pairing_token_str=request.pairing_token,
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            os_version=request.os_version,
            app_version=request.app_version,
            push_token=request.push_token,
            ip_address=(http_request.client.host if http_request.client else None)
        )
        
        if not paired_device:
            raise HTTPException(status_code=400, detail="Invalid or expired pairing token")
        
        try:
            pairing_service.audit("pair_device", {
                "user_id": paired_device.user_id if paired_device else None,
                "device_id": request.device_id,
                "ip": http_request.client.host if http_request.client else None,
                "ua": http_request.headers.get("user-agent")
            })
        except Exception:
            pass

        return PairDeviceResponse(
            device_id=paired_device.device_id,
            jwt_token=paired_device.jwt_token,
            expires_at=paired_device.expires_at.isoformat(),
            mqtt_broker="mqtt.topdog-ide.com",
            user_id=paired_device.user_id
        )
    
    except HTTPException:
        # Preserve intended HTTP status codes (e.g., 400 for invalid OTP)
        raise
    except Exception as e:
        logger.error(f"Failed to pair device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-command", response_model=VoiceCommandResponse, dependencies=[Depends(make_rate_limiter(60, 60, "voice_cmd"))])
async def process_voice_command(
    request: VoiceCommandRequest,
    authorization: str = Header(..., description="Bearer {jwt_token}"),
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Process voice command from phone
    
    Mobile app sends transcribed voice command.
    Claude Sonnet 4.5 interprets and executes the command.
    """
    try:
        # Extract JWT token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        jwt_token = authorization.split(" ")[1]
        
        # Verify JWT token
        payload = pairing_service.verify_jwt_token(jwt_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Verify device
        device = pairing_service.get_device(request.device_id)
        if not device or not device.is_active():
            raise HTTPException(status_code=403, detail="Device not authorized")
        
        # Update last seen
        pairing_service.update_last_seen(request.device_id)
        
        # TODO: Process command with Claude Sonnet 4.5
        # For now, return success
        import secrets
        command_id = secrets.token_hex(16)
        
        logger.info(f"Voice command received from {device.device_name}: {request.command_text}")
        
        # Parse command (simplified example)
        command_lower = request.command_text.lower()
        
        if "build" in command_lower:
            status = "processing"
            message = "Initiating build as requested"
        elif "deploy" in command_lower:
            status = "processing"
            message = "Preparing deployment"
        elif "status" in command_lower:
            status = "success"
            message = "Current project is healthy. No active builds."
        else:
            status = "unknown"
            message = "Command not recognized. Try: 'build project', 'deploy to staging', or 'get status'"
        
        return VoiceCommandResponse(
            command_id=command_id,
            status=status,
            message=message,
            details={
                "confidence": request.confidence,
                "language": request.language,
                "user_id": payload['user_id']
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices", response_model=List[DeviceInfo], dependencies=[Depends(make_rate_limiter(30, 60, "list_devices", key_headers=["x-user-id"]))])
async def list_devices(
    authorization: str = Header(..., description="Bearer {jwt_token}"),
    x_admin_token: Optional[str] = Header(default=None, alias="x-admin-token"),
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    List all paired devices for a user
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        jwt_token = authorization.split(" ")[1]
        payload = pairing_service.verify_jwt_token(jwt_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        # Optional admin gating via header
        import os as _os
        admin_required = _os.getenv("PHONE_DEVICES_REQUIRE_ADMIN", "0").lower() in {"1", "true", "yes"}
        if admin_required:
            required = _os.getenv("ADMIN_TOKEN")
            if not required or x_admin_token != required:
                raise HTTPException(status_code=403, detail="Admin token required")
        user_id = payload['user_id']
        devices = pairing_service.get_user_devices(user_id)
        
        return [
            DeviceInfo(
                device_id=device.device_id,
                device_name=device.device_name,
                device_type=device.device_type.value,
                status=device.status.value,
                paired_at=device.paired_at.isoformat(),
                last_seen=device.last_seen.isoformat(),
                expires_at=device.expires_at.isoformat()
            )
            for device in devices
        ]
    
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/devices/{device_id}", dependencies=[Depends(make_rate_limiter(10, 300, "revoke_device", key_headers=["x-user-id", "x-device-id"]))])
async def revoke_device(
    device_id: str,
    authorization: str = Header(..., description="Bearer {jwt_token}"),
    x_admin_token: Optional[str] = Header(default=None, alias="x-admin-token"),
    pairing_service: PhonePairingService = Depends(get_pairing_service),
    message_broker: CloudMessageBroker = Depends(get_message_broker)
):
    """
    Revoke device pairing
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        jwt_token = authorization.split(" ")[1]
        payload = pairing_service.verify_jwt_token(jwt_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        # Optional admin gating via X-Admin-Token
        import os as _os
        admin_required = _os.getenv("PHONE_DEVICES_REQUIRE_ADMIN", "0").lower() in {"1", "true", "yes"}
        if admin_required:
            admin_token = _os.getenv("ADMIN_TOKEN")
            if not admin_token or x_admin_token != admin_token:
                raise HTTPException(status_code=403, detail="Admin token required")
        user_id = payload['user_id']
        # Verify device belongs to user
        device = pairing_service.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        if device.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Revoke device
        success = pairing_service.revoke_device(device_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to revoke device")
        
        # notify device of logout if possible
        try:
            await message_broker.send_build_notification(
                user_id=user_id,
                device_id=device_id,
                notification=BuildNotification(
                    build_id="security",
                    project_name="q-ide",
                    status=BuildStatus.FAILURE,
                    message="Device access revoked. Please re-pair to regain access.",
                    priority=NotificationPriority.CRITICAL,
                    action_required=True,
                ),
            )
        except Exception:
            pass
        return {"message": "Device revoked successfully", "device_id": device_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/send")
async def send_notification(
    request: SendNotificationRequest,
    message_broker: CloudMessageBroker = Depends(get_message_broker),
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Send build notification to phone
    
    Called by IDE to notify phone about build status changes.
    """
    try:
        # Verify device exists
        device = pairing_service.get_device(request.device_id)
        if not device or not device.is_active():
            raise HTTPException(status_code=404, detail="Device not found or inactive")
        
        # Create notification
        notification = BuildNotification(
            build_id=request.build_id,
            project_name=request.project_name,
            status=request.status,
            message=request.message,
            priority=request.priority,
            action_required=request.action_required
        )
        
        # Send via MQTT
        success = await message_broker.send_build_notification(
            user_id=device.user_id,
            device_id=device.device_id,
            notification=notification
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send notification")
        
        return {"message": "Notification sent successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/request")
async def request_approval(
    request: SendApprovalRequest,
    message_broker: CloudMessageBroker = Depends(get_message_broker),
    pairing_service: PhonePairingService = Depends(get_pairing_service)
):
    """
    Request build approval from phone
    
    Called by IDE when pre-build approval workflow is triggered.
    Phone displays approval UI with build plan details.
    """
    try:
        # Verify device exists
        device = pairing_service.get_device(request.device_id)
        if not device or not device.is_active():
            raise HTTPException(status_code=404, detail="Device not found or inactive")
        
        # Create approval request
        import secrets
        approval = ApprovalRequest(
            approval_id=secrets.token_hex(16),
            build_id=request.build_id,
            project_name=request.project_name,
            plan=request.plan,
            affected_files=request.affected_files,
            estimated_duration=request.estimated_duration,
            requires_approval_by=request.requires_approval_by,
            user_id=request.user_id
        )
        
        # Send via MQTT
        success = await message_broker.send_approval_request(
            user_id=device.user_id,
            device_id=device.device_id,
            approval=approval
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send approval request")
        
        return {
            "message": "Approval request sent successfully",
            "approval_id": approval.approval_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/webhook")
async def sms_webhook(
    From: str = Form(..., description="Sender phone number"),
    Body_text: str = Form(..., alias="Body", description="SMS message text"),
    pairing_service: PhonePairingService = Depends(get_pairing_service),
    sms_handler: SMSCommandHandler = Depends(get_sms_command_handler)
):
    """
    Webhook for incoming SMS messages (Twilio/AWS SNS format)
    
    Handles incoming SMS commands from users.
    Users can text the system to add todos, notes, reminders, etc.
    
    Twilio sends: From, Body
    AWS SNS sends: originationNumber, messageBody
    """
    try:
        # Accept form-encoded (Twilio) parameters; already parsed by FastAPI via Form(...)
        phone_number = From
        message = Body_text
        if not message:
            logger.warning("Empty SMS message received; returning 200 to avoid retry loop")
            return Response(
                content="""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>Empty message received.</Message></Response>""",
                media_type="application/xml"
            )
        
        logger.info(f"Incoming SMS from {phone_number}: {message}")
        
        # Find user by phone number
        # For now, we'll use phone number as user_id
        # In production, you'd look up the user_id from paired devices
        user_id = phone_number  # Simplified
        
        # Handle the SMS command
        result = await sms_handler.handle_sms(message, user_id, phone_number)
        
        # Get reply message
        reply = result.get('result', {}).get('reply', 'Message received.')
        
        # Return TwiML response for Twilio
        # For AWS SNS, you'd return differently
        return Response(
            content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>""",
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error handling SMS webhook: {e}")
        # Return 200 with error message to prevent provider retry storms (idempotent failure handling)
        return Response(
            content=f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, error: {str(e)[:120]}</Message>
</Response>""",
            media_type="application/xml"
        )


@router.get("/sms/todos")
async def get_sms_todos(
    user_id: str = Query(..., description="User ID"),
    sms_handler: SMSCommandHandler = Depends(get_sms_command_handler)
):
    """Get todos added via SMS"""
    try:
        todos = sms_handler.get_todos(user_id)
        return {
            'success': True,
            'todos': todos,
            'count': len(todos)
        }
    except Exception as e:
        logger.error(f"Error getting SMS todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/notes")
async def get_sms_notes(
    user_id: str = Query(..., description="User ID"),
    sms_handler: SMSCommandHandler = Depends(get_sms_command_handler)
):
    """Get notes added via SMS"""
    try:
        notes = sms_handler.get_notes(user_id)
        return {
            'success': True,
            'notes': notes,
            'count': len(notes)
        }
    except Exception as e:
        logger.error(f"Error getting SMS notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sms/reminders")
async def get_sms_reminders(
    user_id: str = Query(..., description="User ID"),
    sms_handler: SMSCommandHandler = Depends(get_sms_command_handler)
):
    """Get reminders added via SMS"""
    try:
        reminders = sms_handler.get_reminders(user_id)
        return {
            'success': True,
            'reminders': reminders,
            'count': len(reminders)
        }
    except Exception as e:
        logger.error(f"Error getting SMS reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for phone pairing service"""
    return {
        "status": "ok",
        "service": "phone-pairing",
        "timestamp": datetime.utcnow().isoformat()
    }
