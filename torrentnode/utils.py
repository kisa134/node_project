"""
Утилиты для TorrentNode Net

Вспомогательные функции для работы с торрентами, хэшами, сетью и т.д.
"""

import hashlib
import json
import os
import random
import socket
import string
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bencodepy
import libtorrent as lt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_node_id() -> str:
    """Генерация уникального ID ноды"""
    # Комбинация UUID и временной метки для уникальности
    unique_id = f"{uuid.uuid4().hex[:8]}-{int(time.time())}"
    return f"node_{unique_id}"


def generate_random_string(length: int = 32) -> str:
    """Генерация случайной строки"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Поиск свободного порта"""
    for i in range(max_attempts):
        port = start_port + i
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_attempts}")


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Вычисление хэша файла"""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def calculate_data_hash(data: Any, algorithm: str = 'sha256') -> str:
    """Вычисление хэша данных"""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, (str, bytes)):
        data = str(data)
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hash_func = hashlib.new(algorithm)
    hash_func.update(data)
    
    return hash_func.hexdigest()


def verify_hash(data: Any, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """Проверка хэша данных"""
    actual_hash = calculate_data_hash(data, algorithm)
    return actual_hash == expected_hash


def create_torrent(
    path: str,
    name: str,
    comment: str = "",
    trackers: List[str] = None,
    web_seeds: List[str] = None,
    piece_size: int = 0,  # 0 = auto
    private: bool = False
) -> bytes:
    """Создание торрент-файла"""
    fs = lt.file_storage()
    
    # Добавление файлов
    if os.path.isfile(path):
        fs.add_file(os.path.basename(path), os.path.getsize(path))
    else:
        lt.add_files(fs, path)
    
    # Создание торрента
    create_flags = 0
    if piece_size == 0:
        piece_size = 0  # libtorrent выберет автоматически
    
    t = lt.create_torrent(fs, piece_size, -1, create_flags)
    
    # Метаданные
    t.set_creator(f"TorrentNode/{generate_node_id()}")
    t.set_comment(comment)
    
    # Трекеры
    if trackers:
        for i, tracker in enumerate(trackers):
            t.add_tracker(tracker, i)
    
    # Web seeds
    if web_seeds:
        for seed in web_seeds:
            t.add_url_seed(seed)
    
    # Приватный торрент
    if private:
        t.set_priv(True)
    
    # Установка хэшей
    lt.set_piece_hashes(t, os.path.dirname(path))
    
    # Генерация торрент-файла
    torrent_data = t.generate()
    return bencodepy.encode(torrent_data)


def parse_torrent(torrent_data: bytes) -> Dict[str, Any]:
    """Парсинг торрент-файла"""
    try:
        torrent_dict = bencodepy.decode(torrent_data)
        
        info = torrent_dict.get(b'info', {})
        
        return {
            'name': info.get(b'name', b'').decode('utf-8', errors='ignore'),
            'piece_length': info.get(b'piece length', 0),
            'pieces': len(info.get(b'pieces', b'')) // 20,
            'files': _parse_files(info),
            'total_size': _calculate_total_size(info),
            'trackers': _parse_trackers(torrent_dict),
            'creation_date': torrent_dict.get(b'creation date', 0),
            'created_by': torrent_dict.get(b'created by', b'').decode('utf-8', errors='ignore'),
            'comment': torrent_dict.get(b'comment', b'').decode('utf-8', errors='ignore'),
            'info_hash': calculate_data_hash(bencodepy.encode(info))
        }
    except Exception as e:
        raise ValueError(f"Invalid torrent file: {e}")


def _parse_files(info: dict) -> List[Dict[str, Any]]:
    """Парсинг списка файлов из торрента"""
    files = []
    
    if b'files' in info:
        # Multi-file torrent
        for file_info in info[b'files']:
            path_parts = [p.decode('utf-8', errors='ignore') for p in file_info[b'path']]
            files.append({
                'path': os.path.join(*path_parts),
                'size': file_info[b'length']
            })
    else:
        # Single file torrent
        files.append({
            'path': info[b'name'].decode('utf-8', errors='ignore'),
            'size': info[b'length']
        })
    
    return files


def _calculate_total_size(info: dict) -> int:
    """Вычисление общего размера торрента"""
    if b'files' in info:
        return sum(f[b'length'] for f in info[b'files'])
    else:
        return info.get(b'length', 0)


def _parse_trackers(torrent_dict: dict) -> List[str]:
    """Парсинг списка трекеров"""
    trackers = []
    
    # Одиночный трекер
    if b'announce' in torrent_dict:
        trackers.append(torrent_dict[b'announce'].decode('utf-8', errors='ignore'))
    
    # Список трекеров
    if b'announce-list' in torrent_dict:
        for tier in torrent_dict[b'announce-list']:
            for tracker in tier:
                trackers.append(tracker.decode('utf-8', errors='ignore'))
    
    return list(set(trackers))  # Удаление дубликатов


def generate_encryption_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Генерация ключа шифрования из пароля"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = kdf.derive(password.encode())
    return key, salt


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Шифрование данных"""
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Расшифровка данных"""
    f = Fernet(key)
    return f.decrypt(encrypted_data)


def format_bytes(size: int) -> str:
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_time(seconds: float) -> str:
    """Форматирование времени в человекочитаемый вид"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def is_valid_address(address: str) -> bool:
    """Проверка валидности адреса (IP:port или hostname:port)"""
    try:
        if ':' not in address:
            return False
        
        host, port = address.rsplit(':', 1)
        port = int(port)
        
        if not (0 < port < 65536):
            return False
        
        # Проверка IP адреса
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            # Проверка hostname
            return len(host) > 0 and all(c.isalnum() or c in '.-' for c in host)
    
    except Exception:
        return False


