from app import create_app
from models import db, ComponentRoleMappingModel, RoleModel

app = create_app()

with app.app_context():
    print("\nChecking Component Access for USER role:")
    
    # Get user role
    user_role = RoleModel.query.filter_by(role_name='user').first()
    if not user_role:
        print("User role not found")
        exit()
        
    mappings = ComponentRoleMappingModel.query.filter_by(role_id=user_role.role_id).all()
    
    for mapping in mappings:
        template_name = mapping.template.template_name if mapping.template else "Unknown"
        print(f"- {template_name}: {mapping.active_flag}")
        
    print("\nResetting 'AGENTIC_RAG' to False for USER role (as per user request)...")
    
    # Find AGENTIC_RAG template
    from models import ComponentModel
    rag_template = ComponentModel.query.filter_by(template_name='AGENTIC_RAG').first()
    
    if rag_template:
        rag_mapping = ComponentRoleMappingModel.query.filter_by(
            role_id=user_role.role_id, 
            template_id=rag_template.template_id
        ).first()
        
        if rag_mapping:
            rag_mapping.active_flag = False
            db.session.commit()
            print("✓ Reset AGENTIC_RAG to False")
        else:
            print("! AGENTIC_RAG access record not found")
    else:
        print("! AGENTIC_RAG template not found")
        
    print("\nVerifying new state:")
    mappings = ComponentRoleMappingModel.query.filter_by(role_id=user_role.role_id).all()
    for mapping in mappings:
        template_name = mapping.template.template_name if mapping.template else "Unknown"
        print(f"- {template_name}: {mapping.active_flag}")
