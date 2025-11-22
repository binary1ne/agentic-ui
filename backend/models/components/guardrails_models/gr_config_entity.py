from datetime import datetime
from ... import db

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
