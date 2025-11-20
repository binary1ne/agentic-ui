from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


class Role(db.Model):
    """Role model for RBAC"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    component_accesses = db.relationship('ComponentAccess', backref='role', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    documents = db.relationship('Document', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    guardrails_logs = db.relationship('GuardrailsLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.has_role('admin')
    
    def get_role_names(self):
        """Get list of role names"""
        return [role.name for role in self.roles]
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'roles': self.get_role_names(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Document(db.Model):
    """Document model for RAG system"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    
    def __repr__(self):
        return f'<Document {self.filename}>'


class ChatHistory(db.Model):
    """Chat history model"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    
    def __repr__(self):
        return f'<ChatHistory {self.id} - {self.chat_type}>'


class ComponentAccess(db.Model):
    """Component access control model"""
    __tablename__ = 'component_access'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    component_name = db.Column(db.String(100), nullable=False)
    has_access = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('role_id', 'component_name', name='_role_component_uc'),)
    
    def to_dict(self):
        """Convert component access to dictionary"""
        role = Role.query.get(self.role_id)
        return {
            'id': self.id,
            'role_id': self.role_id,
            'role_name': role.name if role else None,
            'component_name': self.component_name,
            'has_access': self.has_access
        }
    
    def __repr__(self):
        return f'<ComponentAccess role_id={self.role_id} - {self.component_name}>'


class ComponentMetadata(db.Model):
    """Component metadata for dynamic navigation"""
    __tablename__ = 'component_metadata'
    
    name = db.Column(db.String(100), primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # Emoji or icon class
    description = db.Column(db.Text, nullable=True)
    admin_only = db.Column(db.Boolean, default=False)  # Deprecated: use role-based access
    
    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'icon': self.icon,
            'description': self.description,
            'admin_only': self.admin_only
        }
    
    def __repr__(self):
        return f'<ComponentMetadata {self.name}>'


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
    
    def __repr__(self):
        return f'<GuardrailsConfig {self.rule_type}>'


class GuardrailsLog(db.Model):
    """Guardrails detection log model"""
    __tablename__= 'guardrails_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    guardrail_id = db.Column(db.Integer, db.ForeignKey('guardrails_config.id'), nullable=True)
    detected_rule = db.Column(db.String(100), nullable=False)
    content_snippet = db.Column(db.Text, nullable=True)  # Snippet of flagged content
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    action_taken = db.Column(db.String(50), default='blocked')  # 'blocked', 'warned', 'logged'
    
    def to_dict(self):
        """Convert guardrails log to dictionary"""
        user = User.query.get(self.user_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': user.email if user else 'Unknown',
            'detected_rule': self.detected_rule,
            'content_snippet': self.content_snippet,
            'timestamp': self.timestamp.isoformat(),
            'action_taken': self.action_taken
        }
    
    def __repr__(self):
        return f'<GuardrailsLog {self.detected_rule}>'


class SystemConfig(db.Model):
    """System configuration settings"""
    __tablename__ = 'system_config'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.key}={self.value}>'
