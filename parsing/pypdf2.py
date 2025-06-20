import os
import asyncio
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import GPT
import sys
sys.path.append(str(Path(__file__).parent.parent))
from llms.open_ai import GPT

# Initialize GPT client
gpt = GPT()

async def get_space_fact() -> str:
    """Get a random space fact using GPT."""
    try:
        fact = await gpt.call(
            system_prompt="You are a helpful assistant that provides interesting space facts.",
            user_prompt="Tell me a random interesting fact about space in one sentence.",
            max_tokens=100
        )
        return fact.strip()
    except Exception as e:
        print(f"Error getting space fact: {str(e)}")
        return "Could not fetch space fact."

async def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
    """Asynchronously extract text from a PDF file and get a space fact."""
    loop = asyncio.get_event_loop()
    
    def _extract():
        with open(pdf_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            return '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
    
    # Run PDF extraction and get space fact concurrently
    text, space_fact = await asyncio.gather(
        loop.run_in_executor(None, _extract),
        get_space_fact()
    )
    
    return {
        'text': text,
        'space_fact': space_fact
    }

async def process_pdf(pdf_file: Path) -> Dict[str, Any]:
    """Process a single PDF file asynchronously."""
    try:
        print(f"Processing: {pdf_file.name}")
        extracted = await extract_text_from_pdf(str(pdf_file))
        return {
            'filename': pdf_file.name,
            'text': extracted['text'],
            'space_fact': extracted['space_fact'],
            'status': 'success'
        }
    except Exception as e:
        return {
            'filename': pdf_file.name,
            'error': str(e),
            'status': 'error'
        }

async def process_pdfs_async(directory: str) -> List[Dict[str, Any]]:
    """Process all PDFs in the specified directory concurrently."""
    pdf_files = list(Path(directory).glob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files in {directory}")
    
    # Process all PDFs concurrently
    tasks = [process_pdf(pdf_file) for pdf_file in pdf_files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for result in results:
        if isinstance(result, Exception):
            print(f"Error in task: {str(result)}")
        elif result['status'] == 'error':
            print(f"Error processing {result['filename']}: {result['error']}")
    
    return results

async def main():
    """Main async function."""
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Meril-docs')
    results = await process_pdfs_async(docs_dir)
    success_results = [r for r in results if isinstance(r, dict) and r['status'] == 'success']
    print(f"\nProcessed {len(success_results)} files successfully")
    
    # Print a random space fact from one of the processed files
    if success_results:
        import random
        result = random.choice(success_results)
        print(f"\n🚀 Space Fact: {result.get('space_fact', 'No fact available')}")
    else:
        print("\nNo successful results to show a space fact.")

if __name__ == "__main__":
    asyncio.run(main())
            