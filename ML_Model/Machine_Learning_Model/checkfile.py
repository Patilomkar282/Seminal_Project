import sys
import os
import PyPDF2
from Ml_model import is_file_suspicious, is_content_suspicious

file_path = sys.argv[1]
# print(f"Checking file: {file_path}")
is_suspicious = False


if file_path.endswith('.pdf'):
    try:
        is_suspicious = is_file_suspicious(file_path)
    except Exception as e:
       
        print(f"An error occurred while processing the PDF: {e}")
        sys.stdout.write("True")  
else:
    try:
        # Handle non-PDF files
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        is_suspicious = is_content_suspicious(content)
    except UnicodeDecodeError as e:
        # Handle binary file read errors
        print(f"UnicodeDecodeError: {e} for file: {file_path}")
        sys.stdout.write("True")  # Consider suspicious if the file can't be decoded
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.stdout.write("True")  # Consider suspicious if any other error occurs

# Output result as True or False (use sys.stdout.write for clean output)
if is_suspicious:
    sys.stdout.write("True")
else:
    sys.stdout.write("False")
