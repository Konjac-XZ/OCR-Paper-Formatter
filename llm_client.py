import http.client
import json
from urllib.parse import urlparse
import tiktoken
import time  # Added for retry delays

class LLMClient:
    def __init__(self, api_key, base_url, model="gpt-4o-mini"):
        parsed_url = urlparse(base_url)
        self.hostname = parsed_url.netloc.split(':')[0]
        self.port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

        self.base_url = base_url
        self.api_key = api_key
        self.tokenzier = tiktoken.encoding_for_model("gpt-4o")
        self.model = model
        
    def _send_request(self, messages, status_callback, max_retries=500, initial_delay=1):
        """Send a request to the LLM API
        
        Args:
            messages: List of message objects to send to the API
            status_callback: Callback function for status updates
            max_retries: Maximum number of retry attempts on failure
            initial_delay: Initial delay in seconds between retries (will increase exponentially)
        
        Returns:
            The response content from the API
        """
        status_callback(f"Preparing request with {len(messages)} messages...")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 8192,
            "top_p": 0.8,
            "temperature": 0.2        
        }
        
        header = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json'
        }
        
        retry_count = 0
        delay = initial_delay

        while True:
            if retry_count > 0:
                status_callback(f"Retry attempt {retry_count}/{max_retries} after {delay:.1f}s delay...")
                time.sleep(delay)
                # Exponential backoff: double the delay for the next retry
                delay *= 2
            
            status_callback(f"Sending request to {self.hostname}...")
            
            conn = http.client.HTTPSConnection(self.hostname, self.port)
            
            try:
                conn.request("POST", "/v1/chat/completions", json.dumps(payload), header)
                status_callback("Waiting for response...")
                response = conn.getresponse()
                
                if response.status == 200:
                    status_callback("Response received, processing data...")
                    data = json.loads(response.read().decode())
                    result = data['choices'][0]['message']['content']
                    status_callback("Processing completed successfully.")
                    return result
                else:
                    error_msg = f"API request failed with status {response.status}: {response.read().decode()}"
                    status_callback(error_msg, True)
                    
                    # If we've reached max retries, return the error
                    if retry_count >= max_retries:
                        return error_msg
                    
                    # Otherwise, increment retry count and try again
                    retry_count += 1
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                status_callback(error_msg, True)
                
                # If we've reached max retries, return the error
                if retry_count >= max_retries:
                    return f"Error occurred after {max_retries} retries: {str(e)}"
                
                # Otherwise, increment retry count and try again
                retry_count += 1
                
            finally:
                conn.close()
    
    def _count_tokens(self, message):
        """Count the number of tokens in a message"""
        return len(self.tokenzier.encode(str(message)))
    
    def process_with_all_context(self, system_prompt, context_manager, current_user_message, 
                                 max_tokens=20000, status_callback=None):
        """Process a user message with the LLM using both user and assistant messages as context
        up to a certain token count threshold.
        
        Args:
            system_prompt: The system prompt to guide the LLM
            context_manager: ContextManager instance with message history
            current_user_message: The current user message to process
            max_tokens: Maximum number of tokens to include in context (default: 20000)
            status_callback: Optional callback function for status updates
        """
        if status_callback is None:
            # Default status callback just prints to console
            status_callback = lambda msg, is_error=False: print(f"{'ERROR: ' if is_error else 'STATUS: '}{msg}")
            
        status_callback("Starting processing request with combined user and assistant context...")
        
        # Initialize messages with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Current user message
        current_message = {"role": "user", "content": current_user_message}
        
        # Calculate tokens used by system prompt and current message
        system_tokens = self._count_tokens({"content": system_prompt})
        current_message_tokens = self._count_tokens(current_message)
        
        # Calculate remaining tokens for context
        remaining_tokens = max_tokens - system_tokens - current_message_tokens
        
        if remaining_tokens > 0:
            # Get limited context from context manager
            context_messages, context_tokens = context_manager.get_limited_combined_messages(remaining_tokens)
            
            # Add context messages
            messages.extend(context_messages)
            
            status_callback(f"Added {len(context_messages)} context messages using {context_tokens} tokens.")
        
        # Add current user message
        messages.append(current_message)
        
        status_callback(f"Built context with {len(messages)} messages.")
        
        return self._send_request(messages, status_callback)
    
    def process_with_context_of_assistant(self, system_prompt, context_manager, current_user_message, 
                                          max_tokens=20000, status_callback=None):
        """Process a user message with the LLM and assistant messages as context
        
        Args:
            system_prompt: The system prompt to guide the LLM
            context_manager: ContextManager instance with message history
            current_user_message: The current user message to process
            max_tokens: Maximum number of tokens for context
            status_callback: Optional callback function for status updates
        """
        if status_callback is None:
            # Default status callback just prints to console
            status_callback = lambda msg, is_error=False: print(f"{'ERROR: ' if is_error else 'STATUS: '}{msg}")
            
        status_callback("Starting processing request with assistant context...")
        
        # Initialize messages with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Current user message
        current_message = {"role": "user", "content": current_user_message}
        
        # Calculate tokens used by system prompt and current message
        system_tokens = self._count_tokens({"content": system_prompt})
        current_message_tokens = self._count_tokens(current_message)
        
        # Calculate remaining tokens for context
        remaining_tokens = max_tokens - system_tokens - current_message_tokens
        
        if remaining_tokens > 0:
            # Get limited assistant messages from context manager
            assistant_messages, assistant_tokens = context_manager.get_limited_assistant_messages(remaining_tokens)
            
            # Add assistant messages
            messages.extend(assistant_messages)
            
            status_callback(f"Added {len(assistant_messages)} assistant messages using {assistant_tokens} tokens.")
        
        # Add current user message
        messages.append(current_message)
        
        status_callback(f"Built context with {len(messages)} messages.")
        
        return self._send_request(messages, status_callback)
    
    def process_with_context_of_user(self, system_prompt, context_manager, current_user_message, 
                                     max_tokens=20000, status_callback=None):
        """Process a user message with the LLM and previous user messages as context
        
        Args:
            system_prompt: The system prompt to guide the LLM
            context_manager: ContextManager instance with message history
            current_user_message: The current user message to process
            max_tokens: Maximum number of tokens for context
            status_callback: Optional callback function for status updates
        """
        if status_callback is None:
            # Default status callback just prints to console
            status_callback = lambda msg, is_error=False: print(f"{'ERROR: ' if is_error else 'STATUS: '}{msg}")
            
        status_callback("Starting processing request with user context...")
        
        # Initialize messages with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Current user message
        current_message = {"role": "user", "content": current_user_message}
        
        # Calculate tokens used by system prompt and current message
        system_tokens = self._count_tokens({"content": system_prompt})
        current_message_tokens = self._count_tokens(current_message)
        
        # Calculate remaining tokens for context
        remaining_tokens = max_tokens - system_tokens - current_message_tokens
        
        if remaining_tokens > 0:
            # Get limited user messages from context manager
            user_messages, user_tokens = context_manager.get_limited_user_messages(remaining_tokens)
            
            # Add user messages
            messages.extend(user_messages)
            
            status_callback(f"Added {len(user_messages)} user messages using {user_tokens} tokens.")
        
        # Add current user message
        messages.append(current_message)
        
        status_callback(f"Built context with {len(messages)} messages.")
        
        return self._send_request(messages, status_callback)
    
    def process_with_latest_context(self, system_prompt, context_manager, current_user_message,
                                   max_tokens=20000, status_callback=None):
        """Process a user message with the LLM using only the most recent user-assistant conversation pair
        
        Args:
            system_prompt: The system prompt to guide the LLM
            context_manager: ContextManager instance with message history
            current_user_message: The current user message to process
            max_tokens: Maximum number of tokens for context
            status_callback: Optional callback function for status updates
        """
        if status_callback is None:
            # Default status callback just prints to console
            status_callback = lambda msg, is_error=False: print(f"{'ERROR: ' if is_error else 'STATUS: '}{msg}")
            
        status_callback("Starting processing request with latest conversation context...")
        
        # Initialize messages with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Current user message
        current_message = {"role": "user", "content": current_user_message}
        
        # Calculate tokens used by system prompt and current message
        system_tokens = self._count_tokens({"content": system_prompt})
        current_message_tokens = self._count_tokens(current_message)
        
        # Calculate remaining tokens for context
        remaining_tokens = max_tokens - system_tokens - current_message_tokens
        
        if remaining_tokens > 0:
            # Get latest conversation pair from context manager
            latest_messages = context_manager.get_latest_conversation_pair()
            latest_tokens = sum(self._count_tokens(msg) for msg in latest_messages)
            
            # Add latest conversation messages
            messages.extend(latest_messages)
            
            status_callback(f"Added {len(latest_messages)} latest conversation messages using {latest_tokens} tokens.")
        
        # Add current user message
        messages.append(current_message)
        
        status_callback(f"Built context with {len(messages)} messages.")
        
        return self._send_request(messages, status_callback)
