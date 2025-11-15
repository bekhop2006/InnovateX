# InnovateX Backend

Гибкий бэкенд API построенный на FastAPI с модульной архитектурой.

## 📋 Особенности

- ✅ **FastAPI** - современный веб-фреймворк
- ✅ **PostgreSQL** - база данных с SQLAlchemy ORM
- ✅ **Модульная архитектура** - легко расширяемая структура
- ✅ **Аутентификация** - система регистрации и авторизации
- ✅ **Управление счетами** - создание и управление счетами
- ✅ **Транзакции** - обработка финансовых операций
- ✅ **E-commerce** - система продуктов и корзины
- ✅ **Document Inspector** - анализ документов с YOLOv8

## 📁 Структура проекта

```
backend/
├── main.py                      # Точка входа приложения
├── database.py                  # Конфигурация БД
├── requirements.txt             # Зависимости
├── .env.example                 # Пример переменных окружения
│
├── models/                      # SQLAlchemy модели
│   ├── user.py
│   └── account.py
│
└── services/                    # Бизнес-логика по модулям
    ├── auth/                    # Аутентификация
    ├── account/                 # Управление счетами
    ├── transaction/             # Транзакции
    ├── product/                 # Продукты
    ├── cart/                    # Корзина
    └── document_inspector/      # Анализ документов
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Настройте переменные окружения:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/innovatex_db
APP_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=8000
```

### 3. Создание базы данных

```bash
# Создайте БД в PostgreSQL
createdb innovatex_db

# Или через psql
psql -U postgres
CREATE DATABASE innovatex_db;
```

### 4. Запуск сервера

```bash
# Запуск с автоперезагрузкой (development)
python main.py

# Или через uvicorn напрямую
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Сервер будет доступен по адресу: http://localhost:8000

API документация (Swagger): http://localhost:8000/docs

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Регистрация пользователя
- `POST /api/auth/login` - Вход в систему
- `GET /api/auth/users/{user_id}` - Получить пользователя
- `PUT /api/auth/users/{user_id}` - Обновить профиль
- `POST /api/auth/users/{user_id}/avatar` - Загрузить аватар
- `DELETE /api/auth/users/{user_id}` - Удалить пользователя

### Accounts (`/api/accounts`)
- `GET /api/accounts` - Получить все счета
- `GET /api/accounts/{account_id}` - Получить счет по ID
- `POST /api/accounts` - Создать новый счет
- `GET /api/accounts/user/{user_id}` - Получить счета пользователя
- `PATCH /api/accounts/{account_id}/balance` - Обновить баланс
- `POST /api/accounts/transfer` - Перевод между счетами

### Transactions (`/api/transactions`)
- `GET /api/transactions` - Получить все транзакции
- `GET /api/transactions/{transaction_id}` - Получить транзакцию по ID
- `POST /api/transactions` - Создать транзакцию
- `GET /api/transactions/user/{user_id}` - Транзакции пользователя
- `GET /api/transactions/account/{account_id}` - Транзакции счета
- `POST /api/transactions/filter` - Фильтровать транзакции
- `GET /api/transactions/stats/summary` - Статистика

### Products (`/api/products`)
- `GET /api/products` - Получить все продукты
- `GET /api/products/{product_id}` - Получить продукт по ID
- `POST /api/products` - Создать продукт
- `POST /api/products/search` - Поиск продуктов
- `PUT /api/products/{product_id}` - Обновить продукт
- `DELETE /api/products/{product_id}` - Удалить продукт

### Cart (`/api/cart`)
- `POST /api/cart` - Добавить товар в корзину
- `GET /api/cart/user/{user_id}` - Получить корзину пользователя
- `PUT /api/cart/{cart_id}` - Обновить количество
- `DELETE /api/cart/{cart_id}` - Удалить из корзины
- `POST /api/cart/checkout` - Оформить заказ

### Document Inspector (`/api/document-inspector`)
- Анализ документов с использованием YOLOv8
- (См. документацию модуля для деталей)

## 🗄️ Модели базы данных

### User
- Информация о пользователе
- Аутентификация (email, password_hash)
- Профиль (name, surname, avatar, phone)

### Account
- Финансовые счета пользователей
- Типы: checking, savings, credit
- Баланс и валюта
- Статусы: active, blocked, closed

## 🔧 Добавление нового модуля

1. Создайте папку в `services/`:
```
services/
└── your_module/
    ├── router.py      # API endpoints
    ├── service.py     # Бизнес-логика
    └── schemas.py     # Pydantic схемы
```

2. Добавьте роутер в `main.py`:
```python
try:
    from services.your_module.router import router as your_router
    app.include_router(your_router, prefix="/api/your-module", tags=["Your Module"])
except ImportError:
    print("⚠️  Your Module router not found")
```

3. При необходимости создайте модель в `models/`:
```python
# models/your_model.py
from sqlalchemy import Column, Integer, String
from database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    id = Column(Integer, primary_key=True, index=True)
    # ... другие поля
```

## 🛠️ Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер
- **Bcrypt** - хеширование паролей
- **Pillow** - обработка изображений
- **YOLOv8** - детекция объектов (Document Inspector)

## 📝 Переменные окружения

```env
# База данных
DATABASE_URL=postgresql://user:password@host:port/dbname

# Настройки приложения
APP_ENV=development          # development, production
DEBUG=True                   # True, False
SECRET_KEY=your_secret_key

# Сервер
HOST=0.0.0.0
PORT=8000
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=.
```

## 📄 Лицензия

MIT

## 👤 Автор

InnovateX Team

