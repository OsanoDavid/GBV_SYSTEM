from django.db import models

# Create your models here.
from django.db import models

class HelpChatSession(models.Model):
    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat Session {self.session_token[:8]}"

class ChatMessage(models.Model):
    session = models.ForeignKey(HelpChatSession, on_delete=models.CASCADE, related_name="messages")
    is_from_user = models.BooleanField(default=True)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "User" if self.is_from_user else "AI Assistant"
        return f"{sender} at {self.timestamp.strftime('%H:%M:%S')}"