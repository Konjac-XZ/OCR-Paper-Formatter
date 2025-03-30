from text_splitter import TextSplitter
from llm_client import LLMClient
from context_manager import ContextManager

class DocumentTranslator:
    def __init__(self, input_path, output_path, base_url, prompt_path, api_key, model="gpt-4o-mini"):
        self.input_path = input_path
        self.output_path = output_path
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize components
        self.text_splitter = TextSplitter(max_words=2000)
        self.llm_client = LLMClient(api_key, base_url, model)
        self.context_manager = ContextManager()
        
        # Load prompt
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
        
    def translate(self):
        """Translate the entire document in chunks"""
        # Read input document
        with open(self.input_path, 'r', encoding='utf-8') as f:
            document = f.read()
        
        print(f"Starting document translation of '{self.input_path}'...")
        
        # Split document into chunks
        chunks = self.text_splitter.split_document(document)
        print(f"Document split into {len(chunks)} chunks")
        
        # Store original chunks for context
        source_chunks = []
        
        # Process each chunk
        with open(self.output_path, 'w', encoding='utf-8') as output_file:
            for i, chunk in enumerate(chunks, 1):
                print(f"Translating chunk {i}/{len(chunks)}...")
                
                # Add current chunk to source chunks for context
                source_chunks.append(chunk)
                
                # Process chunk with source context
                response = self.llm_client.process_with_all_context(
                    self.system_prompt,
                    self.context_manager,
                    chunk,
                    max_tokens=20000
                )
                    
                # Add response to context for next iteration
                self.context_manager.add_response(response)
                self.context_manager.add_user_message(chunk)
                
                # Write to output file
                output_file.write(response)
                output_file.write("\n\n")
                
                print(f"✓ Chunk {i}/{len(chunks)} translated successfully")
        
        print(f"Translation complete. Output saved to {self.output_path}")
