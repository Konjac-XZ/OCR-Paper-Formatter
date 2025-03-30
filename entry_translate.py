# main.py
import argparse
from document_translator import DocumentTranslator

def main():
    parser = argparse.ArgumentParser(description="Process OCR'd Markdown with an LLM")
    parser.add_argument("--input", required=True, help="Input Markdown file path")
    parser.add_argument("--output", required=True, help="Output Markdown file path")
    parser.add_argument("--base-url", default="https://api.openai.com/v1/chat/completions", help="LLM API base URL")
    parser.add_argument("--prompt-path", default="prompts_translate.md", help="Path to the system prompt file")
    parser.add_argument("--api-key", required=True, help="LLM API key")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    
    args = parser.parse_args()
        
    processor = DocumentTranslator(
        args.input,
        args.output,
        args.base_url,
        args.prompt_path,
        args.api_key,
        args.model
    )
    
    processor.translate()

if __name__ == "__main__":
    main()
