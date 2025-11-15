# 🚀 Docker Quick Start - InnovateX

Быстрый старт для запуска проекта в Docker за 5 минут!

## ⚡ Супер-быстрый старт

```bash
# 1. Клонируйте репозиторий (если еще не сделали)
git clone <your-repo-url>
cd InnovateX

# 2. Запустите автоматическую установку
./scripts/docker-init.sh

# 3. Готово! 🎉
```

Или используя Make:

```bash
make dev
```

## 📋 Требования

- Docker (>= 20.10)
- Docker Compose (>= 2.0)
- Make (опционально, для удобства)

## 🎯 Основные команды

### С использованием Make (рекомендуется)

```bash
make help          # Показать все команды
make up            # Запустить проект
make down          # Остановить проект
make logs          # Показать логи
make restart       # Перезапустить
make shell         # Открыть shell в backend
make rebuild       # Пересобрать проект
```

### С использованием docker-compose

```bash
docker-compose up -d                    # Запустить
docker-compose down                     # Остановить
docker-compose logs -f                  # Логи
docker-compose restart                  # Перезапустить
docker-compose exec backend /bin/bash  # Shell
```

### С использованием скриптов

```bash
./scripts/docker-init.sh       # Первоначальная настройка
./scripts/docker-backup.sh     # Создать backup БД
./scripts/docker-restore.sh    # Восстановить backup
./scripts/docker-cleanup.sh    # Очистить Docker ресурсы
```

## 🌐 Эндпоинты

После запуска доступны следующие URL:

- **API**: http://localhost:8000
- **Документация (Swagger)**: http://localhost:8000/docs
- **Документация (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **PgAdmin** (опционально): http://localhost:5050

## 🛠️ Настройка

### Переменные окружения

Файл `.env` создается автоматически при первом запуске. Для ручной настройки:

```bash
cp .env.example .env
nano .env  # или используйте любой редактор
```

### Основные параметры

```env
# База данных
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=innovatex_db

# Приложение
APP_ENV=development
DEBUG=True
BACKEND_PORT=8000

# Безопасность (важно для production!)
SECRET_KEY=your-secret-key
```

## 📊 Работа с базой данных

### PgAdmin

```bash
# Запустить PgAdmin
make pgadmin
# или
docker-compose --profile tools up -d pgadmin

# Откройте http://localhost:5050
# Email: admin@innovatex.com
# Password: admin
```

### PostgreSQL CLI

```bash
# Открыть psql
make db-shell
# или
docker-compose exec postgres psql -U postgres -d innovatex_db
```

### Backup и Restore

```bash
# Создать backup
./scripts/docker-backup.sh

# Восстановить из backup
./scripts/docker-restore.sh
```

## 🐛 Решение проблем

### Порт уже занят

```bash
# Изменить порт в .env
BACKEND_PORT=8080
```

### База данных не подключается

```bash
# Проверить статус
docker-compose ps postgres

# Посмотреть логи
docker-compose logs postgres

# Перезапустить
docker-compose restart postgres
```

### Ошибки при запуске backend

```bash
# Посмотреть логи
docker-compose logs backend

# Пересобрать образ
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Очистка при проблемах

```bash
# Полная очистка и перезапуск
make clean
make up

# Или используя скрипт
./scripts/docker-cleanup.sh
```

## 📚 Дополнительная документация

- [Полное руководство по Docker](./DOCKER_GUIDE.md)
- [Основная документация](./README.md)
- [Руководство по разработке](./CONTRIBUTING.md)

## 💡 Полезные советы

### Мониторинг ресурсов

```bash
# Использование ресурсов
docker stats

# Статус сервисов
make status
```

### Разработка

```bash
# Логи в реальном времени
make logs

# Выполнить команду в контейнере
docker-compose exec backend python manage.py <command>

# Установить новую зависимость
docker-compose exec backend pip install package_name
# Затем добавьте в requirements.txt и пересоберите
```

### Тестирование

```bash
# Запустить тесты
docker-compose exec backend pytest

# С подробным выводом
docker-compose exec backend pytest -v

# Конкретный тест
docker-compose exec backend pytest tests/test_auth.py
```

## 🚀 Production

Для production используйте:

```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# С Nginx
docker-compose -f docker-compose.prod.yml --profile nginx up -d
```

**Важно для production:**

1. Измените `SECRET_KEY` на безопасный ключ
2. Настройте `CORS_ORIGINS` на конкретные домены
3. Установите `DEBUG=False`
4. Используйте HTTPS (настройте SSL в Nginx)
5. Регулярно создавайте backups

## ✅ Checklist первого запуска

- [ ] Docker установлен и запущен
- [ ] Клонирован репозиторий
- [ ] Файл `.env` создан и настроен
- [ ] Выполнен `make up` или `./scripts/docker-init.sh`
- [ ] API доступен по http://localhost:8000
- [ ] Документация открывается http://localhost:8000/docs
- [ ] Health check возвращает OK: http://localhost:8000/health

## 🎉 Готово!

Теперь вы можете начать разработку! Все изменения в коде автоматически применяются благодаря hot-reload.

**Нужна помощь?** Посмотрите [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) или создайте issue.

