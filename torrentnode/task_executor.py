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
import resource
import signal
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


class SandboxExecutor:
    """Исполнитель кода в изолированной среде"""
    
    def __init__(self):
        self.executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
    
    def execute_in_sandbox(self, func, args, timeout: int, max_memory: int):
        """Выполнение функции в отдельном процессе с ограничениями"""
        future = self.executor.submit(self._sandboxed_execution, func, args, max_memory)
        
        try:
            result = future.result(timeout=timeout)
            return result
        except TimeoutError:
            future.cancel()
            raise TimeoutError(f"Task execution exceeded timeout of {timeout}s")
        except Exception as e:
            raise Exception(f"Sandbox execution failed: {str(e)}")
    
    @staticmethod
    def _sandboxed_execution(func, args, max_memory: int):
        """Выполнение с ограничениями ресурсов"""
        # Установка лимитов только на Unix-системах
        if platform.system() != 'Windows':
            # Ограничение памяти
            memory_limit = max_memory * 1024 * 1024  # MB to bytes
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            
            # Ограничение CPU времени
            resource.setrlimit(resource.RLIMIT_CPU, (300, 300))  # 5 минут
            
            # Ограничение размера файлов
            resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))  # 10MB
            
            # Ограничение количества процессов
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
        
        # Выполнение функции
        start_time = time.time()
        process = psutil.Process()
        
        try:
            result = func(*args)
            execution_time = time.time() - start_time
            
            # Получение статистики использования ресурсов
            memory_info = process.memory_info()
            cpu_times = process.cpu_times()
            
            return {
                'result': result,
                'execution_time': execution_time,
                'memory_used': memory_info.rss // (1024 * 1024),  # MB
                'cpu_time': cpu_times.user + cpu_times.system
            }
        except Exception as e:
            return {
                'error': str(e),
                'execution_time': time.time() - start_time
            }


class TaskExecutor:
    """Основной исполнитель задач"""
    
    def __init__(self):
        self.sandbox = SandboxExecutor()
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
        """Выполнение задачи"""
        logger.info(f"Executing task: {task.id}, type: {task.type}")
        
        if task.type not in self.task_handlers:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=f"Unsupported task type: {task.type}"
            )
        
        handler = self.task_handlers[task.type]
        
        try:
            # Выполнение в event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.sandbox.execute_in_sandbox,
                handler,
                (task.data,),
                task.timeout,
                task.max_memory
            )
            
            if 'error' in result:
                return TaskResult(
                    task_id=task.id,
                    success=False,
                    error=result['error'],
                    execution_time=result.get('execution_time', 0)
                )
            
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result['result'],
                execution_time=result['execution_time'],
                memory_used=result.get('memory_used', 0),
                cpu_time=result.get('cpu_time', 0)
            )
            
        except TimeoutError as e:
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e)
            )
    
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
        
        import numpy as np
        
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
        # В реальной системе здесь была бы более сложная песочница
        # Сейчас просто заглушка
        raise NotImplementedError("Custom code execution is not yet implemented")


# Примеры задач для тестирования
EXAMPLE_TASKS = [
    Task(
        type=TaskType.SUM,
        data=[1, 2, 3, 4, 5],
        reward=5.0
    ),
    Task(
        type=TaskType.MULTIPLY,
        data=[2, 3, 4, 5],
        reward=5.0
    ),
    Task(
        type=TaskType.SORT,
        data=[5, 2, 8, 1, 9, 3],
        reward=5.0
    ),
    Task(
        type=TaskType.HASH,
        data="Hello, TorrentNode Net!",
        reward=3.0
    ),
    Task(
        type=TaskType.FACTORIAL,
        data=10,
        reward=8.0
    ),
    Task(
        type=TaskType.PRIME_CHECK,
        data=97,
        reward=10.0
    ),
    Task(
        type=TaskType.MATRIX_MULTIPLY,
        data={
            'a': [[1, 2], [3, 4]],
            'b': [[5, 6], [7, 8]]
        },
        reward=15.0
    ),
    Task(
        type=TaskType.TEXT_ANALYSIS,
        data="The quick brown fox jumps over the lazy dog. The dog was really lazy.",
        reward=12.0
    )
]


async def main():
    """Пример использования TaskExecutor"""
    executor = TaskExecutor()
    
    for task in EXAMPLE_TASKS[:3]:  # Тестируем первые 3 задачи
        print(f"\nExecuting task: {task.type}")
        print(f"Data: {task.data}")
        
        result = await executor.execute(task)
        
        if result.success:
            print(f"Result: {result.result}")
            print(f"Execution time: {result.execution_time:.3f}s")
            print(f"Memory used: {result.memory_used}MB")
        else:
            print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main()) 