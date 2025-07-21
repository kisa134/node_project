"""
Модуль безопасного выполнения задач

Реализует песочницу для выполнения кода задач с ограничениями по ресурсам
и безопасности.
"""
import asyncio
import json
import multiprocessing
import os
import platform
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil
import structlog
from pydantic import BaseModel, Field, validator

# Модуль resource недоступен в Windows, поэтому делаем условный импорт
try:
    import resource
except ImportError:
    resource = None

from .rewards import RewardSystem
from .utils import calculate_file_hash

logger = structlog.get_logger()


class TaskType(str, Enum):
    """Поддерживаемые типы задач"""
    SUM = "sum"
    MULTIPLY = "multiply"
    SORT = "sort"
    HASH = "hash"
    FACTORIAL = "factorial"
    PRIME_CHECK = "prime_check"
    MATRIX_MULTIPLY = "matrix_multiply"
    TEXT_ANALYSIS = "text_analysis"
    ML_INFERENCE = "ml_inference"  # В разработке
    RENDER = "render"  # В разработке
    CUSTOM = "custom"  # Пользовательский код


class Task(BaseModel):
    """Модель задачи для выполнения"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: TaskType
    data: Union[List, Dict, str, Any]
    code: Optional[str] = None  # Для CUSTOM задач
    reward: float = 10.0
    timeout: int = 300  # секунды
    max_memory: int = 512  # MB
    max_cpu_percent: int = 80
    created_at: float = Field(default_factory=time.time)
    
    @validator('code')
    def validate_code(cls, v, values):
        if values.get('type') == TaskType.CUSTOM and not v:
            raise ValueError("Code is required for CUSTOM tasks")
        if v and values.get('type') != TaskType.CUSTOM:
            raise ValueError("Code is only allowed for CUSTOM tasks")
        return v


@dataclass
class TaskResult:
    """Результат выполнения задачи"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: int = 0  # MB
    cpu_time: float = 0.0


def _sandboxed_execution(func, args, timeout, max_memory):
    """
    Выполняет функцию в отдельном процессе с ограничениями.
    Эта функция должна быть на верхнем уровне модуля для совместимости с multiprocessing.
    """
    
    # Установка лимитов только на Unix-системах, где доступен модуль resource
    if resource:
        try:
            # Ограничение памяти (в байтах)
            memory_limit = max_memory * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            
            # Ограничение процессорного времени (в секундах)
            resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
            
            # Ограничение размера создаваемых файлов
            resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024)) # 10MB
            
            # Ограничение количества дочерних процессов
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        except Exception as e:
            # В случае ошибки просто логируем, но не прерываем выполнение
            # т.к. на некоторых системах могут быть проблемы с установкой лимитов
            # print(f"Warning: Could not set resource limits: {e}")
            pass

    start_time = time.time()
    process = psutil.Process(os.getpid())
    
    try:
        result_data = func(*args)
        execution_time = time.time() - start_time
        
        memory_info = process.memory_info()
        cpu_times = process.cpu_times()
        
        return {
            'success': True,
            'result': result_data,
            'execution_time': execution_time,
            'memory_used': memory_info.rss // (1024 * 1024),  # в MB
            'cpu_time': cpu_times.user + cpu_times.system
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'success': False,
            'error': str(e),
            'execution_time': execution_time,
        }


