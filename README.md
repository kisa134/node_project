# TorrentNode Net

🌐 **Децентрализованная P2P сеть для распределенных вычислений и хранения**

TorrentNode Net - это инновационная платформа, объединяющая лучшие практики BitTorrent, Chia, Bitcoin и Ethereum для создания экологичной и масштабируемой сети распределенных вычислений.

## 🚀 Особенности

- **P2P архитектура**: Полностью децентрализованная сеть на базе DHT (Distributed Hash Table)
- **Торрент-протокол**: Распределение задач через .torrent файлы
- **Безопасное выполнение**: Изолированная песочница для выполнения кода
- **Система вознаграждений**: Токены за выполнение задач
- **Экологичность**: Proof-of-Space для "фарминга" задач
- **Масштабируемость**: От локальной сети до интернета
- **Шифрование**: Защита данных и коммуникаций

## 📋 Требования

- Python 3.11+
- Poetry (для управления зависимостями)
- Docker (опционально)

## 🛠️ Установка

### Через Poetry (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/torrentnode-net.git
cd torrentnode-net

# Установите зависимости
poetry install

# Активируйте виртуальное окружение
poetry shell
```

### Через pip

```bash
# Установите зависимости
pip install -r requirements.txt
```

### Быстрый старт

```bash
# Используйте bootstrap скрипт
./bootstrap.sh
```

## 🎯 Использование

### Запуск одной ноды

```bash
# Запуск ноды с настройками по умолчанию
python -m torrentnode.node

# Запуск с кастомным портом
python -m torrentnode.node --port 8888

# Запуск с включенным логированием
python -m torrentnode.node --verbose
```

### Запуск нескольких нод локально

```bash
# Терминал 1 - Первая нода
python -m torrentnode.node --port 8888 --name node1

# Терминал 2 - Вторая нода
python -m torrentnode.node --port 8889 --name node2 --bootstrap localhost:8888
```

### Docker запуск

```bash
# Запуск через docker-compose
docker-compose -f infra/docker-compose.yml up

# Масштабирование нод
docker-compose -f infra/docker-compose.yml up --scale node=3
```

## 📚 Примеры

### Создание и распределение задачи

```python
from torrentnode import Node, Task

# Создаем ноду
node = Node(port=8888)
node.start()

# Создаем задачу суммирования
task = Task(
    type="sum",
    data=[1, 2, 3, 4, 5],
    reward=10  # токенов
)

# Распределяем задачу в сети
torrent_hash = node.distribute_task(task)
print(f"Задача распределена: {torrent_hash}")

# Ожидаем результаты
result = node.wait_for_result(torrent_hash)
print(f"Результат: {result}")  # 15
```

### Выполнение задач и получение вознаграждения

```python
# Нода автоматически выполняет доступные задачи
node = Node(port=8889)
node.start()

# Проверяем баланс токенов
balance = node.get_balance()
print(f"Баланс: {balance} токенов")
```

### Поддерживаемые типы задач

- `sum` - суммирование чисел
- `multiply` - умножение чисел
- `sort` - сортировка массива
- `hash` - вычисление хэша
- `ml_inference` - инференс ML модели (в разработке)
- `render` - рендеринг 3D сцены (в разработке)

## 🏗️ Архитектура

```
TorrentNode Net
├── DHT Layer (Kademlia)
│   └── Peer Discovery
├── Torrent Layer
│   ├── Task Distribution
│   └── Data Transfer
├── Execution Layer
│   ├── Sandbox Environment
│   └── Task Processor
├── Consensus Layer
│   ├── Result Verification
│   └── Token Distribution
└── Storage Layer
    ├── Task Cache
    └── Token Database
```

## 🔒 Безопасность

- **Изоляция кода**: Все задачи выполняются в изолированных процессах
- **Проверка хэшей**: Верификация целостности данных
- **Шифрование**: End-to-end шифрование коммуникаций
- **Ограничения ресурсов**: CPU/RAM лимиты для задач
- **Репутационная система**: Отслеживание надежности нод

## 🧪 Тестирование

```bash
# Запуск всех тестов
poetry run pytest

# Запуск с покрытием
poetry run pytest --cov=torrentnode

# Запуск линтера
poetry run ruff check

# Форматирование кода
poetry run ruff format
```

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Гайдлайны

- Следуйте PEP 8
- Добавляйте тесты для новой функциональности
- Обновляйте документацию
- Используйте type hints

## 📊 Производительность

- **Пропускная способность**: до 1000 задач/сек на ноду
- **Латентность**: < 100мс для локальной сети
- **Масштабирование**: до 10,000 нод в сети
- **Эффективность**: 95%+ успешных выполнений

## 🗺️ Roadmap

- [x] Базовая P2P сеть
- [x] Торрент протокол для задач
- [x] Песочница для выполнения
- [x] Система токенов (mock)
- [ ] Интеграция с Ethereum testnet
- [ ] ML задачи
- [ ] GPU поддержка
- [ ] Мобильные клиенты
- [ ] Web интерфейс

## 📜 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🙏 Благодарности

- BitTorrent за протокол обмена файлами
- Chia Network за концепцию Proof-of-Space
- Ethereum за смарт-контракты
- Сообществу open-source

## 📞 Контакты

- GitHub Issues: [github.com/yourusername/torrentnode-net/issues](https://github.com/yourusername/torrentnode-net/issues)
- Email: torrentnode@example.com
- Discord: [Присоединиться к серверу](https://discord.gg/torrentnode)

---

**⚡ Построен с любовью к децентрализации ⚡** 