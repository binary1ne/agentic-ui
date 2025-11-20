from typing import TypedDict, Annotated, Sequence
import operator
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END

from models import db, ChatHistory
from services.auth_service import AuthService
from config import Config

class ChatService:
    """LangGraph tool calling chat service with React agent"""
    
    def __init__(self):
        """Initialize chat service"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError('Google API key not configured')
        
        # Initialize Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize tools
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize available tools"""
        tools = []
        
        # Web search tool
        search_tool = Tool(
            name="web_search",
            func=self._web_search,
            description="Search the internet for current information. Use this when you need up-to-date information or facts not in your knowledge. Input should be a search query string."
        )
        tools.append(search_tool)
        
        # Custom API call tool
        api_tool = Tool(
            name="api_call",
            func=self._api_call,
            description="Make HTTP GET request to a URL. Input should be a valid URL string. Returns the response content."
        )
        tools.append(api_tool)
        
        # Calculator tool
        calc_tool = Tool(
            name="calculator",
            func=self._calculator,
            description="Perform mathematical calculations. Input should be a mathematical expression as a string (e.g., '2 + 2', '10 * 5')."
        )
        tools.append(calc_tool)
        
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
    
    def chat_with_tools(self, message, user_id, chat_history=None):
        """
        Chat with tool calling using LangGraph
        
        Args:
            message: User message
            user_id: User ID
            chat_history: Previous chat history (list of dicts)
            
        Returns:
            dict: Response with answer and tool calls
        """
        # Build conversation context
        context = ""
        if chat_history:
            for entry in chat_history[-5:]:  # Last 5 exchanges
                context += f"User: {entry.get('message', '')}\n"
                context += f"Assistant: {entry.get('response', '')}\n"
        
        # Create prompt with context
        prompt_template = """You are a helpful AI assistant with access to tools. Answer the user's question using the available tools when necessary.

Previous conversation:
{context}

Current question: {message}

Think step by step:
1. Do I need to use any tools to answer this question?
2. What information do I already have?
3. What's the best way to answer?

Available tools:
{tools}

Provide a helpful, accurate response."""
        
        tools_description = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        
        full_prompt = prompt_template.format(
            context=context,
            message=message,
            tools=tools_description
        )
        
        # Track tools used
        tools_used = []
        
        # Simple tool calling logic with LLM
        # First, ask LLM if it needs tools
        decision_prompt = f"""{full_prompt}

First, decide if you need to use any tools. Respond with JSON format:
{{"needs_tools": true/false, "tool_name": "tool_name_if_needed", "tool_input": "input_if_needed"}}"""
        
        try:
            # Get initial response
            response = self.llm.invoke(decision_prompt)
            initial_answer = response.content
            
            # Check if tools are mentioned in response
            tool_results = []
            for tool in self.tools:
                if tool.name.lower() in message.lower():
                    # Extract potential input
                    if tool.name == "web_search" and "search" in message.lower():
                        # Use the message as search query
                        result = tool.func(message)
                        tool_results.append({
                            'tool': tool.name,
                            'input': message,
                            'result': result
                        })
                        tools_used.append(tool.name)
                    elif tool.name == "api_call" and ("http://" in message or "https://" in message):
                        # Extract URL
                        words = message.split()
                        url = [w for w in words if w.startswith(('http://', 'https://'))][0]
                        result = tool.func(url)
                        tool_results.append({
                            'tool': tool.name,
                            'input': url,
                            'result': result
                        })
                        tools_used.append(tool.name)
            
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
            'tool_results': tool_results
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
