from .. import db
from datetime import datetime

class ChatHistory(db.Model):
    """Chat history model"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    chat_type = db.Column(db.String(50), nullable=False)  # 'rag' or 'tool'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    extra_metadata = db.Column(db.JSON, nullable=True)  # Additional metadata (tools used, sources, etc.)
    
    def to_dict(self):
        """Convert chat history to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'chat_type': self.chat_type,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.extra_metadata
        }
