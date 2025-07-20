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

from .node import Node, NodeConfig
from .task_executor import TaskExecutor, Task, TaskResult
from .rewards import RewardSystem, TokenBalance
from .utils import generate_node_id, create_torrent, verify_hash

__all__ = [
    "Node",
    "NodeConfig", 
    "TaskExecutor",
    "Task",
    "TaskResult",
    "RewardSystem",
    "TokenBalance",
    "generate_node_id",
    "create_torrent",
    "verify_hash",
]

# Константы
DEFAULT_PORT = 8888
DEFAULT_DHT_PORT = 8889
MAX_TASK_SIZE = 10 * 1024 * 1024  # 10MB
TASK_TIMEOUT = 300  # 5 минут
TOKEN_DECIMALS = 18 