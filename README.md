# Tic-Tac-Toe Game

Многопользовательская онлайн-игра "Крестики-нолики" с поддержкой WebSocket для реального времени.

## 🎮 Основные функции

- Многопользовательская игра в реальном времени
- Аутентификация через JWT
- WebSocket соединения для мгновенных обновлений
- Система матчмейкинга
- История игр
- Статистика игроков

## 🛠 Технический стек

- **Backend**: Python 3.9+
- **Framework**: Starlette
- **Database**: SQLite (aiosqlite)
- **WebSocket**: Starlette WebSockets
- **Authentication**: JWT
- **Containerization**: Docker
- **Web Server**: Nginx
- **API Documentation**: OpenAPI/Swagger

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/tic-tac-toe.git
cd tic-tac-toe
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## 🚀 Запуск

### Локальная разработка

```bash
python main.py
```

### Docker

```bash
docker-compose up --build
```

## 📁 Структура проекта

```
tic-tac-toe/
├── config/             # Конфигурационные файлы
├── nginx/             # Nginx конфигурация
├── src/               # Исходный код
│   ├── middleware/    # Middleware компоненты
│   ├── models/        # Модели данных
│   ├── routes/        # API маршруты
│   └── services/      # Бизнес-логика
├── static/            # Статические файлы
├── templates/         # HTML шаблоны
├── docker-compose.yaml
├── Dockerfile
└── requirements.txt
```

## 🔧 Переменные окружения

Создайте файл `.env` в корневой директории:

```env
DEBUG=True
SECRET_KEY=your-secret-key
CORS_ALLOWED_HOSTS=["*"]
DATABASE_URL=sqlite:///./game.db
```

## 🧪 Тесты

```bash
pytest
```

## ⚠️ Важные нюансы

- Для продакшена используйте `docker-compose.prod.yml`
- Все WebSocket соединения требуют JWT токен
- База данных автоматически создается при первом запуске
- Nginx настроен для проксирования WebSocket соединений

## 📄 Лицензия

MIT
