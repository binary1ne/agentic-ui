from models import db, User, Role, ComponentAccess, ComponentMetadata, SystemConfig

def init_db(app):
    """Initialize database with default data"""
    with app.app_context():
        # Create tables
        print("Creating database tables...")
        db.create_all()
        
        # 1. Create default roles
        print("Creating default roles...")
        roles_data = [
            {'name': 'admin', 'description': 'Administrator with full access'},
            {'name': 'user', 'description': 'Regular user with standard access'}
        ]
        
        roles = {}
        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
                db.session.flush()  # Get the role ID
            roles[role_data['name']] = role
        
        db.session.commit()
        print(f"✓ Created roles: {', '.join(roles.keys())}")
        
        # 2. Create default admin user
        admin_email = 'admin@mail.com'
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                full_name='Administrator'
            )
            admin.set_password('password')
            admin.roles.append(roles['admin'])  # Assign admin role
            db.session.add(admin)
            db.session.commit()
            print(f'✓ Created default admin user: {admin_email} / password')
        else:
            # Ensure admin has admin role
            if not admin.has_role('admin'):
                admin.roles.append(roles['admin'])
                db.session.commit()
                print(f'✓ Added admin role to existing user: {admin_email}')
        
        # 3. Initialize Guardrails
        print("Initializing guardrails...")
        from services.guardrails_service import GuardrailsService
        GuardrailsService.initialize_defaults()
        
        # 4. Initialize System Config
        print("Initializing system config...")
        if not SystemConfig.query.get('signup_enabled'):
            signup_config = SystemConfig(
                key='signup_enabled',
                value='true',
                description='Enable or disable public user registration'
            )
            db.session.add(signup_config)
            db.session.commit()
        
        # 5. Define navigation items (Components)
        nav_items = [
            {
                'name': 'AGENTIC_RAG',
                'label': 'Agentic RAG',
                'icon': '📚',
                'description': 'Chat with your documents using AI',
                'roles': ['admin', 'user']  # Both roles have access
            },
            {
                'name': 'NORMAL_CHAT',
                'label': 'Tool Chat',
                'icon': '💬',
                'description': 'General AI chat with tool capabilities',
                'roles': ['admin', 'user']
            },
            {
                'name': 'GUARDRAILS_INSIGHTS',
                'label': 'Guardrails Insights',
                'icon': '🛡️',
                'description': 'View security and safety alerts',
                'roles': ['admin', 'user']
            },
            {
                'name': 'USER_MANAGEMENT',
                'label': 'User Management',
                'icon': '👥',
                'description': 'Manage system users',
                'roles': ['admin']  # Admin only
            },
            {
                'name': 'COMPONENT_MANAGEMENT',
                'label': 'Component Management',
                'icon': '🔧',
                'description': 'Manage component access',
                'roles': ['admin']
            },
            {
                'name': 'GUARDRAILS_CONFIGURATION',
                'label': 'Guardrails Config',
                'icon': '⚙️',
                'description': 'Configure safety guardrails',
                'roles': ['admin']
            },
            {
                'name': 'ROLE_MANAGEMENT',
                'label': 'Role Management',
                'icon': '🔐',
                'description': 'Manage roles and permissions',
                'roles': ['admin']
            }
        ]
        
        print("Initializing navigation items...")
        for item_data in nav_items:
            metadata = ComponentMetadata.query.get(item_data['name'])
            if not metadata:
                metadata = ComponentMetadata(
                    name=item_data['name'],
                    label=item_data['label'],
                    icon=item_data['icon'],
                    description=item_data['description'],
                    admin_only=(item_data['roles'] == ['admin'])  # Legacy field
                )
                db.session.add(metadata)
            else:
                # Update existing
                metadata.label = item_data['label']
                metadata.icon = item_data['icon']
                metadata.description = item_data['description']
                metadata.admin_only = (item_data['roles'] == ['admin'])
        
        db.session.commit()
        
        # 6. Ensure ComponentAccess exists for roles
        print("Ensuring role-based access rules...")
        for item in nav_items:
            for role_name in item['roles']:
                role = roles.get(role_name)
                if not role:
                    continue
                
                access = ComponentAccess.query.filter_by(
                    role_id=role.id,
                    component_name=item['name']
                ).first()
                
                if not access:
                    access = ComponentAccess(
                        role_id=role.id,
                        component_name=item['name'],
                        has_access=True
                    )
                    db.session.add(access)
        
        db.session.commit()
        print("✓ Database initialization completed successfully!")
