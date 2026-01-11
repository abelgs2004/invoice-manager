
import requests
import os

URL = "http://127.0.0.1:8000/upload"
FILE_PATH = "bill_2.pdf"

if not os.path.exists(FILE_PATH):
    print(f"File {FILE_PATH} not found.")
    exit(1)

print(f"Uploading {FILE_PATH} to {URL}...")
try:
    with open(FILE_PATH, "rb") as f:
        files = {"file": f}
        response = requests.post(URL, files=files)
    
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
    print("Ensure the server is running on localhost:8000")
