def fixed_size_chunks(text, chunk_size=100):

    chunks = []
    current_chunk = []
    words = text.split()

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) == chunk_size:
            chunks.append(" " .join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def overlap_chunks(text, chunk_size=100, overlap=20):
    chunks = []
    current_chunk = []
    words = text.split()

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) == chunk_size:
            chunks.append(" " .join(current_chunk))
            current_chunk = current_chunk[-overlap:] if overlap>0 else[]

    if current_chunk and len(current_chunk) > overlap:
        chunks.append(" ".join(current_chunk))
    return chunks

def sentence_chunks_legacy(text):

    """Split text into sentences using regex-based rules."""
    import re
    
    protected = text
    
    # Fix 1: Handle multi-period abbreviations FIRST (U.S.A., Ph.D., etc.)
    multi_abbrevs = r'(?:U\.S\.A|U\.S|U\.K|Ph\.D|e\.g|i\.e|a\.m|p\.m)'
    protected = re.sub(
        rf'\b{multi_abbrevs}\.?',
        lambda m: m.group().replace('.', '<ABBR>'),
        protected,
        flags=re.IGNORECASE
    )
    
    # Fix 2: Expanded single-period abbreviations (added military ranks, "May")
    abbrevs = r'(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|al|cf|Inc|Ltd|Co|Corp|St|Ave|Rd|Blvd|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Fig|No|Vol|pp|ed|trans|Gen|Col|Capt|Lt|Sgt)'
    protected = re.sub(rf'\b({abbrevs})\.', r'\1<ABBR>', protected, flags=re.IGNORECASE)
    
    # Protect initials (single capital letter followed by period)
    protected = re.sub(r'\b([A-Z])\.', r'\1<INIT>', protected)
    
    # Protect numbers with decimals
    protected = re.sub(r'(\d)\.(\d)', r'\1<DEC>\2', protected)
    
    # Protect ellipsis
    protected = re.sub(r'\.{3}', '<ELLIP>', protected)
    protected = re.sub(r'…', '<ELLIP>', protected)
    
    # Fix 3: Protect URLs with http/https (not just www)
    protected = re.sub(
        r'(https?://[^\s]+)',
        lambda m: m.group().replace('.', '<DOT>'),
        protected
    )
    protected = re.sub(
        r'(www\.[^\s]+)',
        lambda m: m.group().replace('.', '<DOT>'),
        protected
    )
    
    # Protect emails
    protected = re.sub(
        r'(\S+@\S+\.\S+)',
        lambda m: m.group().replace('.', '<DOT>'),
        protected
    )
    
    # Split on sentence boundaries
    pattern = r'([.!?])\s+(?=[A-Z"\'\(\[])|([.!?])$'
    parts = re.split(pattern, protected)
    
    # Reconstruct sentences
    sentences = []
    current = ""
    
    for part in parts:
        if part is None:
            continue
        if part in '.!?':
            current += part
            if current.strip():
                sentences.append(current.strip())
            current = ""
        else:
            current += part
    
    if current.strip():
        sentences.append(current.strip())
    
    # Restore protected characters
    restored = []
    for s in sentences:
        s = s.replace('<ABBR>', '.')
        s = s.replace('<INIT>', '.')
        s = s.replace('<DEC>', '.')
        s = s.replace('<ELLIP>', '...')
        s = s.replace('<DOT>', '.')
        restored.append(s)
    
    return restored

def sentence_chunks(text):
    import nltk
    sentences = nltk.sent_tokenize(text)
    return sentences

def paragraph_chunks(text):
    import re

    pattern = r'(\n\s*\n)'
    chunks = re.split(pattern, text)

    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks


# Test it
if __name__ == "__main__":
    test_text = """Dr. Smith went to Washington. He met J. K. Rowling there! Did he enjoy it? Yes... he did. The price was $29.99 for the book. "Amazing!" she exclaimed. Visit www.example.com for more info. This is version 2.0 of the software."""
    
    sentences = sentence_chunks(test_text)
    
    print("=" * 50)
    for i, s in enumerate(sentences, 1):
        print(f"{i}: {s}")
    print("=" * 50)

