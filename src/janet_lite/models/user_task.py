import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class TaskAction:
    """Represents an action taken as part of a task."""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_query: str = ""
    action_command: str = "none"
    action_params: Dict[str, Any] = field(default_factory=dict)
    action_result: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # could be 'pending', 'in_progress', 'completed', 'failed'
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')


@dataclass
class UserTask:
    """A data model for an Ollama LLM query and response."""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    model: str = ""
    prompt: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    response_actions: List[Dict[str, Any]] = field(default_factory=list)
    response: str = ""
    task: TaskAction = field(default_factory=TaskAction)
    user_query: str = ""   # <-- added properly
    intent: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')


@dataclass
class Conversation:
    """A data model for a conversation, containing multiple tasks."""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[UserTask] = field(default_factory=list)
    title: str = "New Conversation"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
