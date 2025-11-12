def read_text_file(filename):
    with open(filename, 'r') as f:
        content= f.read()
    return content

def save_text_file(filename, content):
    with open(filename, 'w') as f:
            f.write(str(content))

def append_to_file(filename, content):
    with open(filename, 'a') as f:
        f.write(str(content))

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