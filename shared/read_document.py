
# def read_document(file_path: str) -> str:
#     """Read document with intelligent spacing based on element types."""
#     from unstructured.partition.auto import partition
    
#     elements = partition(filename=file_path)
    
#     if not elements:
#         return ""
    
#     # Build text with appropriate spacing
#     parts = []
#     for i, el in enumerate(elements):
#         el_type = type(el).__name__
#         text = str(el).strip()
        
#         if not text:
#             continue
            
#         # Add extra break after titles/headers
#         if el_type in ["Title", "Header"]:
#             parts.append(text + "\n")
#         else:
#             parts.append(text)
    
#     # Join regular elements with paragraph breaks
#     return '\n\n'.join(parts)

def read_document(file_path: str) -> str:
    from unstructured.partition.auto import partition 
    elements = partition(filename=file_path)

    return '\n\n'.join([str(el) for el in elements]) 