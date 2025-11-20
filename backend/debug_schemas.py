from marshmallow import Schema, fields, ValidationError
import sys

# Mock schemas from the codebase
class UserSchema(Schema):
    """User schema"""
    id = fields.Int()
    email = fields.Email()
    full_name = fields.Str(allow_none=True)
    role = fields.Str()
    created_at = fields.Str()

class CreateUserSchema(Schema):
    """Create user schema"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    role = fields.Str(missing='user', validate=lambda r: r in ['user', 'admin'])
    full_name = fields.Str(missing=None, allow_none=True)

class DocumentSchema(Schema):
    """Document schema"""
    id = fields.Int()
    filename = fields.Str()
    user_id = fields.Int()
    uploaded_at = fields.Str()
    file_size = fields.Int(allow_none=True)

def test_user_schema():
    print("\nTesting UserSchema (Response)...")
    schema = UserSchema()
    
    # Case 1: Full valid data
    data1 = {
        'id': 1,
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'user',
        'created_at': '2023-01-01T00:00:00'
    }
    try:
        schema.dump(data1)
        print("Case 1 (Full data): PASS")
    except Exception as e:
        print(f"Case 1 (Full data): FAIL - {e}")

    # Case 2: None full_name
    data2 = {
        'id': 1,
        'email': 'test@example.com',
        'full_name': None,
        'role': 'user',
        'created_at': '2023-01-01T00:00:00'
    }
    try:
        schema.dump(data2)
        print("Case 2 (None full_name): PASS")
    except Exception as e:
        print(f"Case 2 (None full_name): FAIL - {e}")

def test_create_user_schema():
    print("\nTesting CreateUserSchema (Request)...")
    schema = CreateUserSchema()
    
    # Case 1: Full valid data
    data1 = {
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'user',
        'full_name': 'Test User'
    }
    try:
        schema.load(data1)
        print("Case 1 (Full data): PASS")
    except Exception as e:
        print(f"Case 1 (Full data): FAIL - {e}")

    # Case 2: Missing full_name (should use default None)
    data2 = {
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'user'
    }
    try:
        result = schema.load(data2)
        print(f"Case 2 (Missing full_name): PASS - full_name={result.get('full_name')}")
    except Exception as e:
        print(f"Case 2 (Missing full_name): FAIL - {e}")

    # Case 3: None full_name
    data3 = {
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'user',
        'full_name': None
    }
    try:
        result = schema.load(data3)
        print(f"Case 3 (None full_name): PASS - full_name={result.get('full_name')}")
    except Exception as e:
        print(f"Case 3 (None full_name): FAIL - {e}")

def test_document_schema():
    print("\nTesting DocumentSchema (Response)...")
    schema = DocumentSchema()
    
    # Case 1: None file_size
    data1 = {
        'id': 1,
        'filename': 'test.pdf',
        'user_id': 1,
        'uploaded_at': '2023-01-01T00:00:00',
        'file_size': None
    }
    try:
        schema.dump(data1)
        print("Case 1 (None file_size): PASS")
    except Exception as e:
        print(f"Case 1 (None file_size): FAIL - {e}")

if __name__ == "__main__":
    test_user_schema()
    test_create_user_schema()
    test_document_schema()
