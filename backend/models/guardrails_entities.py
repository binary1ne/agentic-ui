from . import db
from datetime import datetime
from .auth_entities import UserDetailsModel

class GuardrailsConfig(db.Model):
    """Guardrails configuration model"""
    __tablename__ = 'guardrails_config'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_type = db.Column(db.String(100), nullable=False, unique=True)
    enabled = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    description = db.Column(db.Text, nullable=True)
    pattern = db.Column(db.Text, nullable=True)  # Regex pattern or keywords
    
    def to_dict(self):
        """Convert guardrails config to dictionary"""
        return {
            'id': self.id,
            'rule_type': self.rule_type,
            'enabled': self.enabled,
            'severity': self.severity,
            'description': self.description,
            'pattern': self.pattern
        }

class GuardrailsLog(db.Model):
    """Guardrails detection log model"""
    __tablename__= 'guardrails_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    guardrail_id = db.Column(db.Integer, db.ForeignKey('guardrails_config.id'), nullable=True)
    detected_rule = db.Column(db.String(100), nullable=False)
    content_snippet = db.Column(db.Text, nullable=True)  # Snippet of flagged content
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    action_taken = db.Column(db.String(50), default='blocked')  # 'blocked', 'warned', 'logged'
    
    def to_dict(self):
        """Convert guardrails log to dictionary"""
        user = UserDetailsModel.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': user.email if user else 'Unknown',
            'detected_rule': self.detected_rule,
            'content_snippet': self.content_snippet,
            'timestamp': self.timestamp.isoformat(),
            'action_taken': self.action_taken
        }
