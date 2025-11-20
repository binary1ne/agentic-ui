from app import create_app
from models import db, ComponentAccess, RoleEnum

app = create_app()

with app.app_context():
    print("\nChecking Component Access for USER role:")
    access_records = ComponentAccess.query.filter_by(role=RoleEnum.USER).all()
    
    for record in access_records:
        print(f"- {record.component_name}: {record.has_access}")
        
        # Fix: Ensure default is False for Agentic RAG if it was accidentally set to True
        # But wait, the user says "I have Not Assigned...". 
        # If it's True, it means it WAS assigned or initialized as True.
        
    print("\nResetting 'AGENTIC_RAG' to False for USER role (as per user request)...")
    rag_access = ComponentAccess.query.filter_by(
        role=RoleEnum.USER, 
        component_name='AGENTIC_RAG'
    ).first()
    
    if rag_access:
        rag_access.has_access = False
        db.session.commit()
        print("✓ Reset AGENTIC_RAG to False")
    else:
        print("! AGENTIC_RAG access record not found")
        
    print("\nVerifying new state:")
    access_records = ComponentAccess.query.filter_by(role=RoleEnum.USER).all()
    for record in access_records:
        print(f"- {record.component_name}: {record.has_access}")
