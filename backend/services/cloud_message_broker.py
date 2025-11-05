"""
Cloud Message Broker Service for Long-Distance Phone Communication

Provides MQTT-based messaging for phone pairing and remote control across
cellular/WiFi networks. Supports voice commands, notifications, and build control.

Technologies:
- MQTT (Eclipse Mosquitto) for pub/sub messaging
- TLS/SSL for encrypted communication
- JWT tokens for authentication
- WebSockets fallback for restricted networks

Architecture:
- IDE acts as publisher/subscriber
- Mobile app acts as subscriber/publisher
- Cloud broker (e.g., HiveMQ Cloud, AWS IoT Core) handles routing
"""

import asyncio
import json
import logging
import ssl
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import secrets

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logging.warning("paho-mqtt not installed. Phone pairing will be limited.")

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of messages exchanged between IDE and phone"""
    # Phone → IDE
    VOICE_COMMAND = "voice_command"
    PAIRING_REQUEST = "pairing_request"
    HEARTBEAT = "heartbeat"
    ACKNOWLEDGMENT = "acknowledgment"
    
    # IDE → Phone
    BUILD_STATUS = "build_status"
    NOTIFICATION = "notification"
    APPROVAL_REQUEST = "approval_request"
    PAIRING_RESPONSE = "pairing_response"
    COMMAND_RESULT = "command_result"


class BuildStatus(str, Enum):
    """Build status states"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    APPROVAL_PENDING = "approval_pending"
    CANCELLED = "cancelled"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Message:
    """Base message structure"""
    type: MessageType
    payload: Dict[str, Any]
    timestamp: str
    message_id: str
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> 'Message':
        """Deserialize from JSON"""
        obj = json.loads(data)
        return cls(**obj)


@dataclass
class VoiceCommand:
    """Voice command from phone"""
    command_text: str
    user_id: str
    device_id: str
    audio_url: Optional[str] = None  # Optional audio file URL
    confidence: float = 1.0  # STT confidence score
    language: str = "en-US"


@dataclass
class BuildNotification:
    """Build status notification to phone"""
    build_id: str
    project_name: str
    status: BuildStatus
    message: str
    priority: NotificationPriority
    details: Optional[Dict[str, Any]] = None
    action_required: bool = False


@dataclass
class ApprovalRequest:
    """Request approval from phone"""
    approval_id: str
    build_id: str
    project_name: str
    plan: str  # Detailed build plan
    affected_files: List[str]
    estimated_duration: str
    requires_approval_by: str  # Timestamp
    user_id: str


class CloudMessageBroker:
    """
    Manages long-distance communication between IDE and mobile phones
    using cloud-based MQTT broker
    """
    
    def __init__(
        self,
        broker_url: str = "mqtt.topdog-ide.com",
        broker_port: int = 8883,  # TLS port
        use_tls: bool = True,
        ca_cert_path: Optional[str] = None,
        client_id: Optional[str] = None
    ):
        """
        Initialize cloud message broker
        
        Args:
            broker_url: MQTT broker hostname (e.g., HiveMQ Cloud, AWS IoT Core)
            broker_port: Broker port (8883 for TLS, 1883 for non-TLS)
            use_tls: Enable TLS/SSL encryption
            ca_cert_path: Path to CA certificate for TLS
            client_id: Unique client identifier (generated if None)
        """
        if not MQTT_AVAILABLE:
            raise RuntimeError("paho-mqtt package required. Install: pip install paho-mqtt")
        
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.use_tls = use_tls
        self.ca_cert_path = ca_cert_path
        self.client_id = client_id or f"topdog-ide-{secrets.token_hex(8)}"
        
        # MQTT client
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        
        # Topic structure: topdog/{user_id}/{device_id}/{message_type}
        self.base_topic = "topdog"
        
        # Message handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        
        # Connection state
        self.reconnect_delay = 5  # seconds
        self.max_reconnect_delay = 300  # 5 minutes
        
        logger.info(f"CloudMessageBroker initialized: {broker_url}:{broker_port}")
    
    async def connect(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Connect to MQTT broker with optional authentication
        
        Args:
            username: Broker username
            password: Broker password
        """
        try:
            # Create MQTT client
            self.client = mqtt.Client(
                client_id=self.client_id,
                protocol=mqtt.MQTTv5,
                transport="tcp"
            )
            
            # Set credentials
            if username and password:
                self.client.username_pw_set(username, password)
            
            # Configure TLS
            if self.use_tls:
                tls_context = ssl.create_default_context()
                if self.ca_cert_path:
                    tls_context.load_verify_locations(self.ca_cert_path)
                self.client.tls_set_context(tls_context)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Connect
            logger.info(f"Connecting to MQTT broker: {self.broker_url}:{self.broker_port}")
            self.client.connect_async(self.broker_url, self.broker_port, keepalive=60)
            
            # Start network loop
            self.client.loop_start()
            
            # Wait for connection
            for _ in range(10):  # 10 seconds timeout
                if self.connected:
                    logger.info("Successfully connected to MQTT broker")
                    return
                await asyncio.sleep(1)
            
            raise ConnectionError("Failed to connect to MQTT broker within timeout")
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            
            # Subscribe to IDE topics
            # Listen to all voice commands: topdog/+/+/voice_command
            self.client.subscribe(f"{self.base_topic}/+/+/voice_command", qos=1)
            # Listen to pairing requests
            self.client.subscribe(f"{self.base_topic}/+/+/pairing_request", qos=1)
            # Listen to heartbeats
            self.client.subscribe(f"{self.base_topic}/+/+/heartbeat", qos=0)
            # Listen to acknowledgments
            self.client.subscribe(f"{self.base_topic}/+/+/acknowledgment", qos=1)
            
            logger.info("Subscribed to phone communication topics")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {rc}")
        
        # Attempt reconnection
        if rc != 0:
            logger.info("Attempting to reconnect...")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            # Parse topic: topdog/{user_id}/{device_id}/{message_type}
            topic_parts = msg.topic.split('/')
            if len(topic_parts) != 4:
                logger.warning(f"Invalid topic format: {msg.topic}")
                return
            
            _, user_id, device_id, message_type_str = topic_parts
            
            # Parse message
            message = Message.from_json(msg.payload.decode('utf-8'))
            message.user_id = user_id
            message.device_id = device_id
            
            # Validate message type
            try:
                message_type = MessageType(message_type_str)
            except ValueError:
                logger.warning(f"Unknown message type: {message_type_str}")
                return
            
            logger.info(f"Received {message_type} from {user_id}/{device_id}")
            
            # Call registered handlers
            handlers = self.message_handlers.get(message_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(message))
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def subscribe(self, message_type: MessageType, handler: Callable):
        """
        Register handler for specific message type
        
        Args:
            message_type: Type of message to handle
            handler: Callback function (can be async)
        """
        self.message_handlers[message_type].append(handler)
        logger.info(f"Registered handler for {message_type}")
    
    async def publish(
        self,
        user_id: str,
        device_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        qos: int = 1
    ) -> bool:
        """
        Publish message to phone
        
        Args:
            user_id: Target user ID
            device_id: Target device ID
            message_type: Type of message
            payload: Message payload
            qos: Quality of Service (0, 1, or 2)
        
        Returns:
            True if published successfully
        """
        if not self.connected or not self.client:
            logger.error("Not connected to MQTT broker")
            return False
        
        try:
            # Create message
            message = Message(
                type=message_type,
                payload=payload,
                timestamp=datetime.utcnow().isoformat(),
                message_id=secrets.token_hex(16),
                user_id=user_id,
                device_id=device_id
            )
            
            # Publish to topic: topdog/{user_id}/{device_id}/{message_type}
            topic = f"{self.base_topic}/{user_id}/{device_id}/{message_type.value}"
            
            result = self.client.publish(
                topic,
                message.to_json(),
                qos=qos,
                retain=False
            )
            
            # Wait for publish to complete
            result.wait_for_publish(timeout=5)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published {message_type} to {user_id}/{device_id}")
                return True
            else:
                logger.error(f"Failed to publish message: {result.rc}")
                return False
        
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False
    
    async def send_build_notification(
        self,
        user_id: str,
        device_id: str,
        notification: BuildNotification
    ) -> bool:
        """Send build status notification to phone"""
        return await self.publish(
            user_id,
            device_id,
            MessageType.NOTIFICATION,
            asdict(notification),
            qos=1 if notification.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else 0
        )
    
    async def send_approval_request(
        self,
        user_id: str,
        device_id: str,
        approval: ApprovalRequest
    ) -> bool:
        """Send approval request to phone"""
        return await self.publish(
            user_id,
            device_id,
            MessageType.APPROVAL_REQUEST,
            asdict(approval),
            qos=2  # Exactly once delivery for approvals
        )
    
    async def send_command_result(
        self,
        user_id: str,
        device_id: str,
        command_id: str,
        success: bool,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send command execution result to phone"""
        payload = {
            "command_id": command_id,
            "success": success,
            "result": result,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.publish(
            user_id,
            device_id,
            MessageType.COMMAND_RESULT,
            payload,
            qos=1
        )
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.client and self.connected:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except:
                pass


# Singleton instance
_broker: Optional[CloudMessageBroker] = None


def get_message_broker() -> CloudMessageBroker:
    """Get singleton message broker instance"""
    global _broker
    if _broker is None:
        # TODO: Load from config
        _broker = CloudMessageBroker(
            broker_url="mqtt.topdog-ide.com",  # Replace with actual broker
            broker_port=8883,
            use_tls=True
        )
    return _broker


async def initialize_message_broker(
    broker_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> CloudMessageBroker:
    """
    Initialize and connect message broker
    
    Args:
        broker_url: MQTT broker URL
        username: Broker username
        password: Broker password
    
    Returns:
        Connected message broker instance
    """
    broker = get_message_broker()
    await broker.connect(username, password)
    return broker
