#!/usr/bin/env python3
"""
Пример использования TorrentNode Net

Демонстрирует основные возможности сети:
- Запуск нод
- Создание и распределение задач
- Выполнение задач и получение вознаграждений
- Перевод токенов между нодами
"""

import asyncio
import json
import time
from pathlib import Path

from torrentnode import Node, NodeConfig, Task, TaskType
from torrentnode.task_executor import EXAMPLE_TASKS


async def run_example():
    """Основной пример"""
    print("🚀 TorrentNode Net - Пример использования")
    print("=" * 50)
    
    # 1. Создание двух нод
    print("\n1. Создание нод...")
    
    # Первая нода (seed node)
    config1 = NodeConfig(
        name="alice_node",
        port=18888,
        data_dir=Path("./example_data/alice"),
        enable_dht=True,
        enable_encryption=True
    )
    node1 = Node(config1)
    
    # Вторая нода (подключается к первой)
    config2 = NodeConfig(
        name="bob_node", 
        port=18889,
        data_dir=Path("./example_data/bob"),
        bootstrap_nodes=["localhost:18888"],
        enable_dht=True,
        enable_encryption=True
    )
    node2 = Node(config2)
    
    print(f"✓ Создана нода Alice: {node1.node_id}")
    print(f"✓ Создана нода Bob: {node2.node_id}")
    
    # 2. Инициализация балансов
    print("\n2. Инициализация балансов...")
    node1.reward_system.init_balance(node1.node_id)
    node2.reward_system.init_balance(node2.node_id)
    
    alice_balance = node1.get_balance()
    bob_balance = node2.get_balance()
    
    print(f"  Alice: {alice_balance} токенов")
    print(f"  Bob: {bob_balance} токенов")
    
    # 3. Создание и выполнение задач
    print("\n3. Создание задач...")
    
    # Задача суммирования
    sum_task = Task(
        type=TaskType.SUM,
        data=[10, 20, 30, 40, 50],
        reward=15.0
    )
    print(f"  Задача SUM: {sum_task.data} → вознаграждение: {sum_task.reward} токенов")
    
    # Задача сортировки
    sort_task = Task(
        type=TaskType.SORT,
        data=[9, 3, 7, 1, 5, 8, 2, 6, 4],
        reward=10.0
    )
    print(f"  Задача SORT: {sort_task.data} → вознаграждение: {sort_task.reward} токенов")
    
    # Задача хэширования
    hash_task = Task(
        type=TaskType.HASH,
        data="Hello, TorrentNode Net!",
        reward=5.0
    )
    print(f"  Задача HASH: '{hash_task.data}' → вознаграждение: {hash_task.reward} токенов")
    
    # 4. Выполнение задач
    print("\n4. Выполнение задач...")
    
    # Alice выполняет задачу суммирования
    result1 = await node1.task_executor.execute(sum_task)
    if result1.success:
        print(f"  Alice выполнила SUM: результат = {result1.result}")
        print(f"    Время выполнения: {result1.execution_time:.3f}с")
        print(f"    Использовано памяти: {result1.memory_used}MB")
        
        # Начисление вознаграждения
        node1.reward_system.add_reward(node1.node_id, sum_task.reward, sum_task.id)
        print(f"  ✓ Alice получила {sum_task.reward} токенов")
    
    # Bob выполняет задачу сортировки
    result2 = await node2.task_executor.execute(sort_task)
    if result2.success:
        print(f"  Bob выполнил SORT: результат = {result2.result}")
        node2.reward_system.add_reward(node2.node_id, sort_task.reward, sort_task.id)
        print(f"  ✓ Bob получил {sort_task.reward} токенов")
    
    # Bob выполняет задачу хэширования
    result3 = await node2.task_executor.execute(hash_task)
    if result3.success:
        print(f"  Bob выполнил HASH: результат = {result3.result[:16]}...")
        node2.reward_system.add_reward(node2.node_id, hash_task.reward, hash_task.id)
        print(f"  ✓ Bob получил {hash_task.reward} токенов")
    
    # 5. Проверка балансов после выполнения задач
    print("\n5. Балансы после выполнения задач:")
    alice_balance = node1.get_balance()
    bob_balance = node2.get_balance()
    
    print(f"  Alice: {alice_balance} токенов (+{sum_task.reward})")
    print(f"  Bob: {bob_balance} токенов (+{sort_task.reward + hash_task.reward})")
    
    # 6. Перевод токенов
    print("\n6. Перевод токенов...")
    transfer_amount = 20.0
    
    success, msg = node1.reward_system.transfer(
        node1.node_id,
        node2.node_id,
        transfer_amount
    )
    
    if success:
        print(f"  ✓ Alice перевела {transfer_amount} токенов Bob")
    else:
        print(f"  ✗ Ошибка перевода: {msg}")
    
    # 7. Финальные балансы
    print("\n7. Финальные балансы:")
    alice_final = node1.get_balance()
    bob_final = node2.get_balance()
    
    print(f"  Alice: {alice_final} токенов")
    print(f"  Bob: {bob_final} токенов")
    
    # 8. Статистика системы
    print("\n8. Статистика системы:")
    stats = node1.reward_system.get_statistics()
    
    print(f"  Всего адресов: {stats['total_addresses']}")
    print(f"  Общий объем токенов: {stats['total_supply']}")
    print(f"  Всего транзакций: {stats['total_transactions']}")
    print(f"  Распределено вознаграждений: {stats['total_rewards_distributed']}")
    
    # 9. Таблица лидеров
    print("\n9. Таблица лидеров:")
    leaders = node1.reward_system.get_leaderboard(5)
    
    for i, (address, balance, earned) in enumerate(leaders, 1):
        node_name = "Alice" if address == node1.node_id else "Bob"
        print(f"  {i}. {node_name}: {balance} токенов (заработано: {earned})")
    
    # 10. Дополнительные примеры задач
    print("\n10. Другие типы задач:")
    
    # Факториал
    factorial_task = Task(
        type=TaskType.FACTORIAL,
        data=10,
        reward=8.0
    )
    result = await node1.task_executor.execute(factorial_task)
    if result.success:
        print(f"  Факториал 10 = {result.result}")
    
    # Проверка простого числа
    prime_task = Task(
        type=TaskType.PRIME_CHECK,
        data=97,
        reward=10.0
    )
    result = await node2.task_executor.execute(prime_task)
    if result.success:
        print(f"  97 - простое число: {result.result}")
    
    # Умножение матриц
    matrix_task = Task(
        type=TaskType.MATRIX_MULTIPLY,
        data={
            'a': [[1, 2], [3, 4]],
            'b': [[5, 6], [7, 8]]
        },
        reward=15.0
    )
    result = await node1.task_executor.execute(matrix_task)
    if result.success:
        print(f"  Результат умножения матриц:")
        for row in result.result:
            print(f"    {row}")
    
    # Анализ текста
    text_task = Task(
        type=TaskType.TEXT_ANALYSIS,
        data="The quick brown fox jumps over the lazy dog. The dog was sleeping.",
        reward=12.0
    )
    result = await node2.task_executor.execute(text_task)
    if result.success:
        print(f"  Анализ текста:")
        print(f"    Слов: {result.result['word_count']}")
        print(f"    Уникальных слов: {result.result['unique_words']}")
        print(f"    Средняя длина слова: {result.result['average_word_length']:.2f}")
        print(f"    Топ слова: {list(result.result['top_words'].items())[:3]}")
    
    print("\n✅ Пример завершен!")
    print("=" * 50)


