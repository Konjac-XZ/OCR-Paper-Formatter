# main.py
import argparse
import os
from document_translator import DocumentTranslator

def main():
    parser = argparse.ArgumentParser(description="Process OCR'd Markdown with an LLM")
    parser.add_argument("--input", required=True, help="Input Markdown file path or directory containing formatted.md")
    parser.add_argument("--output", required=False, help="Output Markdown file path (optional, defaults to 'translated.md' in input directory)")
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions", help="LLM API base URL")
    parser.add_argument("--prompt-path", default="prompts_translate.md", help="Path to the system prompt file")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    
    args = parser.parse_args()
    
    # Check if input is a directory and look for formatted.md
    input_path = args.input
    if os.path.isdir(input_path):
        formatted_md_path = os.path.join(input_path, "formatted.md")
        if os.path.isfile(formatted_md_path):
            input_path = formatted_md_path
        else:
            raise FileNotFoundError(f"Directory {input_path} does not contain a 'formatted.md' file")
    elif not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist")
    
    # Determine output path if not provided
    if args.output is None:
        input_dir = os.path.dirname(input_path)
        args.output = os.path.join(input_dir, "translated.md")
        
    processor = DocumentTranslator(
        input_path,  # Use the potentially updated input path
        args.output,
        args.base_url,
        args.prompt_path,
        args.api_key,
        args.model
    )
    
    processor.translate()

if __name__ == "__main__":
    main()
