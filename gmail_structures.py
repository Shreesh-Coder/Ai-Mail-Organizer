from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Message:
    """Represents a single email message."""
    from_email: str
    subject: str
    date: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    body: str = ""

@dataclass
class Thread:
    """Represents a thread of email messages."""
    thread_id: str
    history_id: str
    messages: List[Message]

