from flask import request
from flask.views import MethodView
from flask_smorest import abort, Blueprint as SmoreBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields

from services import RAGService, AuthService, GuardrailsService

# Create blueprint
rag_bp = SmoreBlueprint(
    'rag',
    __name__,
    url_prefix='/api/rag',
    description='LangChain Agentic RAG endpoints'
)

# Schemas
from dtos.app_data.rag_dto import (
    DocumentSchema, RagChatRequestSchema, RagChatResponseSchema
)

# Routes
@rag_bp.route('/upload')
class UploadView(MethodView):
    @jwt_required()
    @rag_bp.response(201, DocumentSchema)
    def post(self):
        """Upload document for RAG"""
        try:
            user_id = get_jwt_identity()
            
            # Get file from request
            if 'file' not in request.files:
                abort(400, message='No file provided')
            
            file = request.files['file']
            
            # Initialize RAG service
            rag_service = RAGService()
            
            # Upload and process document
            document = rag_service.upload_document(file, user_id)
            
            return document
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'Upload failed: {str(e)}')

@rag_bp.route('/chat')
class RAGChatView(MethodView):
    @jwt_required()
    @rag_bp.arguments(RagChatRequestSchema)
    @rag_bp.response(200, RagChatResponseSchema)
    def post(self, data):
        """Chat with documents using RAG"""
        try:
            user_id = get_jwt_identity()
            
            # Check guardrails on input
            guardrails_result = GuardrailsService.check_content(
                data['query'],
                user_id,
                'input'
            )
            
            if not guardrails_result['passed']:
                abort(400, message='Content violates guardrails', 
                      violations=guardrails_result['violations'])
            
            # Initialize RAG service
            rag_service = RAGService()
            
            # Process chat
            response = rag_service.chat_with_documents(
                query=data['query'],
                user_id=user_id,
                use_internet=data.get('use_internet', False)
            )
            
            # Check guardrails on output
            output_check = GuardrailsService.check_content(
                response['answer'],
                user_id,
                'output'
            )
            
            if not output_check['passed']:
                response['answer'] = output_check['cleaned_content']
            
            return response
        except ValueError as e:
            abort(400, message=str(e))
        except Exception as e:
            abort(500, message=f'Chat failed: {str(e)}')

@rag_bp.route('/documents')
class DocumentsView(MethodView):
    @jwt_required()
    @rag_bp.response(200, DocumentSchema(many=True))
    def get(self):
        """Get user's documents"""
        try:
            user_id = get_jwt_identity()
            rag_service = RAGService()
            documents = rag_service.get_user_documents(user_id)
            return documents
        except Exception as e:
            abort(500, message=str(e))

@rag_bp.route('/documents/<int:document_id>')
class DocumentView(MethodView):
    @jwt_required()
    def delete(self, document_id):
        """Delete document"""
        try:
            user_id = get_jwt_identity()
            rag_service = RAGService()
            result = rag_service.delete_document(document_id, user_id)
            return result
        except ValueError as e:
            abort(404, message=str(e))
        except Exception as e:
            abort(500, message=str(e))
