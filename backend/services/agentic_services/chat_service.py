import os
import base64
from typing import Optional, List
import requests
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage

from models import db
from models import ChatHistory
from services.auth_services.auth_service import AuthService
from config import Config

class ChatService:
    """LangGraph tool calling chat service with OpenAI Vision support"""
    
    def __init__(self):
        """Initialize chat service"""
        if not Config.OPENAI_API_KEY:
            raise ValueError('OpenAI API key not configured')
        
        # Initialize OpenAI model with vision support
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            openai_api_key=Config.OPENAI_API_KEY,
            temperature=0.7
        )
        
        # Initialize tools
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize available tools"""
        tools = {
            'web_search': {
                'name': 'web_search',
                'description': 'Search the internet for current information',
                'func': self._web_search
            },
            'api_call': {
                'name': 'api_call',
                'description': 'Make HTTP GET request to a URL',
                'func': self._api_call
            },
            'calculator': {
                'name': 'calculator',
                'description': 'Perform mathematical calculations',
                'func': self._calculator
            }
        }
        return tools
    
    def _web_search(self, query: str) -> str:
        """Web search using DuckDuckGo"""
        try:
            search = DuckDuckGoSearchRun()
            result = search.run(query)
            return result
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _api_call(self, url: str) -> str:
        """Make API call to URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                return "Error: URL must start with http:// or https://"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Try to return JSON if available
            try:
                return str(response.json())[:1000]  # Limit response size
            except:
                return response.text[:1000]
        except Exception as e:
            return f"API call error: {str(e)}"
    
    def _calculator(self, expression: str) -> str:
        """Safe calculator evaluation"""
        try:
            # Only allow basic math operations
            allowed_chars = set('0123456789+-*/().= ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def chat_with_tools(self, message, user_id, chat_history=None, images: Optional[List[str]] = None):
        """
        Chat with tool calling and vision support
        
        Args:
            message: User message
            user_id: User ID
            chat_history: Previous chat history (list of dicts)
            images: List of image paths or base64 encoded images
            
        Returns:
            dict: Response with answer and tool calls
        """
        # Build conversation context
        context = ""
        if chat_history:
            for entry in chat_history[-5:]:  # Last 5 exchanges
                context += f"User: {entry.get('message', '')}\n"
                context += f"Assistant: {entry.get('response', '')}\n"
        
        # Prepare message content
        message_content = []
        
        # Add text
        if context:
            message_content.append({
                "type": "text",
                "text": f"Previous conversation:\n{context}\n\nCurrent question: {message}"
            })
        else:
            message_content.append({
                "type": "text",
                "text": message
            })
        
        # Add images if provided
        if images:
            for image in images:
                # Check if it's a file path or base64
                if os.path.exists(image):
                    # It's a file path
                    base64_image = self._encode_image(image)
                    # Determine image type from extension
                    ext = os.path.splitext(image)[1].lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(ext, 'image/jpeg')
                    
                    message_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    })
                else:
                    # Assume it's already base64 or URL
                    if image.startswith('http'):
                        message_content.append({
                            "type": "image_url",
                            "image_url": {"url": image}
                        })
                    else:
                        # Assume base64
                        message_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image}"
                            }
                        })
        
        # Track tools used
        tools_used = []
        tool_results = []
        
        try:
            # Create message
            human_message = HumanMessage(content=message_content)
            
            # Get initial response
            response = self.llm.invoke([human_message])
            initial_answer = response.content
            
            # Check if tools are mentioned in the text message
            if not images:  # Only use tools for text-only queries
                for tool_name, tool_info in self.tools.items():
                    if tool_name.lower() in message.lower():
                        # Extract potential input
                        if tool_name == "web_search" and "search" in message.lower():
                            result = tool_info['func'](message)
                            tool_results.append({
                                'tool': tool_name,
                                'input': message,
                                'result': result
                            })
                            tools_used.append(tool_name)
                        elif tool_name == "api_call" and ("http://" in message or "https://" in message):
                            words = message.split()
                            url = [w for w in words if w.startswith(('http://', 'https://'))][0]
                            result = tool_info['func'](url)
                            tool_results.append({
                                'tool': tool_name,
                                'input': url,
                                'result': result
                            })
                            tools_used.append(tool_name)
                
                # Generate final response with tool results
                if tool_results:
                    tool_context = "\n".join([
                        f"Tool: {tr['tool']}\nInput: {tr['input']}\nResult: {tr['result']}"
                        for tr in tool_results
                    ])
                    
                    final_prompt = f"""Based on the tool results, answer the user's question:
                    
                    User question: {message}
                    
                    Tool results:
                    {tool_context}
                    
                    Provide a comprehensive answer incorporating the tool results:"""
                    
                    final_response = self.llm.invoke(final_prompt)
                    answer = final_response.content
                else:
                    answer = initial_answer
            else:
                answer = initial_answer
            
        except Exception as e:
            answer = f"I encountered an error: {str(e)}"
            tool_results = []
        
        # Save chat history
        chat_entry = ChatHistory(
            user_id=user_id,
            message=message,
            response=answer,
            chat_type='tool',
            extra_metadata={
                'tools_used': tools_used,
                'has_images': bool(images),
                'num_images': len(images) if images else 0,
                'tool_results': [
                    {'tool': tr['tool'], 'input': tr['input'][:200]}
                    for tr in tool_results
                ]
            }
        )
        db.session.add(chat_entry)
        db.session.commit()
        
        return {
            'answer': answer,
            'tools_used': tools_used,
            'tool_results': tool_results,
            'has_images': bool(images)
        }
    
    def get_chat_history(self, user_id, chat_type=None, limit=50):
        """
        Get chat history for user
        
        Args:
            user_id: User ID
            chat_type: Filter by chat type (rag or tool)
            limit: Maximum number of records
            
        Returns:
            list: Chat history records
        """
        query = ChatHistory.query.filter_by(user_id=user_id)
        
        if chat_type:
            query = query.filter_by(chat_type=chat_type)
        
        history = query.order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        
        return [entry.to_dict() for entry in reversed(history)]
    
    def clear_chat_history(self, user_id, chat_type=None):
        """
        Clear chat history
        
        Args:
            user_id: User ID
            chat_type: Filter by chat type
            
        Returns:
            dict: Success message
        """
        query = ChatHistory.query.filter_by(user_id=user_id)
        
        if chat_type:
            query = query.filter_by(chat_type=chat_type)
        
        count = query.delete()
        db.session.commit()
        
        return {'message': f'Deleted {count} chat records'}
