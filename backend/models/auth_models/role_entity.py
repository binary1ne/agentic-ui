from .. import db
from datetime import datetime
import bcrypt


class RoleModel(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    active_flag = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'description': self.description,
            'active_flag': self.active_flag,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }