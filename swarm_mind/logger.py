import logging
import sys
import os

def setup_logger(name, level=logging.INFO):
    """Настройка логгера с поддержкой Windows"""
    
    # Создаем форматтер без эмодзи для Windows
    if os.name == 'nt':  # Windows
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Очищаем существующие обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Создаем обработчик для файла
    file_handler = logging.FileHandler('swarmmind.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name):
    """Получить существующий логгер"""
    return logging.getLogger(name) 