def split_address(address: str) -> Tuple[str, int]:
    """Разделение адреса на хост и порт"""
    if not is_valid_address(address):
        raise ValueError(f"Invalid address format: {address}")
    
    host, port = address.rsplit(':', 1)
    return host, int(port)


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Глубокое слияние двух словарей"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def chunk_data(data: bytes, chunk_size: int = 1024 * 1024) -> List[bytes]:
    """Разбиение данных на чанки"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def validate_task_data(task_type: str, data: Any) -> Tuple[bool, Optional[str]]:
    """Валидация данных задачи"""
    validators = {
        'sum': lambda d: isinstance(d, list) and all(isinstance(x, (int, float)) for x in d),
        'multiply': lambda d: isinstance(d, list) and all(isinstance(x, (int, float)) for x in d),
        'sort': lambda d: isinstance(d, list),
        'hash': lambda d: isinstance(d, str),
        'factorial': lambda d: isinstance(d, int) and d >= 0,
        'prime_check': lambda d: isinstance(d, int) and d >= 2,
        'matrix_multiply': lambda d: isinstance(d, dict) and 'a' in d and 'b' in d,
        'text_analysis': lambda d: isinstance(d, str),
    }
    
    if task_type not in validators:
        return False, f"Unknown task type: {task_type}"
    
    try:
        if validators[task_type](data):
            return True, None
        else:
            return False, f"Invalid data format for task type: {task_type}"
    except Exception as e:
        return False, str(e)


def create_task_manifest(task: Dict[str, Any]) -> Dict[str, Any]:
    """Создание манифеста задачи"""
    return {
        'version': '1.0',
        'id': task.get('id', str(uuid.uuid4())),
        'type': task['type'],
        'created_at': time.time(),
        'data_hash': calculate_data_hash(task['data']),
        'requirements': {
            'timeout': task.get('timeout', 300),
            'max_memory': task.get('max_memory', 512),
            'max_cpu_percent': task.get('max_cpu_percent', 80),
        },
        'reward': task.get('reward', 10.0),
        'metadata': task.get('metadata', {})
    }


def verify_task_manifest(manifest: Dict[str, Any], task_data: Any) -> bool:
    """Проверка манифеста задачи"""
    required_fields = ['version', 'id', 'type', 'created_at', 'data_hash', 'requirements', 'reward']
    
    # Проверка наличия полей
    for field in required_fields:
        if field not in manifest:
            return False
    
    # Проверка хэша данных
    expected_hash = manifest['data_hash']
    actual_hash = calculate_data_hash(task_data)
    
    return expected_hash == actual_hash


# Константы для сетевого взаимодействия
DEFAULT_TRACKERS = [
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://tracker.leechers-paradise.org:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.cyberia.is:6969/announce",
]

DHT_BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("router.utorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("dht.aelitis.com", 6881),
] 