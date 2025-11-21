from models import db
from models.auth_entities import UserDetailsModel, RoleModel, UserRoleMappingModel
from models.component_entities import ComponentModel, ComponentRoleMappingModel
from models.agentic_entities.system import SystemConfig
from services.auth_services.auth_service import AuthService

def init_db(app):
    """Initialize database with default data"""
    with app.app_context():

        # ---------------------------------------------
        # 1. Create tables
        # ---------------------------------------------
        print("Creating database tables...")
        db.create_all()

        # ---------------------------------------------
        # 2. Create default roles
        # ---------------------------------------------
        print("Creating default roles...")
        roles_data = [
            {'role_name': 'admin', 'description': 'Administrator with full access to all components'},
            {'role_name': 'moderator', 'description': 'Moderator with limited administrative access'},
            {'role_name': 'user', 'description': 'Regular user with standard access'},
        ]

        roles = {}
        for role_data in roles_data:
            role = RoleModel.query.filter_by(role_name=role_data['role_name']).first()
            if not role:
                role = RoleModel(**role_data)
                db.session.add(role)
                db.session.flush()
            roles[role_data['role_name']] = role

        db.session.commit()
        print(f"✓ Created roles: {', '.join(roles.keys())}")

        # ---------------------------------------------
        # 3. Create default admin user
        # ---------------------------------------------
        admin_email = 'admin@mail.com'
        admin = UserDetailsModel.query.filter_by(email=admin_email).first()

        if not admin:
            try:
                admin = UserDetailsModel(
                    name='Administrator',
                    email=admin_email,
                    two_factor_auth_enabled=False,
                    file_upload_enabled=True,
                    active_flag=True
                )
                admin.set_password('password')
                db.session.add(admin)
                db.session.flush()

                admin_role_mapping = UserRoleMappingModel(
                    user_id=admin.user_id,
                    role_id=roles['admin'].role_id,
                    active_flag=True
                )
                db.session.add(admin_role_mapping)
                db.session.commit()

                print(f"✓ Created default admin: {admin_email} / password (2FA disabled)")

            except Exception as e:
                print(f"Error creating admin user: {e}")
                db.session.rollback()

        else:
            admin.two_factor_auth_enabled = False
            if not admin.has_role('admin'):
                admin_role_mapping = UserRoleMappingModel(
                    user_id=admin.user_id,
                    role_id=roles['admin'].role_id,
                    active_flag=True
                )
                db.session.add(admin_role_mapping)

            db.session.commit()
            print(f"✓ Updated existing admin user: {admin_email}")

        # ---------------------------------------------
        # 4. Initialize Guardrails
        # ---------------------------------------------
        print("Initializing guardrails...")
        from services.guardrails_services.guardrails_service import GuardrailsService
        GuardrailsService.initialize_defaults()

        # ---------------------------------------------
        # 5. Initialize System Config
        # ---------------------------------------------
        print("Initializing system config...")
        if not SystemConfig.query.get('signup_enabled'):
            signup_config = SystemConfig(
                key='signup_enabled',
                value='true',
                description='Enable or disable public user registration'
            )
            db.session.add(signup_config)
            db.session.commit()

        # ---------------------------------------------
        # 6. Navigation items / Components
        # ---------------------------------------------
        nav_items = [
            {
                'name': 'AGENTIC_RAG',
                'label': 'Agentic RAG',
                'icon': '📚',
                "mode": "path",
                "value": "rag",
                'description': 'Chat with your documents using AI',
                'roles': ['admin', 'user']
            },
            {
                'name': 'NORMAL_CHAT',
                'label': 'Tool Chat',
                'icon': '💬',
                "mode": "path",
                "value": "chat",
                'description': 'General AI chat with tool capabilities',
                'roles': ['admin', 'user']
            },
            {
                'name': 'GUARDRAILS_INSIGHTS',
                'label': 'Guardrails Insights',
                'icon': '🛡️',
                "mode": "path",
                "value": "guardrails",
                'description': 'View security and safety alerts',
                'roles': ['admin', 'user']
            },
            {
                'name': 'USER_MANAGEMENT',
                'label': 'User Management',
                'icon': '👥',
                "mode": "path",
                "value": "users",
                'description': 'Manage system users',
                'roles': ['admin']
            },
            {
                'name': 'COMPONENT_MANAGEMENT',
                'label': 'Component Management',
                'icon': '🔧',
                "mode": "path",
                "value": "components",
                'description': 'Manage component access',
                'roles': ['admin']
            },
            {
                'name': 'GUARDRAILS_CONFIGURATION',
                'label': 'Guardrails Config',
                'icon': '⚙️',
                "mode": "path",
                "value": "guardrails/config",
                'description': 'Configure safety guardrails',
                'roles': ['admin']
            },
            {
                'name': 'ROLE_MANAGEMENT',
                'label': 'Role Management',
                'icon': '🔐',
                "mode": "path",
                "value": "roles",
                'description': 'Manage roles and permissions',
                'roles': ['admin']
            }
        ]

        # ---------------------------------------------
        # 7. Insert/Update components + role mapping
        # ---------------------------------------------
        print("Initializing navigation components...")

        for item_data in nav_items:

            # Create or update ComponentModel
            template = ComponentModel.query.filter_by(template_name=item_data['name']).first()

            if not template:
                template = ComponentModel(
                    template_name=item_data['name'],
                    template_icon=item_data['icon'],
                    description=item_data['description'],
                    component_mode=item_data["mode"],  
                    component_value=item_data["value"],  
                    active_flag=True
                )
                db.session.add(template)
                db.session.flush()

            else:
                template.template_icon = item_data['icon']
                template.description = item_data['description']
                template.component_mode = item_data['mode']
                template.component_value = item_data['value']

            # Create role mappings
            for role_name in item_data['roles']:
                role = roles.get(role_name)
                if not role:
                    continue

                mapping = ComponentRoleMappingModel.query.filter_by(
                    role_id=role.role_id,
                    template_id=template.template_id
                ).first()

                if not mapping:
                    mapping = ComponentRoleMappingModel(
                        role_id=role.role_id,
                        template_id=template.template_id,
                        active_flag=True
                    )
                    db.session.add(mapping)

        db.session.commit()

        print("✓ Database initialization complete!")
        print(f"✓ Admin has access to all {len(nav_items)} components")
        print("✓ Default credentials: admin@mail.com / password (2FA disabled)")
