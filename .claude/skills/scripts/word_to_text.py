#!/usr/bin/env python3
"""
Convert Microsoft Word (.docx) files to plain text.
Requires: python-docx library (install with: pip install python-docx)
"""

import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Error: python-docx library not found.")
    print("Install it with: pip install python-docx")
    sys.exit(1)


def word_to_text(docx_path, output_path=None):
    """
    Convert a Word document to plain text.

    Args:
        docx_path: Path to the .docx file
        output_path: Optional path for output text file. If None, prints to stdout.

    Returns:
        str: The extracted text content
    """
    try:
        # Load the Word document
        doc = Document(docx_path)

        # Extract text from all paragraphs
        text_content = []
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)

        # Join paragraphs with newlines
        full_text = '\n'.join(text_content)

        # Save or print the result
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"Text extracted and saved to: {output_path}")
        else:
            print(full_text)

        return full_text

    except Exception as e:
        print(f"Error processing Word file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python word_to_text.py <input.docx> [output.txt]")
        print("\nExamples:")
        print("  python word_to_text.py document.docx           # Print to console")
        print("  python word_to_text.py document.docx output.txt  # Save to file")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if not input_file.suffix.lower() == '.docx':
        print("Warning: File does not have .docx extension")

    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    word_to_text(input_file, output_file)


if __name__ == "__main__":
    main()
