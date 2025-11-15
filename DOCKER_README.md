# 🐳 Docker Configuration Guide

Полное руководство по использованию Docker для InnovateX проекта.

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Требования](#требования)
- [Структура файлов](#структура-файлов)
- [Режимы запуска](#режимы-запуска)
- [Makefile команды](#makefile-команды)
- [Конфигурация](#конфигурация)
- [Troubleshooting](#troubleshooting)

## 🚀 Быстрый старт

### 1. Проверка зависимостей

```bash
make check
```

### 2. Создание .env файла

```bash
make env
# Затем отредактируйте .env файл под свои нужды
```

### 3. Запуск Development окружения

```bash
make dev
```

Или с пересборкой:

```bash
make dev-build
```

### 4. Проверка статуса

```bash
make status
```

## 📦 Требования

- Docker >= 20.10
- Docker Compose >= 2.0
- Make (опционально, но рекомендуется)

## 📁 Структура файлов

```
InnovateX/
├── docker-compose.yml              # Development конфигурация
├── docker-compose.prod.yml         # Production конфигурация
├── .env.example                    # Пример переменных окружения
├── .env                           # Ваши настройки (создать из .env.example)
├── Makefile                       # Команды для управления
├── backend/
│   ├── Dockerfile                 # Development образ
│   ├── Dockerfile.prod           # Production образ
│   └── .dockerignore             # Исключаемые файлы
├── nginx/
│   └── nginx.conf                # Nginx конфигурация (для prod)
└── backups/                      # Бэкапы базы данных
```

## 🎯 Режимы запуска

### Development Mode

**Особенности:**
- Hot-reload при изменении кода
- Debug режим включен
- Volumes для live-кода
- PgAdmin доступен
- Подробные логи

**Запуск:**

```bash
# Простой запуск
docker-compose up -d

# Или с Makefile
make dev

# С пересборкой
make dev-build
```

**Доступные сервисы:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- PgAdmin: http://localhost:5050 (запустить: `make pgadmin`)

### Production Mode

**Особенности:**
- Оптимизированный multi-stage build
- Non-root пользователь
- Nginx reverse proxy
- Resource limits
- Минимальный размер образа
- Health checks
- Логирование с ротацией

**Запуск:**

```bash
# Убедитесь что .env настроен для production
docker-compose -f docker-compose.prod.yml up -d

# Или с Makefile
make prod

# С пересборкой
make prod-build
```

## 🛠 Makefile команды

### Основные команды

```bash
make help              # Показать все доступные команды
make dev              # Запустить development окружение
make prod             # Запустить production окружение
make down             # Остановить контейнеры
make restart          # Перезапустить контейнеры
make logs             # Показать логи всех контейнеров
make logs-backend     # Показать логи backend
make logs-db          # Показать логи базы данных
```

### Работа с базой данных

```bash
make db-shell         # Подключиться к PostgreSQL shell
make db-backup        # Создать бэкап базы данных
make db-restore       # Восстановить из последнего бэкапа
make pgadmin          # Запустить PgAdmin
```

### Тестирование и мониторинг

```bash
make test             # Запустить тесты
make shell            # Открыть bash в backend контейнере
make ps               # Показать запущенные контейнеры
make stats            # Показать статистику контейнеров
```

### Очистка

```bash
make clean            # Удалить контейнеры и volumes
make clean-all        # Удалить всё включая образы
make prune            # Очистить неиспользуемые Docker ресурсы
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

Скопируйте `.env.example` в `.env` и настройте:

```bash
cp .env.example .env
```

**Основные переменные:**

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=innovatex_db

# Security
SECRET_KEY=your_secure_secret_key  # Используйте: openssl rand -hex 32

# Application
APP_ENV=development  # или production
DEBUG=True          # False для production
```

### Генерация безопасных ключей

```bash
# SECRET_KEY
openssl rand -hex 32

# JWT_SECRET_KEY
openssl rand -hex 32
```

### CORS настройки

**Development:**
```bash
CORS_ORIGINS=*
```

**Production:**
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🔧 Продвинутые настройки

### Масштабирование backend

```bash
# Запустить несколько инстансов backend
docker-compose up -d --scale backend=3
```

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только backend
docker-compose logs -f backend

# Последние 100 строк
docker-compose logs --tail=100 backend

# С временными метками
docker-compose logs -f --timestamps backend
```

### Выполнение команд в контейнере

```bash
# Bash shell
docker-compose exec backend bash

# Python shell
docker-compose exec backend python

# Запуск конкретной команды
docker-compose exec backend python -m pytest
```

### Создание миграций (если используете Alembic)

```bash
# Создать миграцию
docker-compose exec backend alembic revision --autogenerate -m "description"

# Применить миграции
docker-compose exec backend alembic upgrade head

# Откатить миграцию
docker-compose exec backend alembic downgrade -1
```

## 🎓 Работа с ML моделями

Модели монтируются как volume:

```yaml
volumes:
  - ./models:/app/models
  - ./dataset:/app/dataset
```

**Тренировка модели в контейнере:**

```bash
# Войти в контейнер
docker-compose exec backend bash

# Запустить тренировку
cd services/document_inspector
python train_model.py
```

## 🔒 Production Security Checklist

- [ ] Настроены безопасные пароли в `.env`
- [ ] `SECRET_KEY` сгенерирован и уникален
- [ ] `DEBUG=False` в production
- [ ] CORS origins настроены конкретно
- [ ] SSL сертификаты установлены для Nginx
- [ ] Volumes имеют правильные permissions
- [ ] Настроен регулярный backup базы данных
- [ ] Логи ротируются и мониторятся
- [ ] Resource limits установлены

## 🐛 Troubleshooting

### Контейнер не запускается

```bash
# Проверить логи
make logs-backend

# Пересобрать образ
docker-compose build --no-cache backend
docker-compose up -d
```

### База данных не подключается

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Проверить логи
make logs-db

# Перезапустить БД
docker-compose restart postgres
```

### Порты заняты

```bash
# Найти процесс использующий порт 8000
lsof -ti:8000

# Убить процесс
kill -9 $(lsof -ti:8000)

# Или изменить порт в .env
BACKEND_PORT=8001
```

### Ошибки с volumes

```bash
# Удалить volumes
docker-compose down -v

# Пересоздать
docker-compose up -d
```

### Нехватка места на диске

```bash
# Очистить неиспользуемые ресурсы
make prune

# Посмотреть использование места
docker system df

# Детальная информация
docker system df -v
```

### Permission errors

```bash
# Исправить права на volumes
sudo chown -R $(whoami):$(whoami) ./uploads ./models

# Для Linux: добавить пользователя в docker группу
sudo usermod -aG docker $USER
```

## 📊 Мониторинг

### Просмотр resource usage

```bash
# Статистика контейнеров
docker stats

# Или через Makefile
make stats
```

### Health checks

```bash
# Проверить health status
docker-compose ps

# Вручную проверить endpoint
curl http://localhost:8000/health
```

## 🔄 Обновление приложения

### Development

```bash
# Остановить контейнеры
make down

# Получить последние изменения
git pull

# Пересобрать и запустить
make dev-build
```

### Production

```bash
# Создать backup
make db-backup

# Остановить контейнеры
make down-prod

# Получить последние изменения
git pull

# Пересобрать и запустить
make prod-build

# Проверить статус
make status
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

## 💡 Best Practices

1. **Всегда используйте .env файл** для конфигурации
2. **Регулярно создавайте backups** базы данных
3. **Мониторьте логи** в production
4. **Используйте health checks** для проверки сервисов
5. **Ограничивайте ресурсы** в production
6. **Используйте volumes** для персистентных данных
7. **Тестируйте на staging** перед production deploy

## 🤝 Contributing

При добавлении новых сервисов в Docker:

1. Добавьте сервис в `docker-compose.yml`
2. Создайте соответствующий Dockerfile
3. Обновите `.env.example` с новыми переменными
4. Добавьте команды в Makefile
5. Обновите эту документацию

## 📝 Changelog

- **v1.0** - Начальная Docker конфигурация
  - Development и Production режимы
  - PostgreSQL + Backend
  - Nginx reverse proxy
  - PgAdmin опционально
  - Makefile для управления

---

**Поддержка:** Если возникли проблемы, создайте issue в репозитории или обратитесь к команде разработки.

