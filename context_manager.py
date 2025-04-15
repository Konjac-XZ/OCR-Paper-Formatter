import tiktoken

class ContextManager:
    def __init__(self):
        self.assistant_messages = []
        self.user_previous_messages = []
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        
    def add_response(self, response):
        self.assistant_messages.append({
            "role": "assistant", 
            "content": response
        })
        
    def add_user_message(self, message):
        self.user_previous_messages.append({
            "role": "user", 
            "content": message
        })
        
    def get_assistant_messages(self):
        return self.assistant_messages
    
    def get_user_previous_messages(self):
        return self.user_previous_messages
    
    def _count_tokens(self, message):
        """Count the number of tokens in a message"""
        return len(self.tokenizer.encode(str(message)))
    
    def get_limited_user_messages(self, max_tokens):
        """Return the most recent user messages up to max_tokens"""
        messages = []
        token_count = 0
        
        # Process from newest to oldest
        for i in range(len(self.user_previous_messages) - 1, -1, -1):
            msg = self.user_previous_messages[i]
            msg_tokens = self._count_tokens(msg)
            
            if token_count + msg_tokens <= max_tokens:
                messages.insert(0, msg)  # Insert at beginning to maintain chronological order
                token_count += msg_tokens
            else:
                break
                
        return messages, token_count
    
    def get_limited_assistant_messages(self, max_tokens):
        """Return the most recent assistant messages up to max_tokens"""
        messages = []
        token_count = 0
        
        # Process from newest to oldest
        for i in range(len(self.assistant_messages) - 1, -1, -1):
            msg = self.assistant_messages[i]
            msg_tokens = self._count_tokens(msg)
            
            if token_count + msg_tokens <= max_tokens:
                messages.insert(0, msg)  # Insert at beginning to maintain chronological order
                token_count += msg_tokens
            else:
                break
                
        return messages, token_count
    
    def get_limited_combined_messages(self, max_tokens):
        """Return the most recent combined user and assistant messages up to max_tokens"""
        messages = []
        token_count = 0
        
        # Create a timeline of messages in chronological order
        timeline = []
        user_index = 0
        assistant_index = 0
        
        # Assuming user_previous_messages and assistant_messages are in chronological order
        # and generally alternate (user then assistant)
        while user_index < len(self.user_previous_messages) or assistant_index < len(self.assistant_messages):
            if user_index < len(self.user_previous_messages):
                timeline.append(("user", user_index))
                user_index += 1
                
            if assistant_index < len(self.assistant_messages):
                timeline.append(("assistant", assistant_index))
                assistant_index += 1
        
        # Process from newest to oldest
        for i in range(len(timeline) - 1, -1, -1):
            msg_type, idx = timeline[i]
            
            if msg_type == "user":
                msg = self.user_previous_messages[idx]
            else:
                msg = self.assistant_messages[idx]
                
            msg_tokens = self._count_tokens(msg)
            
            if token_count + msg_tokens <= max_tokens:
                messages.insert(0, msg)  # Insert at beginning to maintain chronological order
                token_count += msg_tokens
            else:
                break
                
        return messages, token_count
    
    def get_latest_conversation_pair(self):
        latest_message = []
        if self.user_previous_messages:
            latest_message.append(self.user_previous_messages[-1])
        if self.assistant_messages:
            latest_message.append(self.assistant_messages[-1])
        return latest_message


