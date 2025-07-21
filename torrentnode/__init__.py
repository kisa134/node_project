import os
import sys

# Add the bundled DLLs to the PATH
dll_path = os.path.join(os.path.dirname(__file__), '..', 'dlls')
if os.path.isdir(dll_path):
    os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(dll_path)

"""
TorrentNode Net - Децентрализованная P2P сеть для распределенных вычислений

Основные компоненты:
- Node: Основной класс узла сети
- Task: Модель задачи для выполнения
- TaskExecutor: Безопасный исполнитель задач
- RewardSystem: Система вознаграждений
"""

__version__ = "0.1.0"
__author__ = "TorrentNode Team"
__license__ = "MIT"

# Оставляем только самые важные импорты верхнего уровня,
# чтобы избежать циклических зависимостей при инициализации.
# Другие компоненты могут быть импортированы напрямую из модулей.
from .node import Node, NodeConfig
from .task_executor import Task, TaskType

__all__ = [
    "Node",
    "NodeConfig",
    "Task",
    "TaskType",
]

# Константы
DEFAULT_PORT = 8888
DEFAULT_DHT_PORT = 8889
MAX_TASK_SIZE = 10 * 1024 * 1024  # 10MB
TASK_TIMEOUT = 300  # 5 минут
TOKEN_DECIMALS = 18 