from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from .auth_entities import RoleModel, UserDetailsModel, UserRoleMappingModel
from .component_entities import ComponentModel, ComponentRoleMappingModel
from .guardrails_entities import GuardrailsConfig, GuardrailsLog
from .agentic_entities.chat import ChatHistory
from .agentic_entities.document import Document
from .agentic_entities.system import SystemConfig
