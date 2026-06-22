---
name: word-to-text
description: Convert Microsoft Word (.docx) files to plain text and save in Raw Data folder
trigger_phrases:
  - convert word to text
  - convert docx to text
  - extract text from word
  - word to text
---

# Word to Text Converter

This skill converts Microsoft Word (.docx) files to plain text format and saves the output in the `Raw Data` folder.

## Instructions

When this skill is invoked:

1. Ask the user to provide the path to the Word document (.docx file) they want to convert
2. Extract the filename (without extension) from the input path to use for the output text file
3. Define the output path as `Raw Data/<filename>.txt` where `<filename>` is the base name of the input file
4. Run the conversion script using: `python .claude/skills/scripts/word_to_text.py "<input_path>" "<output_path>"`
5. Verify the output file was created successfully in the Raw Data folder
6. Report the results to the user, including the output file location

## Prerequisites

Ensure the `python-docx` library is installed. If not, instruct the user to run:
```bash
pip install python-docx
```

## Example Usage

User: "Convert my document.docx to text"

Steps:
1. Confirm the input file path
2. Run: `python .claude/skills/scripts/word_to_text.py "document.docx" "Raw Data/document.txt"`
3. Verify and report success

## Error Handling

- If the input file doesn't exist, report the error to the user
- If python-docx is not installed, provide installation instructions
- If the Raw Data folder doesn't exist, create it before running the conversion
