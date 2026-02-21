import sys
from pathlib import Path


def setup_november_imports():
    this_file=Path(__file__)
    november_challenge_folder =this_file.parent

    if str(november_challenge_folder) not in sys.path:
        sys.path.insert(0,str(november_challenge_folder))
    
    for item in november_challenge_folder.iterdir():
        if item.is_dir():
            if item.name.startswith('day'):

                if str(item) not in sys.path:
                    sys.path.insert(0, str(item))
    
    

setup_november_imports()