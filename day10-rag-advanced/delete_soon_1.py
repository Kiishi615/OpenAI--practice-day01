def sentence_chunks(text):
    """Split text into sentences using regex-based rules"""
    import re
    
    protected = text

    multi_abbrevs = r'(U\.S\.A|U\.S|U\.K|Ph\.D|e\.g|i\.e|a\.m|p\.m)'

    protected = re.sub(
        rf'\b{multi_abbrevs}\.?',
        lambda m: m.group().replace('.', '<ABBR>'),
        protected,
        flags=re.IGNORECASE
    )

    abbrevs= r'(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|al|cf|Inc|Ltd|Co|Corp|St|Ave|Rd|Blvd|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Fig|No|Vol|pp|ed|trans|Gen|Col|Capt|Lt|Sgt)'
    protected = re.sub(rf'\b({abbrevs})\.', r'\1<ABBR>', protected, flags=re.IGNORECASE)

    protected = re.sub(r'\b([A-Z])\.', r'\1<INITIAL>', protected)

    protected = re.sub(r'(\d)\.(\d)', r'\1<DEC>\2', protected)

    protected = re.sub(r'\.{3}', r'<ECLP>', protected)
    protected = re.sub(r'…', '<ELLIP>', protected)

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

    protected = re.sub(
        r'(\S+@\S+\.\S+)',
        lambda m: m.group().replace('.', '<DOT>'),
        protected
    )

    pattern = r'([.!?])\s+(?=[A-Z"\'\(\[]) |([.!?])$'
    parts = re.split(pattern, protected)

    sentences = []
    current = ""

    for part in parts:
        if part is None:
            continue
        if part in '.!?':
            current +=part
            if current.strip():
                sentences.append(current.strip())
            current =""
        else:
            current +=part
    
    if current.strip():
        sentences.append(current.strip())

    restored = []
    for s in sentences:
        s = s.replace('<ABBR>', '.')
        s = s.replace('<INIT>', '.')
        s = s.replace('<DEC>', '.')
        s = s.replace('<ELLIP>', '...')
        s = s.replace('<DOT>', '.')
        restored.append(s)

    return restored