# main.py
import argparse
import os
from document_processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="Process OCR'd Markdown with an LLM")
    parser.add_argument("--input", required=True, help="Input Markdown file path or directory containing complete.md")
    parser.add_argument("--output", required=False, help="Output Markdown file path")
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions", help="LLM API base URL")
    parser.add_argument("--prompt-path", default="prompts.md", help="Path to the system prompt file")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    
    args = parser.parse_args()
    
    # Check if input is a directory and look for complete.md
    input_path = args.input
    if os.path.isdir(input_path):
        complete_md_path = os.path.join(input_path, "complete.md")
        if os.path.isfile(complete_md_path):
            input_path = complete_md_path
        else:
            raise FileNotFoundError(f"Directory {input_path} does not contain a 'complete.md' file")
    elif not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist")
    
    # If output path is not provided, create a default one in the same directory as input
    if args.output is None:
        input_dir = os.path.dirname(input_path)
        args.output = os.path.join(input_dir, "formatted.md")
        
    processor = DocumentProcessor(
        input_path,  # Use the potentially updated input path
        args.output,
        args.base_url,
        args.prompt_path,
        args.api_key,
        args.model
    )
    
    processor.process()

if __name__ == "__main__":
    main()