async def demo_distributed_task():
    """Демонстрация распределенного выполнения задачи через торрент"""
    print("\n📡 Демо: Распределенное выполнение задачи")
    print("=" * 50)
    
    # Создание нод с мок-сессиями для демонстрации
    from unittest.mock import MagicMock, patch
    
    # Создатель задачи
    creator_config = NodeConfig(
        name="creator",
        port=28888,
        data_dir=Path("./example_data/creator")
    )
    creator = Node(creator_config)
    
    # Исполнитель задачи
    worker_config = NodeConfig(
        name="worker",
        port=28889,
        data_dir=Path("./example_data/worker"),
        bootstrap_nodes=["localhost:28888"]
    )
    worker = Node(worker_config)
    
    # Создание сложной задачи
    complex_task = Task(
        type=TaskType.SUM,
        data=list(range(1, 101)),  # Сумма чисел от 1 до 100
        reward=50.0,
        timeout=60
    )
    
    print(f"1. Создана задача: сумма чисел от 1 до 100")
    print(f"   Вознаграждение: {complex_task.reward} токенов")
    
    # Мокаем торрент-функционал для демонстрации
    with patch('torrentnode.node.create_torrent', return_value=b'mock_torrent'):
        with patch('torrentnode.node.lt.torrent_info'):
            creator.session = MagicMock()
            
            # Распределение задачи
            # torrent_hash = await creator.distribute_task(complex_task)
            # print(f"2. Задача распределена в сети")
            # print(f"   Торрент хэш: {torrent_hash[:16]}...")
    
    # Симуляция выполнения задачи воркером
    print(f"3. Worker обнаружил и выполняет задачу...")
    
    result = await worker.task_executor.execute(complex_task)
    
    if result.success:
        print(f"4. Задача выполнена успешно!")
        print(f"   Результат: {result.result}")
        print(f"   Время выполнения: {result.execution_time:.3f}с")
        
        # Начисление вознаграждения
        worker.reward_system.init_balance(worker.node_id)
        worker.reward_system.add_reward(worker.node_id, complex_task.reward, complex_task.id)
        
        print(f"5. Worker получил вознаграждение: {complex_task.reward} токенов")
        print(f"   Баланс: {worker.get_balance()} токенов")
    
    print("\n✅ Демо завершено!")


