from .. import db
from datetime import datetime
import bcrypt



class UserRoleMappingModel(db.Model):
    __tablename__ = "user_role_mapping"

    user_role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    active_flag = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(255))

    # relationships
    user = db.relationship("UserDetailsModel", backref="user_roles")
    role = db.relationship("RoleModel", backref="role_users")

    def to_dict(self):
        return {
            'user_role_id': self.user_role_id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'active_flag': self.active_flag,
            'description': self.description
        }
