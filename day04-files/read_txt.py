# read_txt.py
with open('test.txt', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    print(content)