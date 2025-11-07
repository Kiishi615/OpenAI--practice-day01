import os

# Check if file exists
if os.path.exists('sample.txt'):
    print("File exists!")
    
    # Check file size
    size = os.path.getsize('sample.txt')
    print(f"File size: {size} bytes")
    
    # Try reading with different encodings
    try:
        with open('sample.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Content length: {len(content)} characters")
            print("Content:")
            print(content)
            if not content:
                print("File is empty!")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File 'sample.txt' not found!")