async def stress_test_example():
    """Стресс-тест выполнения множества задач"""
    print("\n⚡ Стресс-тест: Выполнение множества задач")
    print("=" * 50)
    
    # Создание ноды для тестирования
    config = NodeConfig(
        name="stress_test_node",
        port=38888,
        data_dir=Path("./example_data/stress_test")
    )
    node = Node(config)
    node.reward_system.init_balance(node.node_id)
    
    # Создание множества задач разных типов
    tasks = []
    
    # 10 задач суммирования
    for i in range(10):
        tasks.append(Task(
            type=TaskType.SUM,
            data=list(range(i*10, (i+1)*10)),
            reward=5.0
        ))
    
    # 5 задач сортировки
    for i in range(5):
        import random
        data = list(range(20))
        random.shuffle(data)
        tasks.append(Task(
            type=TaskType.SORT,
            data=data,
            reward=3.0
        ))
    
    # 5 задач хэширования
    for i in range(5):
        tasks.append(Task(
            type=TaskType.HASH,
            data=f"Test string {i} for hashing",
            reward=2.0
        ))
    
    print(f"Создано {len(tasks)} задач для выполнения")
    
    # Выполнение всех задач
    start_time = time.time()
    successful = 0
    failed = 0
    total_reward = 0.0
    
    print("\nВыполнение задач...")
    
    for i, task in enumerate(tasks):
        result = await node.task_executor.execute(task)
        
        if result.success:
            successful += 1
            total_reward += task.reward
            node.reward_system.add_reward(node.node_id, task.reward, task.id)
            
            if (i + 1) % 5 == 0:
                print(f"  Выполнено {i + 1}/{len(tasks)} задач...")
        else:
            failed += 1
            print(f"  ✗ Ошибка в задаче {i + 1}: {result.error}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Статистика
    print(f"\n📊 Результаты стресс-теста:")
    print(f"  Всего задач: {len(tasks)}")
    print(f"  Успешно выполнено: {successful}")
    print(f"  Ошибок: {failed}")
    print(f"  Общее время: {total_time:.2f}с")
    print(f"  Среднее время на задачу: {total_time/len(tasks):.3f}с")
    print(f"  Заработано токенов: {total_reward}")
    print(f"  Финальный баланс: {node.get_balance()}")
    
    print("\n✅ Стресс-тест завершен!")


if __name__ == "__main__":
    print("TorrentNode Net - Примеры использования")
    print("=====================================\n")
    
    print("Выберите пример:")
    print("1. Основной пример (2 ноды, задачи, переводы)")
    print("2. Распределенное выполнение задачи")
    print("3. Стресс-тест (множество задач)")
    print("4. Запустить все примеры")
    
    choice = input("\nВаш выбор (1-4): ")
    
    try:
        if choice == "1":
            asyncio.run(run_example())
        elif choice == "2":
            asyncio.run(demo_distributed_task())
        elif choice == "3":
            asyncio.run(stress_test_example())
        elif choice == "4":
            asyncio.run(run_example())
            asyncio.run(demo_distributed_task())
            asyncio.run(stress_test_example())
        else:
            print("Неверный выбор!")
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc() 