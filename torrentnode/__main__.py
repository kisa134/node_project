"""
Точка входа для запуска TorrentNode Net как модуля

Использование: python -m torrentnode
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main()) 