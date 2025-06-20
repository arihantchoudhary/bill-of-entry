import os
import PyPDF2
from pathlib import Path
from typing import List, Dict, Optional

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text_parts = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Only add non-empty text
                text_parts.append(page_text)
                
        return '\n'.join(text_parts)

def process_meril_docs(directory: str) -> List[Dict]:
    """Process all PDF files in the specified directory.
    
    Args:
        directory: Path to the directory containing MERIL PDFs
        
    Returns:
        List[Dict]: List of dictionaries containing file info and extracted text
    """
    results = []
    
    # Convert to Path object for easier handling
    dir_path = Path(directory)
    
    # Check if directory exists
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is not a directory")
        return results
    
    # Get all PDF files in the directory
    pdf_files = list(dir_path.glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in '{directory}'")
        return results
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            print(f"Processing file: {pdf_file.name}")
            text = extract_text_from_pdf(str(pdf_file))
            
            # Store results
            results.append({
                'filename': pdf_file.name,
                'filepath': str(pdf_file),
                'text': text,
                'page_count': len(PyPDF2.PdfReader(str(pdf_file)).pages)
            })
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
    
    return results

def main():
    # Path to the Meril-docs directory (one level up from current directory)
    meril_docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Meril-docs')
    
    print(f"Looking for MERIL documents in: {meril_docs_dir}")
    
    # Process all PDFs in the Meril-docs directory
    results = process_meril_docs(meril_docs_dir)
    
    # Print summary
    print("\nProcessing complete!")
    print(f"Successfully processed {len(results)} PDF files.")
    
    # # Print first 500 characters of each file's text
    # for i, result in enumerate(results, 1):
    #     print(f"\n--- {i}. {result['filename']} (Pages: {result['page_count']}) ---")
    #     print(result['text'][:500] + ("..." if len(result['text']) > 500 else ""))

if __name__ == "__main__":
    main()
            