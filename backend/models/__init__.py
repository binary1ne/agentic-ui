from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from .auth_models.role_entity import RoleModel
from .auth_models.user_entity import UserDetailsModel
from .auth_models.mapping_entities import UserRoleMappingModel

from .system_models.managemnt_models import SystemConfig
from .system_models.template_models.template_entity import ComponentModel
from .system_models.template_models.mapping_entities import ComponentRoleMappingModel

from .components.guardrails_models.gr_config_entity import GuardrailsConfig
from .components.guardrails_models.gr_log_entity import GuardrailsLog

from .components.agentic_models.chat_entity import ChatHistory
from .components.agentic_models.document_entity import Document


