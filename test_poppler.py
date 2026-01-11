
try:
    from pdf2image import convert_from_path
    # Try verifying poppler without converting real file
    # This usually checks path
    print("pdf2image imported")
except ImportError:
    print("pdf2image not installed")
except Exception as e:
    print(f"Error: {e}")
