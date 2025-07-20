"""
CLI интерфейс для TorrentNode Net

Предоставляет команды для управления нодой, задачами и токенами.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from .node import Node, NodeConfig
from .task_executor import Task, TaskType, EXAMPLE_TASKS
from .utils import format_bytes, format_time, is_valid_address

console = Console()


@click.group()
@click.version_option(version='0.1.0', prog_name='TorrentNode Net')
def cli():
    """TorrentNode Net - Децентрализованная P2P сеть для распределенных вычислений"""
    pass


@cli.command()
@click.option('--port', '-p', default=8888, help='Порт для прослушивания')
@click.option('--name', '-n', default=None, help='Имя ноды')
@click.option('--data-dir', '-d', default='./data', help='Директория для данных')
@click.option('--bootstrap', '-b', multiple=True, help='Bootstrap ноды (host:port)')
@click.option('--no-dht', is_flag=True, help='Отключить DHT')
@click.option('--no-encryption', is_flag=True, help='Отключить шифрование')
@click.option('--max-peers', default=50, help='Максимальное количество пиров')
@click.option('--verbose', '-v', is_flag=True, help='Подробный вывод')
def start(port, name, data_dir, bootstrap, no_dht, no_encryption, max_peers, verbose):
    """Запустить ноду TorrentNode"""
    console.print(f"[bold cyan]🚀 TorrentNode Net v0.1.0[/bold cyan]")
    console.print()
    
    # Создание конфигурации
    config = NodeConfig(
        port=port,
        name=name or f"node_{port}",
        data_dir=Path(data_dir),
        bootstrap_nodes=list(bootstrap),
        enable_dht=not no_dht,
        enable_encryption=not no_encryption,
        max_peers=max_peers,
        log_level="DEBUG" if verbose else "INFO"
    )
    
    # Вывод конфигурации
    table = Table(title="Конфигурация ноды")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="green")
    
    table.add_row("Имя", config.name)
    table.add_row("Порт", str(config.port))
    table.add_row("Директория данных", str(config.data_dir))
    table.add_row("DHT", "✓" if config.enable_dht else "✗")
    table.add_row("Шифрование", "✓" if config.enable_encryption else "✗")
    table.add_row("Макс. пиров", str(config.max_peers))
    
    if config.bootstrap_nodes:
        table.add_row("Bootstrap ноды", "\n".join(config.bootstrap_nodes))
    
    console.print(table)
    console.print()
    
    # Создание и запуск ноды
    node = Node(config)
    
    try:
        console.print("[yellow]Нажмите Ctrl+C для остановки[/yellow]")
        asyncio.run(node.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Остановка ноды...[/yellow]")
        asyncio.run(node.stop())
        console.print("[green]✓ Нода остановлена[/green]")


@cli.command()
@click.option('--type', '-t', type=click.Choice([t.value for t in TaskType]), required=True, help='Тип задачи')
@click.option('--data', '-d', required=True, help='Данные задачи (JSON)')
@click.option('--reward', '-r', default=10.0, type=float, help='Вознаграждение в токенах')
@click.option('--node-port', '-p', default=8888, help='Порт ноды')
@click.option('--timeout', default=300, help='Таймаут выполнения (секунды)')
def task(type, data, reward, node_port, timeout):
    """Создать и распределить задачу в сети"""
    console.print("[cyan]Создание задачи...[/cyan]")
    
    try:
        # Парсинг данных
        task_data = json.loads(data)
        
        # Создание задачи
        task_obj = Task(
            type=TaskType(type),
            data=task_data,
            reward=reward,
            timeout=timeout
        )
        
        # Вывод информации о задаче
        table = Table(title="Информация о задаче")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")
        
        table.add_row("ID", task_obj.id)
        table.add_row("Тип", task_obj.type.value)
        table.add_row("Данные", str(task_obj.data))
        table.add_row("Вознаграждение", f"{task_obj.reward} токенов")
        table.add_row("Таймаут", f"{task_obj.timeout} сек")
        
        console.print(table)
        
        # Подтверждение
        if not Confirm.ask("\nРаспределить задачу в сети?"):
            console.print("[red]Отменено[/red]")
            return
        
        # Создание временной ноды для распределения
        config = NodeConfig(port=node_port)
        node = Node(config)
        
        async def distribute():
            node.session = node._create_session()
            torrent_hash = await node.distribute_task(task_obj)
            console.print(f"\n[green]✓ Задача распределена![/green]")
            console.print(f"[cyan]Hash: {torrent_hash}[/cyan]")
            return torrent_hash
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Распределение задачи...", total=None)
            torrent_hash = asyncio.run(distribute())
        
    except json.JSONDecodeError:
        console.print("[red]Ошибка: Неверный формат JSON данных[/red]")
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


@cli.command()
@click.option('--node-port', '-p', default=8888, help='Порт ноды')
def balance(node_port):
    """Показать баланс токенов"""
    try:
        config = NodeConfig(port=node_port)
        node = Node(config)
        
        # Получение баланса
        balance_info = node.reward_system.get_balance_info(node.node_id)
        
        # Вывод информации
        table = Table(title=f"Баланс ноды {node.node_id}")
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="green")
        
        table.add_row("Доступно", f"{balance_info.balance:.2f} токенов")
        table.add_row("Заблокировано", f"{balance_info.locked:.2f} токенов")
        table.add_row("Всего заработано", f"{balance_info.earned_total:.2f} токенов")
        table.add_row("Всего потрачено", f"{balance_info.spent_total:.2f} токенов")
        
        console.print(table)
        
        # История транзакций
        transactions = node.reward_system.get_transactions(node.node_id, limit=10)
        
        if transactions:
            console.print("\n[cyan]Последние транзакции:[/cyan]")
            tx_table = Table()
            tx_table.add_column("Тип", style="cyan")
            tx_table.add_column("От", style="yellow")
            tx_table.add_column("Кому", style="yellow")
            tx_table.add_column("Сумма", style="green")
            tx_table.add_column("Время", style="magenta")
            
            for tx in transactions:
                from_addr = tx.from_address[:8] + "..." if len(tx.from_address) > 10 else tx.from_address
                to_addr = tx.to_address[:8] + "..." if len(tx.to_address) > 10 else tx.to_address
                
                tx_table.add_row(
                    tx.tx_type,
                    from_addr,
                    to_addr,
                    f"{tx.amount:.2f}",
                    format_time(time.time() - tx.timestamp)
                )
            
            console.print(tx_table)
        
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


@cli.command()
@click.option('--from-port', '-f', default=8888, help='Порт ноды отправителя')
@click.option('--to', '-t', required=True, help='ID ноды получателя')
@click.option('--amount', '-a', required=True, type=float, help='Количество токенов')
def transfer(from_port, to, amount):
    """Перевести токены другой ноде"""
    try:
        config = NodeConfig(port=from_port)
        node = Node(config)
        
        # Проверка баланса
        balance = node.reward_system.get_balance(node.node_id)
        if balance < amount:
            console.print(f"[red]Недостаточно средств. Баланс: {balance:.2f} токенов[/red]")
            return
        
        # Подтверждение
        console.print(f"[yellow]Перевод {amount} токенов от {node.node_id} к {to}[/yellow]")
        if not Confirm.ask("Подтвердить перевод?"):
            console.print("[red]Отменено[/red]")
            return
        
        # Выполнение перевода
        success, msg = node.reward_system.transfer(node.node_id, to, amount)
        
        if success:
            console.print(f"[green]✓ Перевод выполнен успешно![/green]")
            if msg != "Success":
                console.print(f"[cyan]TX: {msg}[/cyan]")
        else:
            console.print(f"[red]✗ Ошибка перевода: {msg}[/red]")
            
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


@cli.command()
@click.option('--limit', '-l', default=10, help='Количество позиций')
def leaderboard(limit):
    """Показать таблицу лидеров по заработанным токенам"""
    try:
        # Используем временную конфигурацию для доступа к БД
        config = NodeConfig()
        node = Node(config)
        
        leaders = node.reward_system.get_leaderboard(limit)
        
        if not leaders:
            console.print("[yellow]Таблица лидеров пуста[/yellow]")
            return
        
        table = Table(title="🏆 Таблица лидеров")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Нода", style="yellow")
        table.add_column("Баланс", style="green", justify="right")
        table.add_column("Заработано", style="magenta", justify="right")
        
        for i, (address, balance, earned) in enumerate(leaders, 1):
            node_display = address[:16] + "..." if len(address) > 20 else address
            table.add_row(
                str(i),
                node_display,
                f"{balance:.2f}",
                f"{earned:.2f}"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


@cli.command()
def examples():
    """Показать примеры задач"""
    console.print("[bold cyan]📚 Примеры задач[/bold cyan]\n")
    
    for i, task in enumerate(EXAMPLE_TASKS, 1):
        console.print(f"[yellow]{i}. {task.type.value.upper()}[/yellow]")
        console.print(f"   Данные: {json.dumps(task.data)}")
        console.print(f"   Вознаграждение: {task.reward} токенов")
        console.print(f"   Команда: [cyan]torrentnode task -t {task.type.value} -d '{json.dumps(task.data)}' -r {task.reward}[/cyan]")
        console.print()


@cli.command()
def stats():
    """Показать статистику системы"""
    try:
        config = NodeConfig()
        node = Node(config)
        
        stats = node.reward_system.get_statistics()
        
        table = Table(title="📊 Статистика системы")
        table.add_column("Метрика", style="cyan")
        table.add_column("Значение", style="green")
        
        table.add_row("Всего адресов", str(stats['total_addresses']))
        table.add_row("Общий объем токенов", f"{stats['total_supply']:.2f}")
        table.add_row("Заблокировано токенов", f"{stats['total_locked']:.2f}")
        table.add_row("Всего транзакций", str(stats['total_transactions']))
        table.add_row("Распределено вознаграждений", f"{stats['total_rewards_distributed']:.2f}")
        table.add_row("Начальный баланс ноды", f"{stats['initial_balance_per_node']:.2f}")
        table.add_row("Блокчейн подключен", "✓" if stats['blockchain_connected'] else "✗")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")


@cli.command()
@click.argument('addresses', nargs=-1, required=True)
def connect(addresses):
    """Подключиться к указанным нодам"""
    console.print("[cyan]Проверка адресов...[/cyan]")
    
    valid_addresses = []
    for addr in addresses:
        if is_valid_address(addr):
            valid_addresses.append(addr)
            console.print(f"  ✓ {addr}")
        else:
            console.print(f"  [red]✗ {addr} - неверный формат[/red]")
    
    if valid_addresses:
        console.print(f"\n[green]Валидных адресов: {len(valid_addresses)}[/green]")
        # Здесь была бы логика подключения
    else:
        console.print("\n[red]Нет валидных адресов для подключения[/red]")


def main():
    """Основная функция CLI"""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Критическая ошибка: {e}[/red]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main()) 