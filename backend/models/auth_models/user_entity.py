from .. import db
from datetime import datetime
import bcrypt


class UserDetailsModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    user_password = db.Column(db.String(200), nullable=False)
    active_flag = db.Column(db.Boolean, nullable=False, default=True)
    
    # New fields
    file_upload_enabled = db.Column(db.Boolean, default=False)
    two_factor_auth_enabled = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(100), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.user_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.user_password.encode('utf-8'))

    def has_role(self, role_name):
        """Check if user has a specific role"""
        # user_roles is the backref from UserRoleMappingModel
        return any(ur.role.role_name == role_name for ur in self.user_roles if ur.active_flag)

    def is_admin(self):
        """Check if user has admin role"""
        return self.has_role('admin')

    def get_role_names(self):
        """Get list of role names"""
        return [ur.role.role_name for ur in self.user_roles if ur.active_flag]

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'roles': self.get_role_names(),
            'active_flag': self.active_flag,
            'file_upload_enabled': self.file_upload_enabled,
            'two_factor_auth_enabled': self.two_factor_auth_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
