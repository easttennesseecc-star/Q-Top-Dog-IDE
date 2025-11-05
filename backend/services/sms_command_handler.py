"""
SMS Command Handler

Handles incoming SMS messages from users to control IDE remotely.
Users can send text messages to add tasks, notes, reminders, or commands.
"""

import logging
import re
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SMSCommandType(Enum):
    """Types of SMS commands"""
    TODO = "todo"
    NOTE = "note"
    REMINDER = "reminder"
    BUILD = "build"
    DEPLOY = "deploy"
    STATUS = "status"
    HELP = "help"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


@dataclass
class SMSCommand:
    """Parsed SMS command"""
    command_type: SMSCommandType
    content: str
    user_id: str
    phone_number: str
    timestamp: datetime
    metadata: Dict[str, Any]
    raw_message: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'command_type': self.command_type.value,
            'content': self.content,
            'user_id': self.user_id,
            'phone_number': self.phone_number,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'raw_message': self.raw_message
        }


class SMSCommandHandler:
    """
    Handles incoming SMS commands from users
    
    Supported SMS formats:
    - "TODO: Fix bug in login page" -> Adds todo item
    - "NOTE: Remember to update docs" -> Saves note
    - "REMIND: Review PR in 2 hours" -> Sets reminder
    - "BUILD ProjectAlpha" -> Triggers build
    - "DEPLOY staging" -> Deploys to environment
    - "STATUS" -> Gets current build/project status
    - "HELP" -> Shows available commands
    """
    
    # Command patterns
    COMMAND_PATTERNS = {
        SMSCommandType.TODO: [
            r'^todo:?\s*(.+)',
            r'^add task:?\s*(.+)',
            r'^task:?\s*(.+)'
        ],
        SMSCommandType.NOTE: [
            r'^note:?\s*(.+)',
            r'^remember:?\s*(.+)',
            r'^save:?\s*(.+)'
        ],
        SMSCommandType.REMINDER: [
            r'^remind(?:er)?:?\s*(.+)',
            r'^remind me:?\s*(.+)',
            r'^alert:?\s*(.+)'
        ],
        SMSCommandType.BUILD: [
            r'^build\s+(.+)',
            r'^run build\s+(.+)',
            r'^start build\s+(.+)'
        ],
        SMSCommandType.DEPLOY: [
            r'^deploy\s+(.+)',
            r'^deploy to\s+(.+)',
            r'^push to\s+(.+)'
        ],
        SMSCommandType.STATUS: [
            r'^status$',
            r'^what\'s the status\??$',
            r'^show status$'
        ],
        SMSCommandType.HELP: [
            r'^help$',
            r'^commands?$',
            r'^\?$'
        ],
        SMSCommandType.CANCEL: [
            r'^cancel$',
            r'^stop$',
            r'^abort$'
        ]
    }
    
    def __init__(self):
        """Initialize SMS command handler"""
        self.handlers = {
            SMSCommandType.TODO: self._handle_todo,
            SMSCommandType.NOTE: self._handle_note,
            SMSCommandType.REMINDER: self._handle_reminder,
            SMSCommandType.BUILD: self._handle_build,
            SMSCommandType.DEPLOY: self._handle_deploy,
            SMSCommandType.STATUS: self._handle_status,
            SMSCommandType.HELP: self._handle_help,
            SMSCommandType.CANCEL: self._handle_cancel,
        }
        
        # Storage for todos, notes, reminders
        self.todos = []
        self.notes = []
        self.reminders = []
        
    def parse_sms(self, message: str, user_id: str, phone_number: str) -> SMSCommand:
        """
        Parse incoming SMS message into command
        
        Args:
            message: Raw SMS message text
            user_id: User ID who sent the message
            phone_number: Phone number that sent the message
            
        Returns:
            Parsed SMSCommand
        """
        message = message.strip()
        message_lower = message.lower()
        
        # Try to match against known patterns
        for command_type, patterns in self.COMMAND_PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, message_lower, re.IGNORECASE)
                if match:
                    # Extract content (if pattern has capture group)
                    content = match.group(1).strip() if match.groups() else message
                    
                    return SMSCommand(
                        command_type=command_type,
                        content=content,
                        user_id=user_id,
                        phone_number=phone_number,
                        timestamp=datetime.utcnow(),
                        metadata={},
                        raw_message=message
                    )
        
        # No pattern matched - treat as unknown command
        return SMSCommand(
            command_type=SMSCommandType.UNKNOWN,
            content=message,
            user_id=user_id,
            phone_number=phone_number,
            timestamp=datetime.utcnow(),
            metadata={},
            raw_message=message
        )
    
    async def handle_sms(self, message: str, user_id: str, phone_number: str) -> Dict[str, Any]:
        """
        Handle incoming SMS message
        
        Args:
            message: Raw SMS message text
            user_id: User ID who sent the message
            phone_number: Phone number that sent the message
            
        Returns:
            Response dictionary with status and reply message
        """
        try:
            # Parse command
            command = self.parse_sms(message, user_id, phone_number)
            
            logger.info(f"SMS command from {phone_number}: {command.command_type.value} - {command.content}")
            
            # Get handler for command type
            handler = self.handlers.get(command.command_type)
            
            if handler:
                result = await handler(command)
            else:
                result = await self._handle_unknown(command)
            
            return {
                'success': True,
                'command': command.to_dict(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error handling SMS command: {e}")
            return {
                'success': False,
                'error': str(e),
                'reply': f"Sorry, I couldn't process your message. Error: {str(e)}"
            }
    
    async def _handle_todo(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle TODO command"""
        # Add to todos list
        todo = {
            'id': len(self.todos) + 1,
            'content': command.content,
            'user_id': command.user_id,
            'phone_number': command.phone_number,
            'created_at': command.timestamp.isoformat(),
            'completed': False
        }
        self.todos.append(todo)
        
        logger.info(f"Added todo #{todo['id']}: {command.content}")
        
        return {
            'action': 'todo_added',
            'todo': todo,
            'reply': f"✓ Added to your todo list:\n\n\"{command.content}\"\n\nYou now have {len([t for t in self.todos if not t['completed']])} open tasks."
        }
    
    async def _handle_note(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle NOTE command"""
        # Save note
        note = {
            'id': len(self.notes) + 1,
            'content': command.content,
            'user_id': command.user_id,
            'phone_number': command.phone_number,
            'created_at': command.timestamp.isoformat()
        }
        self.notes.append(note)
        
        logger.info(f"Saved note #{note['id']}: {command.content}")
        
        return {
            'action': 'note_saved',
            'note': note,
            'reply': f"📝 Note saved:\n\n\"{command.content}\"\n\nYou can access it in the IDE notes section."
        }
    
    async def _handle_reminder(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle REMINDER command"""
        # Parse time from content (simplified - could use NLP)
        reminder = {
            'id': len(self.reminders) + 1,
            'content': command.content,
            'user_id': command.user_id,
            'phone_number': command.phone_number,
            'created_at': command.timestamp.isoformat(),
            'triggered': False
        }
        self.reminders.append(reminder)
        
        logger.info(f"Set reminder #{reminder['id']}: {command.content}")
        
        return {
            'action': 'reminder_set',
            'reminder': reminder,
            'reply': f"⏰ Reminder set:\n\n\"{command.content}\"\n\nI'll notify you when it's time."
        }
    
    async def _handle_build(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle BUILD command"""
        project_name = command.content
        
        logger.info(f"Build requested for: {project_name}")
        
        # TODO: Integrate with actual build system
        return {
            'action': 'build_initiated',
            'project': project_name,
            'reply': f"🚀 Starting build for \"{project_name}\"...\n\nI'll notify you when it completes."
        }
    
    async def _handle_deploy(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle DEPLOY command"""
        environment = command.content
        
        logger.info(f"Deploy requested to: {environment}")
        
        # TODO: Integrate with deployment system
        return {
            'action': 'deploy_initiated',
            'environment': environment,
            'reply': f"🚀 Deploying to \"{environment}\"...\n\nThis may require approval. Check your notifications."
        }
    
    async def _handle_status(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle STATUS command"""
        # Get current status
        open_todos = len([t for t in self.todos if not t['completed']])
        notes_count = len(self.notes)
        reminders_count = len([r for r in self.reminders if not r['triggered']])
        
        status_message = f"""📊 Status Report:

Tasks: {open_todos} open
Notes: {notes_count} saved
Reminders: {reminders_count} active

All systems operational ✓"""
        
        return {
            'action': 'status_retrieved',
            'stats': {
                'open_todos': open_todos,
                'notes': notes_count,
                'reminders': reminders_count
            },
            'reply': status_message
        }
    
    async def _handle_help(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle HELP command"""
        help_message = """📱 SMS Commands:

TODO: <task>
Add task to your list

NOTE: <text>
Save a note

REMIND: <what>
Set a reminder

BUILD <project>
Start a build

DEPLOY <env>
Deploy to environment

STATUS
Get current status

Reply with any command!"""
        
        return {
            'action': 'help_shown',
            'reply': help_message
        }
    
    async def _handle_cancel(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle CANCEL command"""
        # TODO: Cancel current operation
        return {
            'action': 'cancelled',
            'reply': "✓ Cancelled current operation."
        }
    
    async def _handle_unknown(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle unknown command"""
        # Save as a note by default
        note = {
            'id': len(self.notes) + 1,
            'content': command.content,
            'user_id': command.user_id,
            'phone_number': command.phone_number,
            'created_at': command.timestamp.isoformat(),
            'type': 'freeform'
        }
        self.notes.append(note)
        
        return {
            'action': 'saved_as_note',
            'note': note,
            'reply': f"💬 Saved your message as a note:\n\n\"{command.content}\"\n\nReply HELP for command list."
        }
    
    def get_todos(self, user_id: str) -> List[dict]:
        """Get todos for user"""
        return [t for t in self.todos if t['user_id'] == user_id]
    
    def get_notes(self, user_id: str) -> List[dict]:
        """Get notes for user"""
        return [n for n in self.notes if n['user_id'] == user_id]
    
    def get_reminders(self, user_id: str) -> List[dict]:
        """Get reminders for user"""
        return [r for r in self.reminders if r['user_id'] == user_id]


# Singleton instance
_sms_handler = None

def get_sms_command_handler() -> SMSCommandHandler:
    """Get singleton SMS command handler instance"""
    global _sms_handler
    if _sms_handler is None:
        _sms_handler = SMSCommandHandler()
    return _sms_handler
