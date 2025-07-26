import logging
import threading
import time
from datetime import datetime

LOG_FILE = 'swarmmind_events.log'

class SwarmMindLogger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_logger()
            return cls._instance

    def _init_logger(self):
        self.logger = logging.getLogger('SwarmMindLogger')
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.subscribers = []  # Для AI-аналитики

    def log(self, message, level=logging.INFO):
        self.logger.log(level, message)
        self._notify_subscribers(message, level)

    def _notify_subscribers(self, message, level):
        for callback in self.subscribers:
            try:
                callback(message, level)
            except Exception:
                pass

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def get_recent_events(self, n=100):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return lines[-n:]
        except Exception:
            return []

# Глобальный логгер
swarm_logger = SwarmMindLogger()

# Быстрая функция для логирования
log_event = lambda msg, level=logging.INFO: swarm_logger.log(msg, level) 