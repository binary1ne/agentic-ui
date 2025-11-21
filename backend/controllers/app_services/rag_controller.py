from flask import request, jsonify
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.datastructures import FileStorage

from services.agentic_services.rag_service import RAGService
from services.guardrails_services.guardrails_service import GuardrailsService
from dtos.app_data.rag_dto import (
    DocumentSchema, RagChatRequestSchema, RagChatResponseSchema
)

from utils.marshmallow_utils import marshmallow_to_restx_model

rag_ns = Namespace('rag', description='RAG (Retrieval Augmented Generation) operations')

# Models for Swagger generated from Marshmallow Schemas
document_model = marshmallow_to_restx_model(rag_ns, DocumentSchema)
chat_request_model = marshmallow_to_restx_model(rag_ns, RagChatRequestSchema)
chat_response_model = marshmallow_to_restx_model(rag_ns, RagChatResponseSchema)

upload_parser = rag_ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Document file')

@rag_ns.route('/upload')
class UploadDocument(Resource):
    @rag_ns.doc('upload_document')
    @rag_ns.expect(upload_parser)
    @rag_ns.marshal_with(document_model, code=201)
    @jwt_required()
    def post(self):
        """Upload document for RAG"""
        try:
            user_id = get_jwt_identity()
            
            args = upload_parser.parse_args()
            file = args['file']
            
            # Initialize RAG service
            rag_service = RAGService()
            
            # Upload and process document
            document = rag_service.upload_document(file, user_id)
            
            return DocumentSchema().dump(document), 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': f'Upload failed: {str(e)}'}, 500

@rag_ns.route('/chat')
class RagChat(Resource):
    @rag_ns.doc('chat_rag')
    @rag_ns.expect(chat_request_model)
    @rag_ns.marshal_with(chat_response_model)
    @jwt_required()
    def post(self):
        """Chat with documents using RAG"""
        try:
            user_id = get_jwt_identity()
            data = RagChatRequestSchema().load(request.get_json())
            
            # Check guardrails on input
            guardrails_result = GuardrailsService.check_content(
                data['query'],
                user_id,
                'input'
            )
            
            if not guardrails_result['passed']:
                rag_ns.abort(400, 'Content violates guardrails', violations=guardrails_result['violations'])
            
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
            
            return RagChatResponseSchema().dump(response), 200
        except ValidationError as err:
            return err.messages, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': f'Chat failed: {str(e)}'}, 500

@rag_ns.route('/documents')
class DocumentList(Resource):
    @rag_ns.doc('list_documents')
    @rag_ns.marshal_list_with(document_model)
    @jwt_required()
    def get(self):
        """Get user's documents"""
        try:
            user_id = get_jwt_identity()
            rag_service = RAGService()
            documents = rag_service.get_user_documents(user_id)
            return DocumentSchema(many=True).dump(documents), 200
        except Exception as e:
            return {'message': str(e)}, 500

@rag_ns.route('/documents/<int:document_id>')
@rag_ns.param('document_id', 'Document ID')
class Document(Resource):
    @rag_ns.doc('delete_document')
    @jwt_required()
    def delete(self, document_id):
        """Delete document"""
        try:
            user_id = get_jwt_identity()
            rag_service = RAGService()
            result = rag_service.delete_document(document_id, user_id)
            return result, 200
        except ValueError as e:
            return {'message': str(e)}, 404
        except Exception as e:
            return {'message': str(e)}, 500
