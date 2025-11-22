from ... import db

class ComponentRoleMappingModel(db.Model):
    __tablename__ = "template_role_mapping"

    template_role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template_id = db.Column(db.Integer,db.ForeignKey("templates.template_id"),nullable=False)
    role_id = db.Column(db.Integer,db.ForeignKey("roles.role_id"),nullable=False)

    active_flag = db.Column(db.Boolean, nullable=False, default=True)

    # relationships
    template = db.relationship("ComponentModel", backref="template_roles")
    role = db.relationship("RoleModel", backref="role_templates")

    def to_dict(self):
        return {
            'template_role_id': self.template_role_id,
            'template_id': self.template_id,
            'role_id': self.role_id,
            'active_flag': self.active_flag
        }