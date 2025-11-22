from ... import db
from datetime import datetime

class Document(db.Model):
    """Document model for RAG system"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    vector_store_id = db.Column(db.String(100), nullable=True)  # Chroma collection ID
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'user_id': self.user_id,
            'uploaded_at': self.uploaded_at.isoformat(),
            'file_size': self.file_size
        }
