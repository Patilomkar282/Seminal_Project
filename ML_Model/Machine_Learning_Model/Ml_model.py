import os
import re
import PyPDF2
import string
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


# Check if the content contains suspicious keywords or patterns
def is_content_suspicious(content):
    SUSPICIOUS_KEYWORDS = [
        "malware", "virus", "phishing", "hack", "exploit", "ransomware",
        "http://", "https://", "ftp://", "alert", "unauthorized"
    ]
    
    SUSPICIOUS_PATTERNS = [
        r"\.exe", r"\.bat", r"\.cmd", r"\.sh", r"\.js", r"\.py"
    ]

    # Check for suspicious keywords
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.lower() in content.lower():
            return True  # Suspicious content detected

    # Check for suspicious patterns using regular expressions
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True  # Suspicious content detected

    return False  # No suspicious content found



def train_model():
    
    file_contents = [
        "This is a normal file.", 
        "Some safe content.", 
        "alert('malicious code');",
        "DROP TABLE users;",
        "virus detected in system."
    ]
    labels = [0, 0, 1, 1, 1]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(file_contents)
    
    model = RandomForestClassifier()
    model.fit(X, labels)

    # Save the model and vectorizer
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')

# Predict whether a file is suspicious based on content
def is_file_suspicious(file_path):
    global model, vectorizer
    if file_path.endswith('.pdf'):
        return check_pdf_for_suspicious_content(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for suspicious keywords and patterns in text files
            if is_content_suspicious(content):
                return True
            
            # Transform the content and make a prediction
            content_vector = vectorizer.transform([content])
            prediction = model.predict(content_vector)

            return prediction[0] == 1  # Return True if suspicious (1)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError: {e} for file: {file_path}")
            return True  # Consider the file suspicious if it can't be read
        except Exception as e:
            print(f"An error occurred: {e}")
            return True  # Handle any other errors as needed

# Check PDF for suspicious content
def check_pdf_for_suspicious_content(pdf_path):
    global model, vectorizer
    try:
        with open(pdf_path, 'rb') as file:  # Open PDF file in binary mode
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Loop through all pages to extract text
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text
            
            if not text:
                # If no text could be extracted, consider suspicious
                print(f"No text extracted from PDF: {pdf_path}")
                return True  # Suspicious file due to no text
            
            # Check for suspicious keywords and patterns in the extracted text
            if is_content_suspicious(text):
                return True  # Suspicious content detected
            
            # If no keywords or patterns, predict using the trained model
            content_vector = vectorizer.transform([text])
            prediction = model.predict(content_vector)

            return prediction[0] == 1  # Return True if prediction says suspicious (1)

    except Exception as e:
        # Handle any errors during PDF processing
        print(f"An error occurred while reading the PDF: {e}")
        return True  # Consider suspicious if there was an error



if __name__ == '__main__':
    if not os.path.exists('model.pkl'):
        print("Training the model...")
        train_model()

    # Load the model and vectorizer once
    model = joblib.load('model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')

    # # Test the model on a file (replace with actual file path)
    # file_to_check = 'C://Users//Omkar Patil//Desktop//mahek.txt'  # Example file path
    # if is_file_suspicious(file_to_check):
    #     print("The file is suspicious.")
    # else:
    #     print("The file is safe.")
