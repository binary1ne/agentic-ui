from . import db

class ComponentModel(db.Model):
    __tablename__ = "templates"

    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    template_name = db.Column(db.String(120), nullable=False, unique=True)
    template_icon = db.Column(db.String(100))
    description = db.Column(db.String(255))
    component_mode = db.Column(db.String(255), nullable=False) #'VALUE SHOULD BE : COMPONENT/PATH'
    component_value = db.Column(db.String(255), nullable=False) #'Respective VALUE SHOULD STORE If component then component name if path then Path value' 
    active_flag = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self):
        return {
            'template_id': self.template_id,
            'template_icon': self.template_icon,
            'template_name': self.template_name,
            'description': self.description,
            'component_mode': self.component_mode,
            'component_value': self.component_value,
            'active_flag': self.active_flag
        }

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
