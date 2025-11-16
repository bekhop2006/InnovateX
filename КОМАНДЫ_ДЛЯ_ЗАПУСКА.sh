#!/bin/bash
# Скрипт для быстрого запуска InnovateX
# Выполняйте команды по очереди

echo "🚀 Запуск InnovateX..."
echo ""

# Шаг 1: Запуск Backend и БД
echo "📦 Шаг 1: Запуск Docker контейнеров..."
cd /Users/beknur/InnovateX
docker-compose up -d

echo ""
echo "⏳ Ждём 10 секунд пока запустится база данных..."
sleep 10

# Шаг 2: Миграции
echo ""
echo "🗄️  Шаг 2: Применение миграций базы данных..."
docker-compose exec backend alembic revision --autogenerate -m "Add authentication and scan history"
docker-compose exec backend alembic upgrade head

# Шаг 3: Создание админа
echo ""
echo "👤 Шаг 3: Создание администратора..."
docker-compose exec backend python scripts/create_admin.py

# Шаг 4: Frontend
echo ""
echo "🎨 Шаг 4: Установка зависимостей frontend..."
cd frontend
npm install
npm install react-router-dom

echo ""
echo "✅ Всё готово!"
echo ""
echo "📝 Запустите frontend командой:"
echo "   cd frontend && npm run dev"
echo ""
echo "🌐 После этого откройте:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000/docs"
echo ""
echo "🔐 Данные админа:"
echo "   Email:    admin@innovatex.com"
echo "   Пароль:   admin123"
echo ""

