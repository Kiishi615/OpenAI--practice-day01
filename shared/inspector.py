"""
Parameter Inspector Utility
Save this file and import: from inspector import params, full_inspect
"""

import inspect
from typing import Any

def params(obj: Any) -> None:
    """Quick view of required/optional parameters"""
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        print(f"❌ Cannot inspect: {obj}")
        return
    
    name = getattr(obj, '__name__', str(obj))
    
    print(f"\n{'='*50}")
    print(f"📦 {name}")
    print('='*50)
    
    required, optional = [], []
    
    for pname, param in sig.parameters.items():
        if pname in ('self', 'cls', 'args', 'kwargs'):
            continue
        
        if param.default == inspect.Parameter.empty:
            required.append((pname, param.annotation))
        else:
            optional.append((pname, param.default, param.annotation))
    
    # Required params
    print("\n🔴 REQUIRED:")
    if required:
        for pname, annotation in required:
            type_hint = _format_annotation(annotation)
            print(f"   • {pname}{type_hint}")
    else:
        print("   (none)")
    
    # Optional params
    print("\n🟢 OPTIONAL:")
    if optional:
        for pname, default, annotation in optional:
            type_hint = _format_annotation(annotation)
            default_str = _format_default(default)
            print(f"   • {pname}{type_hint} = {default_str}")
    else:
        print("   (none)")
    
    print()


def full_inspect(obj: Any) -> None:
    """Detailed inspection including methods and docstring"""
    params(obj)
    
    # Show docstring
    if obj.__doc__:
        print("📝 DOCSTRING:")
        doc_lines = obj.__doc__.strip().split('\n')[:5]  # First 5 lines
        for line in doc_lines:
            print(f"   {line}")
        if len(obj.__doc__.strip().split('\n')) > 5:
            print("   ...")
    
    # Show useful methods
    print("\n🔧 KEY METHODS:")
    methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m, None))]
    for method in methods[:10]:  # First 10 methods
        print(f"   • {method}()")
    if len(methods) > 10:
        print(f"   ... and {len(methods) - 10} more")
    
    print()


def _format_annotation(annotation) -> str:
    """Format type annotation for display"""
    if annotation == inspect.Parameter.empty:
        return ""
    
    if hasattr(annotation, '__name__'):
        return f": {annotation.__name__}"
    
    return f": {str(annotation)}"


def _format_default(default) -> str:
    """Format default value for display"""
    if callable(default):
        return '<function>'
    if isinstance(default, str) and len(default) > 30:
        return f"'{default[:30]}...'"
    return repr(default)

# Quick aliases
p = params
fi = full_inspect