class TaskExecutor:
    """Основной исполнитель задач"""

    def __init__(self):
        # Используем ProcessPoolExecutor для запуска задач в отдельных процессах
        self.executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.task_handlers = {
            TaskType.SUM: self._execute_sum,
            TaskType.MULTIPLY: self._execute_multiply,
            TaskType.SORT: self._execute_sort,
            TaskType.HASH: self._execute_hash,
            TaskType.FACTORIAL: self._execute_factorial,
            TaskType.PRIME_CHECK: self._execute_prime_check,
            TaskType.MATRIX_MULTIPLY: self._execute_matrix_multiply,
            TaskType.TEXT_ANALYSIS: self._execute_text_analysis,
            TaskType.CUSTOM: self._execute_custom,
        }

    async def execute(self, task: Task) -> TaskResult:
        """Асинхронное выполнение задачи"""
        logger.info(f"Executing task: {task.id}, type: {task.type}")
        
        handler = self.task_handlers.get(task.type)
        if not handler:
            return TaskResult(task_id=task.id, success=False, error=f"Unsupported task type: {task.type}")

        loop = asyncio.get_event_loop()
        
        try:
            future = self.executor.submit(
                _sandboxed_execution,
                handler,
                (task.data,),
                task.timeout,
                task.max_memory
            )
            
            # Ждем результат с таймаутом
            result_dict = await loop.run_in_executor(None, lambda: future.result(timeout=task.timeout))

            if result_dict.get('success'):
                return TaskResult(
                    task_id=task.id,
                    success=True,
                    result=result_dict.get('result'),
                    execution_time=result_dict.get('execution_time', 0),
                    memory_used=result_dict.get('memory_used', 0),
                    cpu_time=result_dict.get('cpu_time', 0)
                )
            else:
                 return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=result_dict.get('error'),
                    execution_time=result_dict.get('execution_time', 0)
                )

        except TimeoutError:
            return TaskResult(task_id=task.id, success=False, error=f"Task execution timed out after {task.timeout} seconds.")
        except Exception as e:
            logger.error("Task execution failed unexpectedly", exc_info=e)
            return TaskResult(task_id=task.id, success=False, error=f"An unexpected error occurred: {e}")

    @staticmethod
    def _execute_sum(data: List[Union[int, float]]) -> Union[int, float]:
        """Суммирование чисел"""
        if not isinstance(data, list):
            raise ValueError("Data must be a list of numbers")
        return sum(data)
    
    @staticmethod
    def _execute_multiply(data: List[Union[int, float]]) -> Union[int, float]:
        """Умножение чисел"""
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data must be a non-empty list of numbers")
        
        result = 1
        for num in data:
            result *= num
        return result
    
    @staticmethod
    def _execute_sort(data: List[Any]) -> List[Any]:
        """Сортировка массива"""
        if not isinstance(data, list):
            raise ValueError("Data must be a list")
        return sorted(data)
    
    @staticmethod
    def _execute_hash(data: str) -> str:
        """Вычисление SHA-256 хэша"""
        import hashlib
        if not isinstance(data, str):
            data = str(data)
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def _execute_factorial(data: int) -> int:
        """Вычисление факториала"""
        if not isinstance(data, int) or data < 0:
            raise ValueError("Data must be a non-negative integer")
        if data > 1000:
            raise ValueError("Factorial input too large (max 1000)")
        
        import math
        return math.factorial(data)
    
    @staticmethod
    def _execute_prime_check(data: int) -> bool:
        """Проверка на простое число"""
        if not isinstance(data, int) or data < 2:
            raise ValueError("Data must be an integer >= 2")
        if data > 10**12:
            raise ValueError("Number too large for prime check")
        
        if data == 2:
            return True
        if data % 2 == 0:
            return False
        
        for i in range(3, int(data**0.5) + 1, 2):
            if data % i == 0:
                return False
        return True
    
    @staticmethod
    def _execute_matrix_multiply(data: Dict[str, List[List[float]]]) -> List[List[float]]:
        """Умножение матриц"""
        if not isinstance(data, dict) or 'a' not in data or 'b' not in data:
            raise ValueError("Data must contain matrices 'a' and 'b'")
        
        # numpy может быть не установлен по умолчанию, импортируем внутри
        try:
            import numpy as np
        except ImportError:
            raise RuntimeError("Numpy is required for matrix multiplication. Please install it.")

        a = np.array(data['a'])
        b = np.array(data['b'])
        
        if a.shape[1] != b.shape[0]:
            raise ValueError("Matrix dimensions don't match for multiplication")
        
        result = np.matmul(a, b)
        return result.tolist()
    
    @staticmethod
    def _execute_text_analysis(data: str) -> Dict[str, Any]:
        """Анализ текста"""
        if not isinstance(data, str):
            raise ValueError("Data must be a string")
        
        words = data.split()
        chars_no_spaces = len(data.replace(" ", ""))
        
        # Подсчет частоты слов
        word_freq = {}
        for word in words:
            word_lower = word.lower().strip('.,!?;:"')
            if word_lower:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Топ-10 слов
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_chars': len(data),
            'chars_no_spaces': chars_no_spaces,
            'word_count': len(words),
            'unique_words': len(word_freq),
            'average_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'top_words': dict(top_words)
        }
    
    @staticmethod
    def _execute_custom(data: Dict[str, Any]) -> Any:
        """Выполнение пользовательского кода (ограниченно)"""
        code = data.get("code")
        if not code:
            raise ValueError("No code provided for custom task")

        # ОПАСНО! Это просто заглушка. В реальной системе нужна настоящая песочница.
        # Например, с использованием Docker, gVisor, или WebAssembly.
        # Ограничим доступные встроенные функции для минимальной безопасности.
        restricted_globals = {
            "__builtins__": {
                "print": print, "len": len, "range": range, "sum": sum,
                "abs": abs, "min": min, "max": max, "sorted": sorted,
                "int": int, "float": float, "str": str, "list": list,
                "dict": dict, "tuple": tuple, "set": set, "bool": bool,
                "isinstance": isinstance,
                "Exception": Exception,
            },
        }
        
        try:
            # Выполняем код в ограниченном окружении
            exec(code, restricted_globals)
            # Пользовательский код должен вызвать функцию `main()` и вернуть результат
            if "main" in restricted_globals:
                return restricted_globals["main"]()
            else:
                raise RuntimeError("No `main` function found in the provided code.")
        except Exception as e:
            raise RuntimeError(f"Error executing custom code: {e}")


async def main():
    """Пример использования TaskExecutor"""
    executor = TaskExecutor()
    task = Task(
        type=TaskType.SUM,
        data=[1, 2, 3, 4, 5, 10, 20],
        reward=5.0
    )
    
    print(f"\nExecuting task: {task.type}")
    print(f"Data: {task.data}")
    
    result = await executor.execute(task)
    
    if result.success:
        print(f"Result: {result.result}")
        print(f"Execution time: {result.execution_time:.4f}s")
        print(f"Memory used: {result.memory_used}MB")
        print(f"CPU time: {result.cpu_time:.4f}s")
    else:
        print(f"Error: {result.error}")
        print(f"Execution time: {result.execution_time:.4f}s")


if __name__ == "__main__":
    # Для Windows необходимо это условие для корректной работы multiprocessing
    multiprocessing.freeze_support()
    asyncio.run(main()) 