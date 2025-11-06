"""
Push Notifications API

Register and manage push notification subscribers. This enables optional push
alerts in addition to SMS-first and email fallbacks.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.services.push_store import add_subscriber, remove_subscriber, list_subscribers
from backend.services.push_service import get_push_service

router = APIRouter(prefix="/push", tags=["push"])


class RegisterPayload(BaseModel):
    user_id: Optional[str] = Field(default=None)
    token: Optional[str] = Field(default=None)
    platform: str = Field(default="web")  # web|ios|android|webpush|other
    meta: Optional[Dict[str, Any]] = Field(default=None)
    subscription: Optional[Dict[str, Any]] = Field(default=None, description="Web Push subscription JSON (endpoint, keys)")


@router.post("/register")
def register_push(req: RegisterPayload):
    add_subscriber(req.user_id or "__global__", req.token, req.platform, req.meta, req.subscription)
    return {"status": "ok"}


@router.post("/unregister")
def unregister_push(user_id: Optional[str], token: str):
    remove_subscriber(user_id or "__global__", token)
    return {"status": "ok"}


@router.get("/subscribers")
def get_subscribers(user_id: Optional[str] = None):
    return {"status": "ok", "subscribers": list_subscribers(user_id or "__global__")}


class NotifyPayload(BaseModel):
    user_id: Optional[str] = None
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None


@router.post("/notify")
def notify(req: NotifyPayload):
    sent = get_push_service().send(req.user_id, req.title, req.body, req.data)
    return {"status": "ok", "sent": sent}


@router.get("/vapid-public")
def vapid_public_key():
    # Expose VAPID public key for web clients to subscribe securely
    import os
    pub = os.getenv("VAPID_PUBLIC_KEY", "")
    return {"status": "ok", "publicKey": pub}


@router.get("/help")
def push_help():
    """Return helpful links and current config status for push setup."""
    import os
    return {
        "status": "ok",
        "webpush": {
            "configured": bool(os.getenv("VAPID_PUBLIC_KEY") and os.getenv("VAPID_PRIVATE_KEY")),
            "subject": os.getenv("VAPID_SUBJECT", "")
        },
        "providers": {
            "firebase_console": "https://console.firebase.google.com/",
            "firebase_cloud_messaging_keys": "https://console.firebase.google.com/project/_/settings/cloudmessaging",
            "onesignal_signup": "https://app.onesignal.com/signup",
            "onesignal_dashboard": "https://app.onesignal.com/",
            "pusher_beams_signup": "https://dash.pusher.com/accounts/sign_up",
            "pusher_dashboard": "https://dashboard.pusher.com/",
            "aws_sns_console": "https://console.aws.amazon.com/sns/v3/home",
            "azure_portal": "https://portal.azure.com/",
            "azure_notification_hubs": "https://azure.microsoft.com/products/notification-hubs/",
            "apple_developer": "https://developer.apple.com/account/",
            "apns_certificates": "https://developer.apple.com/account/resources/certificates/list"
        }
    }
