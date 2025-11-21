from marshmallow import Schema,fields

# Additional Schemas
class VerifyOtpSchema(Schema):
    email = fields.Email(required=True)
    otp = fields.Str(required=True)
    role = fields.Str(allow_none=True)