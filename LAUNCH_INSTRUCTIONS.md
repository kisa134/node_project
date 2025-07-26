# 🚀 ИНСТРУКЦИИ ПО ЗАПУСКУ SWARMIND

## 🎯 Быстрый старт

### 1. Автоматический запуск (рекомендуется)
```bash
python start_autonomous_system.py
```

Этот скрипт автоматически:
- ✅ Проверит все зависимости
- 🐳 Запустит Docker контейнеры
- 🌐 Запустит веб-интерфейс
- 🧬 Запустит эволюционную систему
- 📊 Запустит мониторинг

### 2. Ручной запуск компонентов

#### Шаг 1: Проверка системы
```bash
python scripts/full_system_test.py
```

#### Шаг 2: Запуск Docker контейнеров
```bash
docker-compose up --build -d
```

#### Шаг 3: Запуск веб-интерфейса
```bash
python web_interface.py
```

#### Шаг 4: Запуск эволюции
```bash
python scripts/run_evolution.py full
```

## 🌐 Веб-интерфейс

После запуска веб-интерфейса откройте в браузере:
```
http://localhost:5000
```

### Возможности веб-интерфейса:
- 📊 Мониторинг системных метрик (CPU, память)
- 🐳 Статус Docker контейнеров
- 🧬 Отслеживание эволюционных циклов
- 🚀 Управление эволюцией (запуск/остановка)
- 🔄 Автообновление данных

## 🐳 Docker контейнеры

### Проверка статуса:
```bash
docker-compose ps
```

### Просмотр логов:
```bash
docker-compose logs -f
```

### Остановка:
```bash
docker-compose down
```

## 🧬 Эволюционная система

### Демонстрация (3 цикла):
```bash
python scripts/simple_evolution_demo.py
```

### Полная эволюция (бесконечно):
```bash
python scripts/run_evolution.py full
```

### Тестирование компонентов:
```bash
python scripts/run_evolution.py test
```

## 📊 Мониторинг и управление

### Проверка статуса системы:
```bash
python scripts/full_system_test.py
```

### Просмотр логов:
- Docker контейнеры: `docker-compose logs -f`
- Веб-интерфейс: логи в консоли
- Эволюция: логи в консоли

### Остановка всей системы:
```bash
# Остановка Docker
docker-compose down

# Остановка процессов (Ctrl+C в терминалах)
```

## 🔧 Требования

### Системные требования:
- Python 3.11+
- Docker & Docker Compose
- 4GB+ RAM
- 2GB+ свободного места

### Python зависимости:
```bash
pip install -r requirements.txt
```

### Дополнительные требования:
- Ollama (для LLM функциональности)
- Доступ к интернету (для загрузки моделей)

## 🚨 Устранение неполадок

### Проблема: Docker контейнеры не запускаются
```bash
# Проверьте Docker:
docker --version
docker-compose --version

# Пересоберите образы:
docker-compose down
docker-compose up --build
```

### Проблема: Веб-интерфейс недоступен
```bash
# Проверьте порт 5000:
netstat -an | grep 5000

# Перезапустите веб-интерфейс:
python web_interface.py
```

### Проблема: Ollama не работает
```bash
# Проверьте Ollama:
curl http://localhost:11434/api/version

# Запустите Ollama:
ollama serve
```

### Проблема: Недостаточно памяти
```bash
# Остановите ненужные контейнеры:
docker system prune -a

# Уменьшите количество нейронов в docker-compose.yml
```

## 🎯 Рекомендуемый рабочий процесс

1. **Запуск**: `python start_autonomous_system.py`
2. **Мониторинг**: Откройте http://localhost:5000
3. **Наблюдение**: Следите за эволюцией через веб-интерфейс
4. **Остановка**: Ctrl+C в терминале запуска

## 🌟 Дополнительные возможности

### Запуск отдельных нейронов:
```bash
python scripts/run_neuron.py --type=miner --neuron.name MyMiner
python scripts/run_neuron.py --type=llm_validator --neuron.name MyValidator
```

### Тестирование P2P:
```bash
python scripts/run_neuron.py --type=miner --neuron.p2p_port=6881
python scripts/run_neuron.py --type=validator --neuron.p2p_port=6882
```

### Настройка конфигурации:
Отредактируйте файлы в папке `swarm_mind/` для настройки поведения системы.

---

## 🎉 Готово!

Ваша SwarmMind система теперь работает автономно! 

🌐 **Веб-интерфейс**: http://localhost:5000  
🐳 **Docker статус**: `docker-compose ps`  
🧬 **Эволюция**: Работает в фоне  
📊 **Мониторинг**: Активен  

Система будет эволюционировать и улучшаться самостоятельно! 🚀 