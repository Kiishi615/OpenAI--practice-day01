from typing import Optional, Any

def read_text_file(filename:str) -> Optional[str]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content= f.read()
        return content
    except FileNotFoundError:
        print(f"Error: File '{filename}' was not found.")
    except Exception as e:
        print(f"Some other error {e} occured")

    


def save_text_file(filename:str, content:Any):
    try:
        with open(filename, 'w',encoding='utf-8') as f:
            f.write(str(content))
    except Exception as e:
        print(f"Error writing file: {e}")

def append_to_file(filename, content):
    try:
        with open(filename, 'a') as f:
            f.write(str(content))
    except Exception as e:
        print(f"Error occured appending to file: {e}")

if __name__== "__main__" :
    test_file = "test.txt"

    # Test save_text_file
    save_text_file(test_file, "Hello, world!\n")
    print("After save_text_file:")
    print(read_text_file(test_file))

    # Test append_to_file
    append_to_file(test_file, "This is appended text.\n")
    print("After append_to_file:")
    print(read_text_file(test_file))

    # Test read_text_file directly
    content = read_text_file(test_file)
    print("Final file content read using read_text_file:")
    print(content)