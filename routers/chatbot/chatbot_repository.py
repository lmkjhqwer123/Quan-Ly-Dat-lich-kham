"""
Chatbot Repository Layer - Handles all CHAT_CONVERSATIONS and CHAT_MESSAGES database operations
"""
import pyodbc
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)


class ChatbotRepository:
    """Repository class for managing chatbot conversations and messages"""
    
    def __init__(self):
        """Initialize repository with database connection config"""
        self.db_config = DB_CONFIG
    
    def _get_connection(self):
        """
        Create and return a new database connection
        
        Returns:
            pyodbc.Connection: Database connection with proper encoding
        """
        try:
            conn_str = (
                f'Driver={{{self.db_config["driver"]}}};'
                f'Server={self.db_config["server"]};'
                f'Database={self.db_config["database"]};'
                f'Trusted_Connection=yes;'
            )
            conn = pyodbc.connect(conn_str)
            # Set encoding for Vietnamese character support
            conn.setdecoding(pyodbc.SQL_WCHAR, 'utf-16-le')
            conn.setdecoding(pyodbc.SQL_CHAR, 'utf-8')
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def save_conversation(self, patient_id: Optional[int] = None, 
                         session_id: Optional[str] = None) -> Optional[int]:
        """
        Create a new chat conversation
        
        Args:
            patient_id: Patient ID (optional, for logged-in patients)
            session_id: Unique session identifier (optional)
        
        Returns:
            int: conversation_id if successful, None if failed
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate session_id if not provided
            if not session_id:
                from uuid import uuid4
                session_id = str(uuid4())
            
            # INSERT into CHAT_CONVERSATIONS
            query = """
            INSERT INTO CHAT_CONVERSATIONS (patient_id, session_id, status, created_at, ended_at, recommended_specialty_id)
            VALUES (?, ?, ?, GETDATE(), NULL, NULL)
            """
            
            cursor.execute(query, (patient_id, session_id, 'active'))
            conn.commit()
            
            # Get the inserted conversation_id
            cursor.execute("SELECT @@IDENTITY AS id")
            result = cursor.fetchone()
            conversation_id = result[0] if result else None
            
            logger.info(f"Conversation created: ID={conversation_id}, Session={session_id}")
            cursor.close()
            conn.close()
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return None
    
    def save_message(self, conversation_id: int, sender_type: str, 
                    message_text: str, tool_used: Optional[str] = None, 
                    tool_response: Optional[str] = None) -> Optional[int]:
        """
        Save a message to the conversation
        
        Args:
            conversation_id: ID of the conversation
            sender_type: 'user' or 'bot'
            message_text: The message content
            tool_used: Name of tool used (if any)
            tool_response: Tool response/result (if any)
        
        Returns:
            int: message_id if successful, None if failed
        """
        try:
            # Validate sender_type
            if sender_type not in ['user', 'bot']:
                logger.warning(f"Invalid sender_type: {sender_type}. Must be 'user' or 'bot'")
                return None
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # INSERT into CHAT_MESSAGES
            query = """
            INSERT INTO CHAT_MESSAGES 
            (conversation_id, sender_type, message_text, tool_used, tool_response, created_at)
            VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            
            cursor.execute(query, (
                conversation_id, 
                sender_type, 
                message_text, 
                tool_used, 
                tool_response
            ))
            conn.commit()
            
            # Get the inserted message_id
            cursor.execute("SELECT @@IDENTITY AS id")
            result = cursor.fetchone()
            message_id = result[0] if result else None
            
            logger.info(f"Message saved: ID={message_id}, Conversation={conversation_id}")
            cursor.close()
            conn.close()
            
            return message_id
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None
    
    def get_conversation_messages(self, conversation_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve all messages from a conversation
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            List of message dictionaries with keys:
            - message_id, conversation_id, sender_type, message_text, 
              tool_used, tool_response, created_at
            Returns None if error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                message_id, conversation_id, sender_type, message_text, 
                tool_used, tool_response, created_at
            FROM CHAT_MESSAGES
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """
            
            cursor.execute(query, (conversation_id,))
            columns = [column[0] for column in cursor.description]
            messages = []
            
            for row in cursor.fetchall():
                message = dict(zip(columns, row))
                messages.append(message)
            
            logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            cursor.close()
            conn.close()
            
            return messages if messages else []
            
        except Exception as e:
            logger.error(f"Error retrieving conversation messages: {str(e)}")
            return None
    
    def update_conversation_status(self, conversation_id: int, 
                                  status: str, 
                                  recommended_specialty_id: Optional[int] = None) -> bool:
        """
        Update conversation status and optionally set recommended specialty
        
        Args:
            conversation_id: ID of the conversation
            status: New status ('active', 'closed', 'archived')
            recommended_specialty_id: ID of recommended specialty (optional)
        
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Validate status
            if status not in ['active', 'closed', 'archived']:
                logger.warning(f"Invalid status: {status}")
                return False
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if status == 'closed':
                # Include ended_at timestamp when closing
                query = """
                UPDATE CHAT_CONVERSATIONS
                SET status = ?, ended_at = GETDATE(), recommended_specialty_id = ?
                WHERE conversation_id = ?
                """
                cursor.execute(query, (status, recommended_specialty_id, conversation_id))
            else:
                # For other status updates
                query = """
                UPDATE CHAT_CONVERSATIONS
                SET status = ?, recommended_specialty_id = ?
                WHERE conversation_id = ?
                """
                cursor.execute(query, (status, recommended_specialty_id, conversation_id))
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            if rows_affected > 0:
                logger.info(f"Conversation {conversation_id} status updated to '{status}'")
                cursor.close()
                conn.close()
                return True
            else:
                logger.warning(f"No conversation found with ID {conversation_id}")
                cursor.close()
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Error updating conversation status: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single conversation by ID
        
        Args:
            conversation_id: ID of the conversation
        
        Returns:
            Dictionary with conversation details, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                conversation_id, patient_id, session_id, status, 
                created_at, ended_at, recommended_specialty_id
            FROM CHAT_CONVERSATIONS
            WHERE conversation_id = ?
            """
            
            cursor.execute(query, (conversation_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                conversation = dict(zip(columns, row))
                logger.info(f"Retrieved conversation {conversation_id}")
            else:
                conversation = None
                logger.warning(f"Conversation {conversation_id} not found")
            
            cursor.close()
            conn.close()
            return conversation
            
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return None
    
    def get_patient_conversations(self, patient_id: int, 
                                 limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve all conversations for a patient
        
        Args:
            patient_id: ID of the patient
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversation dictionaries, or None if error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = f"""
            SELECT TOP {limit}
                conversation_id, patient_id, session_id, status, 
                created_at, ended_at, recommended_specialty_id
            FROM CHAT_CONVERSATIONS
            WHERE patient_id = ?
            ORDER BY created_at DESC
            """
            
            cursor.execute(query, (patient_id,))
            columns = [column[0] for column in cursor.description]
            conversations = []
            
            for row in cursor.fetchall():
                conversation = dict(zip(columns, row))
                conversations.append(conversation)
            
            logger.info(f"Retrieved {len(conversations)} conversations for patient {patient_id}")
            cursor.close()
            conn.close()
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error retrieving patient conversations: {str(e)}")
            return None


# Create a singleton instance for easy import
chatbot_repository = ChatbotRepository()
