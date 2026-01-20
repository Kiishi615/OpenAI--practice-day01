def inspect_document(file_path: str):

    """See what unstructured outputs for a file."""

    from shared import read_document

    text = read_document(file_path)

    # Count structure

    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    single_newlines = text.count('\n') - text.count('\n\n') * 2

    print(f"\n{'='*60}")

    print(f"📄 File: {file_path}")

    print(f"{'='*60}")

    print(f"Total characters: {len(text):,}")

    print(f"Total words: {len(text.split()):,}")

    print(f"Paragraph breaks (\\n\\n): {len(paragraphs)}")

    print(f"Single newlines: {single_newlines}")

    if paragraphs:

        sizes = [len(p) for p in paragraphs]

        print(f"\nParagraph sizes:")

        print(f" Min: {min(sizes)} chars")

        print(f" Max: {max(sizes)} chars")

        print(f" Avg: {sum(sizes)//len(sizes)} chars")

        print(f"\n{'─'*60}")

        print("First 500 chars:")

        print(f"{'─'*60}")

        print(repr(text[:500])) # repr shows \n explicitly

        print(f"\n{'─'*60}")

        print("First 3 paragraphs:")

        print(f"{'─'*60}")

        for i, p in enumerate(paragraphs[:3], 1):

            preview = p[:150] + "..." if len(p) > 150 else p

            print(f"\n[{i}] ({len(p)} chars):")

            print(f" {preview}")

    return {

    "char_count": len(text),

    "word_count": len(text.split()),

    "paragraph_count": len(paragraphs),

    "paragraph_sizes": [len(p) for p in paragraphs] if paragraphs else [],

    "text": text

    }

if __name__ == "__main__":
    inspect_document(r'C:\Users\Audit\Documents\November-Challenge\day10-rag-advanced\documents\033547.pdf')
