# 🐳 Docker Setup Guide for InnovateX

Полное руководство по работе с Docker в проекте InnovateX.

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Требования](#требования)
- [Структура Docker](#структура-docker)
- [Команды](#команды)
- [Конфигурация](#конфигурация)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Быстрый старт

### 1. Убедитесь, что Docker установлен

```bash
docker --version
docker-compose --version
```

### 2. Запустите проект

```bash
# Используя Makefile (рекомендуется)
make dev

# Или напрямую через docker-compose
docker-compose up --build
```

### 3. Проверьте, что все работает

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📦 Требования

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Make** (опционально, для удобства)

### Установка Docker

**macOS:**
```bash
brew install --cask docker
```

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Windows:**
Скачайте Docker Desktop с официального сайта: https://www.docker.com/products/docker-desktop

---

## 🏗️ Структура Docker

### Сервисы

1. **postgres** - PostgreSQL 15 база данных
2. **backend** - FastAPI приложение
3. **pgadmin** - Web-интерфейс для управления БД (опционально)

### Volumes

- `postgres_data` - Данные PostgreSQL
- `pgadmin_data` - Данные PgAdmin
- `backend_uploads` - Загруженные файлы

### Networks

- `innovatex_network` - Внутренняя сеть для связи между контейнерами

---

## 🛠️ Команды

### Используя Makefile (рекомендуется)

```bash
# Показать все доступные команды
make help

# Запустить проект
make up

# Запустить с PgAdmin
make up-full

# Остановить проект
make down

# Перезапустить
make restart

# Посмотреть логи
make logs                # Все сервисы
make logs-backend        # Только backend
make logs-postgres       # Только postgres

# Открыть shell в контейнере
make shell               # Backend shell
make db-shell           # PostgreSQL shell

# Rebuild проекта
make rebuild

# Очистить все (осторожно!)
make clean

# Полный dev setup
make dev
```

### Используя docker-compose напрямую

```bash
# Запустить все сервисы
docker-compose up -d

# Запустить с PgAdmin
docker-compose --profile tools up -d

# Остановить
docker-compose down

# Посмотреть логи
docker-compose logs -f

# Посмотреть статус
docker-compose ps

# Rebuild
docker-compose up --build

# Открыть shell
docker-compose exec backend /bin/bash

# Выполнить команду
docker-compose exec backend python manage.py some_command
```

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Основные параметры:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=innovatex_db

# Application
APP_ENV=development
DEBUG=True
BACKEND_PORT=8000

# Security (ВАЖНО: измените в production!)
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=*
```

### Порты

По умолчанию используются следующие порты:

- `8000` - Backend API
- `5432` - PostgreSQL
- `5050` - PgAdmin (опционально)

Вы можете изменить их в `.env`:

```env
BACKEND_PORT=8080
POSTGRES_PORT=5433
PGADMIN_PORT=8050
```

---

## 🔍 Основные сценарии использования

### Разработка

```bash
# 1. Запустить проект
make up

# 2. Смотреть логи в реальном времени
make logs

# 3. При изменении requirements.txt
make rebuild
```

### Работа с базой данных

```bash
# Открыть PostgreSQL shell
make db-shell

# Или использовать PgAdmin
make pgadmin
# Откройте http://localhost:5050
```

#### Настройка PgAdmin

1. Откройте http://localhost:5050
2. Войдите с учетными данными из `.env`:
   - Email: `admin@innovatex.com`
   - Password: `admin`
3. Добавьте сервер:
   - Host: `postgres`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`

### Отладка

```bash
# Посмотреть логи backend
make logs-backend

# Открыть shell в backend
make shell

# Проверить статус всех сервисов
make status

# Проверить работу API
curl http://localhost:8000/health
```

### Тестирование

```bash
# Запустить тесты в контейнере
make test

# Или напрямую
docker-compose exec backend pytest -v
```

---

## 🐛 Troubleshooting

### Проблема: Порт уже занят

```
Error: bind: address already in use
```

**Решение:**
```bash
# Проверить, что использует порт
lsof -i :8000

# Изменить порт в .env
BACKEND_PORT=8080
```

### Проблема: База данных не подключается

```
Connection refused to postgres:5432
```

**Решение:**
```bash
# Проверить статус postgres
docker-compose ps postgres

# Посмотреть логи
make logs-postgres

# Перезапустить базу
docker-compose restart postgres
```

### Проблема: Backend не запускается

**Решение:**
```bash
# Посмотреть логи
make logs-backend

# Проверить зависимости
docker-compose exec backend pip list

# Rebuild контейнера
make rebuild
```

### Проблема: Volumes не обновляются

**Решение:**
```bash
# Остановить и удалить volumes
make clean-volumes

# Запустить заново
make up
```

### Проблема: Нехватка места на диске

**Решение:**
```bash
# Очистить неиспользуемые образы
docker system prune -a

# Очистить volumes
docker volume prune

# Полная очистка (осторожно!)
docker system prune -a --volumes
```

---

## 📊 Мониторинг

### Проверка здоровья сервисов

```bash
# Статус всех контейнеров
make status

# Health check endpoint
curl http://localhost:8000/health

# Проверка postgres
docker-compose exec postgres pg_isready -U postgres
```

### Логи

```bash
# Все логи
make logs

# Только ошибки
make logs | grep ERROR

# Последние 100 строк
docker-compose logs --tail=100
```

### Ресурсы

```bash
# Использование ресурсов
docker stats

# Информация о контейнерах
docker-compose ps
```

---

## 🔒 Production

### Важные изменения для production:

1. **Измените SECRET_KEY**:
```bash
openssl rand -hex 32
```

2. **Настройте CORS**:
```env
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

3. **Используйте более безопасные пароли**:
```env
POSTGRES_PASSWORD=$(openssl rand -base64 32)
PGADMIN_PASSWORD=$(openssl rand -base64 32)
```

4. **Отключите DEBUG**:
```env
DEBUG=False
APP_ENV=production
```

5. **Используйте docker-compose.prod.yml** (создать отдельно)

---

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)

---

## 💡 Полезные команды

```bash
# Посмотреть размер образов
docker images

# Удалить конкретный контейнер
docker rm -f innovatex_backend

# Экспорт базы данных
docker-compose exec postgres pg_dump -U postgres innovatex_db > backup.sql

# Импорт базы данных
docker-compose exec -T postgres psql -U postgres innovatex_db < backup.sql

# Выполнить Python скрипт
docker-compose exec backend python script.py

# Установить новую зависимость
docker-compose exec backend pip install package_name
# Затем добавить в requirements.txt и rebuild
```

---

## 🎯 Следующие шаги

1. ✅ Настроить Docker окружение
2. ✅ Запустить проект
3. 📝 Ознакомиться с API документацией: http://localhost:8000/docs
4. 🧪 Запустить тесты
5. 🚀 Начать разработку!

---

**Вопросы?** Проверьте [CONTRIBUTING.md](CONTRIBUTING.md) или создайте issue в репозитории.

