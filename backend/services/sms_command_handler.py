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
    UIDRAFT = "uidraft"
    PLAN = "plan"
    APPROVE = "approve"
    MODIFY = "modify"
    PAIR = "pair"
    UNPAIR = "unpair"
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
        ],
        SMSCommandType.UIDRAFT: [
            r'^(?:ui\s*draft|draft\s*ui|wireframe):?\s*(.+)'
        ],
        SMSCommandType.PLAN: [
            r'^plan:?\s*(.+)'
        ],
        SMSCommandType.APPROVE: [
            r'^(?:approve(?:\s*plan)?)\s+([\w\-]+)'
        ],
        SMSCommandType.MODIFY: [
            r'^(?:modify|change|revise):?\s*(.*)'
        ],
        SMSCommandType.PAIR: [
            r'^(?:away\s+on|pair)(?::?\s*(\+?[\d\-\s\(\)]+))?\s*$'
        ],
        SMSCommandType.UNPAIR: [
            r'^(?:away\s+off|unpair)$'
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
            SMSCommandType.UIDRAFT: self._handle_uidraft,
            SMSCommandType.PLAN: self._handle_plan,
            SMSCommandType.APPROVE: self._handle_approve,
            SMSCommandType.MODIFY: self._handle_modify,
            SMSCommandType.PAIR: self._handle_pair,
            SMSCommandType.UNPAIR: self._handle_unpair,
        }
        
        # Storage for notes, reminders (todos are persisted via tasks_service)
        self.todos = []  # kept for backward-compat; not authoritative
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
            # Log inbound SMS into session log
            try:
                from backend.services.sms_session_log import log_inbound
                log_inbound(phone_number, user_id, command.raw_message, {"cmd": command.command_type.value})
            except Exception:
                pass
            
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
        # Persist via tasks service
        try:
            from backend.services.tasks_service import get_tasks_service
            svc = get_tasks_service()
            task = svc.add_task(command.user_id, command.content, metadata={
                "source": "sms",
                "phone_number": command.phone_number,
                "raw": command.raw_message,
            })
            logger.info(f"Added task {task.id} from SMS: {command.content}")
            open_count = len([t for t in svc.list_tasks(command.user_id, include_completed=False)])
            return {
                'action': 'todo_added',
                'todo': task.to_dict(),
                'reply': f"✓ Added to your todo list:\n\n\"{command.content}\"\n\nYou now have {open_count} open tasks."
            }
        except Exception as e:
            logger.warning(f"Falling back to in-memory todos: {e}")
            # Add to in-memory list (fallback)
            todo = {
                'id': len(self.todos) + 1,
                'content': command.content,
                'user_id': command.user_id,
                'phone_number': command.phone_number,
                'created_at': command.timestamp.isoformat(),
                'completed': False
            }
            self.todos.append(todo)
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
        project_name = command.content or "default"
        logger.info(f"Build requested via SMS for: {project_name}")
        try:
            import uuid, threading
            # Reuse backend.main build runner to ensure same behavior as API
            from backend import main as app_main
            build_id = str(uuid.uuid4())
            # Initialize store entry similar to /build/run
            app_main.BUILD_STORE[build_id] = {"id": build_id, "status": "queued", "log": ""}
            t = threading.Thread(target=app_main.run_local_build, args=(build_id,), daemon=True)
            t.start()
            return {
                'action': 'build_initiated',
                'project': project_name,
                'build_id': build_id,
                'reply': f"🚀 Build started (ID {build_id[:8]}). Reply STATUS anytime or open IDE to view logs."
            }
        except Exception as e:
            logger.error(f"Failed to start build via SMS: {e}")
            return {
                'action': 'build_failed',
                'project': project_name,
                'reply': "Couldn't start build right now. Please try again or use the IDE.",
                'error': str(e),
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

    async def _handle_uidraft(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle UI DRAFT command -> generate low-cost UI visual via media service"""
        try:
            from backend.media_service import get_media_service, MediaType
            from backend.services.media_requirements_resolver import resolve_requirements
            from backend.services.email_service import get_email_service
            from pathlib import Path
            # Helper: find a default email for this user if available
            def _get_default_email_for_user(uid: str) -> Optional[str]:
                try:
                    from backend.auth import get_user
                    u = get_user(uid)
                    if isinstance(u, dict):
                        mail = u.get('email') or u.get('provider_email')
                        if mail:
                            return str(mail)
                except Exception:
                    pass
                import os
                return os.getenv("EMAIL_APPROVAL_TO")
            desc = command.content or "simple app layout"
            resolved = resolve_requirements(project_id=command.user_id, description=desc, media_type="image")
            svc = get_media_service()
            result = await svc.generate(
                description=desc,
                media_type=MediaType.IMAGE,
                resolution=resolved.get('resolution'),
                format=resolved.get('format'),
            )
            # Keep SMS reply concise; advise user to check IDE for image
            tier = result.tier.value
            res = resolved.get('resolution')
            fmt = resolved.get('format')
            reply = (
                f"UI draft created ({tier}). Res={res} fmt={fmt}. "
                f"Open IDE to view the draft. Configure providers for higher fidelity."
            )
            # Prepare approval + modify links and optionally send MMS with snapshot
            import os, base64, uuid
            from backend.services.email_token_service import register_token
            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
            approve_token = register_token({
                "kind": "ui_draft_approval",
                "project_id": command.user_id,
                "description": desc,
            })
            approve_link = f"{backend_url.rstrip('/')}/api/assistant/approve-email?token={approve_token}"
            modify_token = register_token({
                "kind": "ui_draft_modify",
                "project_id": command.user_id,
                "description": desc,
            }, expires_seconds=24*3600)
            modify_link = f"{backend_url.rstrip('/')}/api/assistant/modify-email?token={modify_token}"
            # Build MMS media URL if possible
            media_url: Optional[str] = None
            artifact_bytes: Optional[bytes] = None
            artifact_ctype: str = "image/png"
            artifact_name: str = f"ui-draft-{uuid.uuid4().hex}.png"
            try:
                if isinstance(result.url, str) and result.url.startswith("data:"):
                    header, b64 = result.url.split(",", 1)
                    if ";base64" in header:
                        try:
                            if "image/" in header:
                                artifact_ctype = header.split(":",1)[1].split(";",1)[0]
                                # Try to infer extension
                                ext = artifact_ctype.split("/")[-1]
                                if ext:
                                    artifact_name = f"ui-draft-{uuid.uuid4().hex}.{ext}"
                        except Exception:
                            pass
                        artifact_bytes = base64.b64decode(b64)
                elif isinstance(result.url, str) and result.url.startswith("http"):
                    # Remote URL that Twilio can fetch directly
                    media_url = result.url
            except Exception:
                pass
            # If we have bytes, persist to artifacts and construct URL
            if artifact_bytes:
                try:
                    artifacts_dir = Path(__file__).resolve().parent.parent.parent / "artifacts"
                    artifacts_dir.mkdir(exist_ok=True)
                    fpath = artifacts_dir / artifact_name
                    fpath.write_bytes(artifact_bytes)
                    media_url = f"{backend_url.rstrip('/')}/artifacts/{artifact_name}"
                except Exception:
                    media_url = None
            # Send MMS with approve/modify links appended
            try:
                from backend.services.sms_sender import get_sms_sender
                sms = get_sms_sender()
                body_lines = [
                    "UI draft ready.",
                    f"Approve: {approve_link}",
                    f"Modify: {modify_link}",
                ]
                body = "\n".join(body_lines)
                if media_url:
                    sms.send_mms(command.phone_number, media_url, body)
                else:
                    sms.send_sms_text(command.phone_number, body)
            except Exception:
                pass
            # Optional: email to default approval recipient
            email_to = _get_default_email_for_user(command.user_id)
            try:
                if email_to:
                    img_bytes = None
                    filename = "ui-draft.png"
                    ctype = "image/png"
                    if isinstance(result.url, str) and result.url.startswith("data:"):
                        try:
                            header, b64 = result.url.split(",", 1)
                            if ";base64" in header:
                                if "image/" in header:
                                    ctype = header.split(":",1)[1].split(";",1)[0]
                                img_bytes = base64.b64decode(b64)
                        except Exception:
                            img_bytes = None
                    elif isinstance(result.url, str) and result.url.startswith("http"):
                        import urllib.request
                        try:
                            with urllib.request.urlopen(result.url, timeout=10) as resp:
                                img_bytes = resp.read()
                                ctype = resp.headers.get_content_type() or ctype
                        except Exception:
                            img_bytes = None
                    subject = "UI Draft for Approval — SMS"
                    text = (
                        f"Desc: {desc}\nTier: {tier}\nRes: {res}\nFmt: {fmt}\nURL: {result.url}\n\n"
                        f"Quick reply by email (no links needed):\n"
                        f"ACCEPT {approve_token}\n"
                        f"DECLINE {approve_token}\n"
                        f"MODIFY {modify_token}: <your notes>\n"
                    )
                    html = (
                        f"<p>UI draft created from SMS.</p>"
                        f"<p><b>Desc:</b> {desc}</p>"
                        f"<p><a href='{result.url}'>Open Draft</a></p>"
                        f"<p>Actions:</p>"
                        f"<p><a href='{approve_link}' style='background:#10b981;color:#fff;padding:8px 12px;text-decoration:none;border-radius:6px;margin-right:8px'>Approve and Build</a>"
                        f"<a href='{modify_link}' style='background:#374151;color:#fff;padding:8px 12px;text-decoration:none;border-radius:6px'>Request Changes</a></p>"
                        f"<hr><p><b>Prefer replying by email?</b> You can simply reply with:</p>"
                        f"<pre style='background:#f3f4f6;padding:8px;border-radius:6px'>ACCEPT {approve_token}\nDECLINE {approve_token}\nMODIFY {modify_token}: change request here</pre>"
                    )
                    atts = [(filename, img_bytes, ctype)] if img_bytes else []
                    get_email_service().send(subject, [email_to], html=html, text=text, attachments=atts)
            except Exception as ee:
                logger.warning(f"SMS email send skipped/failed: {ee}")

            # Optional: send push notification as an additional channel (non-blocking)
            try:
                from backend.services.push_service import get_push_service
                get_push_service().send(command.user_id, "UI draft ready", "Approve or request changes.", {
                    "approve_link": approve_link,
                    "modify_link": modify_link,
                    "url": result.url,
                })
            except Exception:
                pass
            return {
                'action': 'ui_draft_created',
                'reply': reply,
                'metadata': {
                    'tier': tier,
                    'resolution': res,
                    'format': fmt,
                }
            }
        except Exception as e:
            logger.error(f"UIDRAFT via SMS failed: {e}")
            return {
                'action': 'ui_draft_failed',
                'reply': "Couldn't create UI draft right now. Please try again or use the IDE.",
                'error': str(e),
            }

    async def _handle_plan(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle PLAN command -> create a minimal build plan from comma-separated features"""
        try:
            from backend.services.build_plan_approval_service import get_plan_approval_service, PlanStep
            svc = get_plan_approval_service()
            raw = command.content or "scaffold app, add auth"
            # Split on commas into coarse features
            parts = [p.strip() for p in re.split(r",|;|\n", raw) if p.strip()]
            if not parts:
                parts = [raw]
            steps = []
            for i, p in enumerate(parts, start=1):
                steps.append(PlanStep(
                    step_id=f"sms-{i}",
                    order=i,
                    description=p,
                    estimated_duration="1h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria=f"Tests pass for: {p[:40]}"
                ))
            plan = svc.generate_plan(
                workflow_id=f"wf-sms-{command.user_id}",
                generated_by="sms",
                objective="User-initiated plan via SMS",
                scope="MVP",
                steps=steps,
                risks=[],
                dependencies_to_install=[],
                files_to_create=[],
                files_to_modify=[],
                files_to_delete=[],
                estimated_total_duration=None,
            )
            reply = f"Plan drafted with {len(steps)} step(s). Reply: APPROVE {plan.plan_id} to proceed."
            return {
                'action': 'plan_created',
                'reply': reply,
                'plan_id': plan.plan_id,
                'steps': [s.description for s in steps],
            }
        except Exception as e:
            logger.error(f"PLAN via SMS failed: {e}")
            return {
                'action': 'plan_failed',
                'reply': "Couldn't create plan. Try again with: PLAN feature1, feature2",
                'error': str(e),
            }

    async def _handle_approve(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle APPROVE <plan_id> -> approve and start execution"""
        try:
            from backend.services.build_plan_approval_service import get_plan_approval_service
            plan_id = (command.content or '').split()[0]
            if not plan_id:
                return {'action': 'approve_failed', 'reply': 'Usage: APPROVE <plan_id>'}
            svc = get_plan_approval_service()
            plan = svc.approve_plan(plan_id, approved_by=command.user_id)
            if not plan:
                return {'action': 'approve_failed', 'reply': 'Plan not found or cannot be approved.'}
            # Optionally start execution
            plan = svc.start_execution(plan_id) or plan
            return {
                'action': 'plan_approved',
                'reply': f"Plan {plan_id} approved and started.",
                'plan_id': plan_id,
            }
        except Exception as e:
            logger.error(f"APPROVE via SMS failed: {e}")
            return {
                'action': 'approve_failed',
                'reply': 'Approval failed. Check the plan id and try again.',
                'error': str(e),
            }

    async def _handle_modify(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle MODIFY [change-notes] -> either send a link to a change form or create a revised plan and return approval link."""
        try:
            import os
            from backend.services.email_token_service import register_token
            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
            changes = (command.content or '').strip()
            if not changes:
                # Issue a modify token so the user can open a small change form
                token = register_token({
                    "kind": "ui_draft_modify",
                    "project_id": command.user_id,
                    "description": "SMS change request",
                }, expires_seconds=24*3600)
                link = f"{backend_url.rstrip('/')}/api/assistant/modify-email?token={token}"
                return {
                    'action': 'modify_link_sent',
                    'reply': f"Open to request changes: {link}",
                    'link': link,
                }
            # Create a revised plan now and provide an approval link
            from backend.services.build_plan_approval_service import get_plan_approval_service, PlanStep
            svc = get_plan_approval_service()
            import uuid
            workflow_id = f"wf-smsmod-{uuid.uuid4().hex[:8]}"
            steps = [
                PlanStep(
                    step_id="step-1",
                    order=1,
                    description=f"Apply requested changes: {changes[:200]}",
                    estimated_duration="1-2h",
                    files_affected=[],
                    dependencies=[],
                    risk_level="low",
                    verification_criteria="Updated UI reflects requested changes",
                ),
                PlanStep(
                    step_id="step-2",
                    order=2,
                    description="Regenerate UI draft and confirm",
                    estimated_duration="1h",
                    files_affected=[],
                    dependencies=["step-1"],
                    risk_level="low",
                    verification_criteria="New draft approved",
                ),
            ]
            plan = svc.generate_plan(
                workflow_id=workflow_id,
                generated_by="sms-modify",
                objective="Revise UI per SMS changes",
                scope=f"Changes: {changes}",
                steps=steps,
                risks=[],
                dependencies_to_install=[],
                files_to_create=[],
                files_to_modify=[],
                files_to_delete=[],
                estimated_total_duration=None,
            )
            approve_token = register_token({
                "kind": "plan_approval",
                "plan_id": plan.plan_id,
                "start_execution": True,
            }, expires_seconds=7*24*3600)
            approve_link = f"{backend_url.rstrip('/')}/api/assistant/approve-email?token={approve_token}"
            return {
                'action': 'modify_plan_created',
                'reply': f"Revised plan ready. Approve here: {approve_link}",
                'plan_id': plan.plan_id,
                'link': approve_link,
            }
        except Exception as e:
            logger.error(f"MODIFY via SMS failed: {e}")
            return {
                'action': 'modify_failed',
                'reply': 'Could not process change request. Try again or use the email link.',
                'error': str(e),
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

UI DRAFT: <desc>
Create a low-cost UI visual

PLAN: feature1, feature2
Create a build plan from features

APPROVE <plan_id>
Approve and start execution

MODIFY [notes]
Request changes (link if no notes)

PAIR [phone]
Enable away mode and verify via SMS link

UNPAIR
Disable away mode

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
        # Save as a note AND route to assistant inbox
        note = {
            'id': len(self.notes) + 1,
            'content': command.content,
            'user_id': command.user_id,
            'phone_number': command.phone_number,
            'created_at': command.timestamp.isoformat(),
            'type': 'freeform'
        }
        self.notes.append(note)
        try:
            from backend.services.assistant_inbox import add_message
            add_message(command.user_id, "sms", command.content, {
                "phone": command.phone_number,
                "raw": command.raw_message,
            })
            # Immediate triage so natural language like "add ..." executes now
            try:
                from backend.services.assistant_inbox_triage import triage_and_act
                await triage_and_act(user_id=command.user_id, limit=10)
            except Exception:
                pass
        except Exception:
            pass
        auto = False
        try:
            import os
            auto = os.getenv("ASSISTANT_INBOX_AUTOREPLY", "false").lower() in ("1","true","yes")
        except Exception:
            auto = False
        reply = f"💬 Saved your message as a note and queued for assistant:\n\n\"{command.content}\""
        if not auto:
            reply += "\n\nReply HELP for commands."
        return {
            'action': 'saved_to_inbox',
            'note': note,
            'reply': reply
        }

    async def _handle_pair(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle AWAY ON <phone>/PAIR <phone> or AWAY ON/PAIR (use sender number).
        Sends a verification link by SMS which, when tapped, completes pairing.
        """
        try:
            phone = command.content.strip()
            if not phone:
                phone = command.phone_number
            from backend.services.email_token_service import register_token
            from backend.services.sms_sender import get_sms_sender
            import os
            token = register_token({
                "kind": "away_pair_verify",
                "user_id": command.user_id,
                "phone": phone,
            }, expires_seconds=30*60)
            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
            link = f"{backend_url.rstrip('/')}/api/away/verify-sms?token={token}"
            body = (
                "Q‑IDE: Tap to confirm pairing and enable SMS-first away mode.\n"
                f"Verify: {link}"
            )
            get_sms_sender().send_sms_text(phone, body)
            return {
                'action': 'away_verification_sent',
                'reply': f"Verification link sent to {phone}. Tap to complete pairing.",
                'phone': phone,
            }
        except Exception as e:
            logger.error(f"PAIR via SMS failed: {e}")
            return {'action': 'away_pair_failed', 'reply': 'Could not set away mode.', 'error': str(e)}

    async def _handle_unpair(self, command: SMSCommand) -> Dict[str, Any]:
        """Handle AWAY OFF or UNPAIR to clear away phone."""
        try:
            from backend.services.away_store import clear_away_phone
            clear_away_phone(command.user_id)
            return {
                'action': 'away_unpaired',
                'reply': "✓ Away mode disabled. We'll stop sending SMS first.",
            }
        except Exception as e:
            logger.error(f"UNPAIR via SMS failed: {e}")
            return {'action': 'away_unpair_failed', 'reply': 'Could not disable away mode.', 'error': str(e)}
    
    def get_todos(self, user_id: str) -> List[dict]:
        """Get todos for user (from persistent store if available)"""
        try:
            from backend.services.tasks_service import get_tasks_service
            svc = get_tasks_service()
            return [t.to_dict() for t in svc.list_tasks(user_id)]
        except Exception:
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
