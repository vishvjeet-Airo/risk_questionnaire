

from typing import Optional, Dict, Any, List
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
import os

# Set AWS bearer token for Bedrock if it's configured
if settings.aws_bearer_token_bedrock:
    os.environ['AWS_BEARER_TOKEN_BEDROCK'] = settings.aws_bearer_token_bedrock
    print("✓ AWS Bearer token configured for Bedrock")
else:
    print("⚠ AWS Bearer token not set - using default AWS credentials")

# Langfuse imports
try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    print(f"Warning: Failed to import Langfuse: {e}")
    print("Install with: pip install langfuse")


class TracedBedrockClient:
    """
    A simple wrapper around LangChain's ChatBedrock that provides cost monitoring.
    LangSmith tracing is handled automatically by LangChain when environment variables are set.
    Langfuse tracing is also supported for additional observability.
    """
    
    def __init__(self):
        self.client = ChatBedrock(
            model_id=settings.bedrock_model_id,
            region_name=settings.aws_region,
            streaming=False,
            max_tokens=10000
        )
        
        # Initialize embedding client
        self.embedding_client = BedrockEmbeddings(
            model_id=settings.bedrock_embedding_model_id,
            region_name=settings.aws_region
        )

        # Initialize Langfuse client if available
        self.langfuse_client = None
        self.langfuse_callback = None
        
        if LANGFUSE_AVAILABLE:
            try:
                # Check if Langfuse configuration is available
                if settings.langfuse_secret_key and settings.langfuse_public_key:
                    langfuse = Langfuse(
                        secret_key=settings.langfuse_secret_key,
                        public_key=settings.langfuse_public_key,
                        host=settings.langfuse_host
                    )
                    self.langfuse_client = langfuse
                    self.langfuse_callback = CallbackHandler(
                        public_key=settings.langfuse_public_key,
                        secret_key=settings.langfuse_secret_key,
                        host=settings.langfuse_host
                    )
                    if langfuse.auth_check():
                        print("Langfuse authentication successful")
                    else:
                        print("Langfuse authentication failed")
                else:
                    print("Warning: Langfuse credentials not set. Configure langfuse_secret_key and langfuse_public_key in settings")
            except Exception as e:
                print(f"Warning: Failed to initialize Langfuse: {e}")
                self.langfuse_client = None
                self.langfuse_callback = None
    
    def invoke_with_tracing(
        self, 
        prompt: str, 
        system_message: Optional[str] = None
    ) -> str:
        """
        Invoke the Bedrock model with both LangSmith and Langfuse tracing.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            metadata: Optional metadata for tracing
            trace_name: Optional name for the trace (for Langfuse)
            session_id: Optional session ID for grouping traces
            
        Returns:
            The model response as a string
        """
        # Prepare messages
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))
        
        # Start Langfuse trace if available
        # langfuse_trace = None
        # if self.langfuse_client and trace_name:
        #     try:
        #         langfuse_trace = self.langfuse_client(
        #             name=trace_name,
        #             session_id=session_id,
        #             metadata=metadata or {}
        #         )
        #     except Exception as e:
        #         print(f"Warning: Failed to start Langfuse trace: {e}")
        
        try:
            # Invoke with Langfuse callback if available
                 
            if self.langfuse_callback:
                self.langfuse_callback.flush()
                # Use Langfuse callback for automatic tracing
                response = self.client.invoke(messages, config={"callbacks": [self.langfuse_callback]})
            else:
                # Standard invoke - LangChain handles LangSmith tracing automatically
                response = self.client.invoke(messages)
            
            return response.content
            
        except Exception as e:
            print(f"Warning: Failed to log error to Langfuse: {e}")
            raise e
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for a single text string.
        
        Args:
            text: The text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        try:
            embedding = self.embedding_client.embed_query(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise e
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple text strings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        try:
            embeddings = self.embedding_client.embed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise e
    
    def embed_with_tracing(
        self, 
        text: str, 
        trace_name: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """
        Generate embeddings with Langfuse tracing support.
        
        Args:
            text: The text to embed
            trace_name: Optional name for the trace
            session_id: Optional session ID for grouping traces
            metadata: Optional metadata for tracing
            
        Returns:
            List of float values representing the embedding vector
        """
        try:
            # Start Langfuse trace if available
            langfuse_trace = None
            if self.langfuse_client and trace_name:
                try:
                    langfuse_trace = self.langfuse_client.trace(
                        name=trace_name,
                        session_id=session_id,
                        metadata=metadata or {}
                    )
                except Exception as e:
                    print(f"Warning: Failed to start Langfuse trace: {e}")
            
            # Generate embedding
            embedding = self.embed_text(text)
            
            # Log to Langfuse trace if available
            if langfuse_trace:
                try:
                    langfuse_trace.generation(
                        name="embedding_generation",
                        input=text,
                        output=embedding,
                        metadata={"embedding_model": settings.bedrock_embedding_model_id}
                    )
                except Exception as e:
                    print(f"Warning: Failed to log embedding to Langfuse: {e}")
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding with tracing: {e}")
            raise e
    
    def create_trace(self, name: str, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Create a Langfuse trace for manual tracing.
        
        Args:
            name: Name of the trace
            session_id: Optional session ID for grouping traces
            metadata: Optional metadata for the trace
            
        Returns:
            Langfuse trace object or None if not available
        """
        if self.langfuse_client:
            try:
                return self.langfuse_client.trace(
                    name=name,
                    session_id=session_id,
                    metadata=metadata or {}
                )
            except Exception as e:
                print(f"Warning: Failed to create Langfuse trace: {e}")
        return None
    
    def flush_langfuse(self):
        """
        Flush pending Langfuse events to ensure they are sent.
        """
        if self.langfuse_client:
            try:
                self.langfuse_client.flush()
            except Exception as e:
                print(f"Warning: Failed to flush Langfuse events: {e}")
    
    

# Global instance
bedrock_client = TracedBedrockClient()

# Example usage:
# 
# # Basic chat usage (LangSmith tracing only, if env vars are set)
# response = bedrock_client.invoke_with_tracing("Hello, world!")
# 
# # Chat with Langfuse tracing
# response = bedrock_client.invoke_with_tracing(
#     prompt="Hello, world!",
#     system_message="You are a helpful assistant.",
#     trace_name="my_conversation",
#     session_id="user_123",
#     metadata={"user_id": "123", "feature": "chat"}
# )
# 
# # Basic embedding usage
# embedding = bedrock_client.embed_text("This is a sample text to embed")
# 
# # Embed multiple texts
# texts = ["First text", "Second text", "Third text"]
# embeddings = bedrock_client.embed_texts(texts)
# 
# # Embedding with Langfuse tracing
# embedding = bedrock_client.embed_with_tracing(
#     text="This is a sample text to embed",
#     trace_name="embedding_generation",
#     session_id="user_123",
#     metadata={"user_id": "123", "feature": "embeddings"}
# )
# 
# # Manual trace creation
# trace = bedrock_client.create_trace("manual_trace", session_id="session_1")
# if trace:
#     trace.generation(name="custom_generation", input="test", output="result")
#     trace.update(output="final_result")
# 
# # Flush events to ensure they're sent
# bedrock_client.flush_langfuse()
