# main.py
import argparse
import os
from document_processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="Process OCR'd Markdown with an LLM")
    parser.add_argument("--input", required=True, help="Input Markdown file path")
    parser.add_argument("--output", required=False, help="Output Markdown file path")
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions", help="LLM API base URL")
    parser.add_argument("--prompt-path", default="prompts.md", help="Path to the system prompt file")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    
    args = parser.parse_args()
    
    # If output path is not provided, create a default one in the same directory as input
    if args.output is None:
        input_dir = os.path.dirname(args.input)
        args.output = os.path.join(input_dir, "formatted.md")
        
    processor = DocumentProcessor(
        args.input,
        args.output,
        args.base_url,
        args.prompt_path,
        args.api_key,
        args.model
    )
    
    processor.process()

if __name__ == "__main__":
    main()
