# 🚀 Полное руководство по запуску проекта InnovateX

## ✅ Текущий статус

### Backend
- ✅ API работает на http://localhost:8000
- ✅ PostgreSQL на порту 5433
- ✅ Модель YOLOv8 загружена и готова
- ✅ Document Inspector API функционирует

### Frontend
- ✅ React приложение на http://localhost:5173
- ✅ Интегрировано с backend API
- ✅ Поддержка drag & drop для PDF
- ✅ Интерактивный просмотр с bounding boxes

## 🎯 Быстрый запуск

### Вариант 1: Все в Docker (рекомендуется)

```bash
# Backend + Database
docker-compose up -d

# Frontend (опционально, в Docker)
docker-compose --profile frontend up -d
```

### Вариант 2: Backend в Docker, Frontend локально

```bash
# 1. Запустить backend
docker-compose up -d

# 2. Запустить frontend (в новом терминале)
cd frontend
npm install
npm run dev
```

## 📍 Доступные URL

### Backend
- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Document Inspector Health**: http://localhost:8000/api/document-inspector/health

### Frontend
- **React App**: http://localhost:5173

### Database
- **PostgreSQL**: localhost:5433
- **PgAdmin**: http://localhost:5050 (запускается с `make pgadmin`)

## 🧪 Тестирование

### 1. Проверить backend

```bash
# Health check
curl http://localhost:8000/health

# Document Inspector health
curl http://localhost:8000/api/document-inspector/health

# Тест детекции
curl -X POST "http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5" \
  -F "file=@dataset/pdfs/письмо-.pdf" | jq
```

### 2. Тестировать через frontend

1. Откройте http://localhost:5173
2. Перетащите PDF файл или кликните для выбора
3. Нажмите "Analyze document"
4. Просмотрите результаты
5. Откройте PDF viewer для интерактивного просмотра

### 3. Тестировать через Swagger UI

1. Откройте http://localhost:8000/docs
2. Найдите `/api/document-inspector/detect`
3. Нажмите "Try it out"
4. Загрузите PDF файл
5. Установите `conf_threshold` (например, 0.5)
6. Нажмите "Execute"

## 📊 Пример использования API

### Python

```python
import requests

# Загрузить и проанализировать PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/document-inspector/detect",
        files={"file": f},
        params={"conf_threshold": 0.5}
    )
    
result = response.json()
print(f"Найдено элементов на {result['total_pages']} страницах:")
for page in result['pages']:
    print(f"  Страница {page['page_number']}: {len(page['annotations'])} элементов")
```

### JavaScript (Frontend)

```javascript
const formData = new FormData()
formData.append('file', pdfFile)

const response = await fetch(
  'http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5',
  {
    method: 'POST',
    body: formData
  }
)

const result = await response.json()
console.log('Результат анализа:', result)
```

### cURL

```bash
# JSON результат
curl -X POST "http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5" \
  -F "file=@document.pdf" \
  -o result.json

# Визуализация с bounding boxes
curl -X POST "http://localhost:8000/api/document-inspector/detect-visualize?page_number=1" \
  -F "file=@document.pdf" \
  --output result.png
```

## 🔧 Управление

### Backend

```bash
# Просмотр логов
docker-compose logs -f backend

# Перезапуск
docker-compose restart backend

# Остановка
docker-compose down

# Пересборка
docker-compose up -d --build
```

### Frontend

```bash
cd frontend

# Development
npm run dev

# Build для production
npm run build

# Preview production build
npm run preview
```

### База данных

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d innovatex_db

# PgAdmin
make pgadmin
# или
docker-compose --profile tools up -d pgadmin

# Backup
make db-backup

# Restore
make db-restore
```

## 📁 Структура проекта

```
InnovateX/
├── backend/                      # FastAPI backend
│   ├── main.py                   # Главный файл API
│   ├── services/
│   │   └── document_inspector/   # Document Inspector сервис
│   │       ├── router.py         # API endpoints
│   │       ├── service.py        # Бизнес-логика
│   │       ├── detector.py       # YOLOv8 detector
│   │       └── ...
│   └── models/                   # ML модели
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── App.jsx              # Главный компонент
│   │   └── components/          # UI компоненты
│   ├── vite.config.js           # Vite конфигурация
│   └── package.json
├── models/                       # Обученные ML модели
│   └── document_inspector_yolo.pt
├── dataset/                      # Датасеты для обучения
│   ├── pdfs/                     # PDF файлы
│   └── yolo_dataset/             # Подготовленный датасет
├── docker-compose.yml            # Docker конфигурация
└── Makefile                      # Make команды
```

## 🎨 Возможности

### Document Inspector API
- ✅ Детекция подписей (signatures)
- ✅ Детекция печатей (stamps)
- ✅ Детекция QR кодов
- ✅ Обработка многостраничных PDF
- ✅ Настраиваемый порог уверенности (confidence threshold)
- ✅ JSON результаты
- ✅ Визуализация с bounding boxes

### Frontend UI
- ✅ Drag & drop загрузка PDF
- ✅ Интерактивный просмотр с аннотациями
- ✅ Навигация по страницам
- ✅ Фильтры по категориям
- ✅ Миниатюры найденных элементов
- ✅ Spotlight эффект
- ✅ Отображение confidence и времени обработки

## 🐛 Troubleshooting

### Backend не запускается

```bash
# Проверить логи
docker-compose logs backend

# Пересобрать
docker-compose down
docker-compose up -d --build
```

### Frontend не подключается к backend

1. Проверьте что backend работает: `curl http://localhost:8000/health`
2. Проверьте CORS в backend (должно быть `allow_origins=["*"]`)
3. Убедитесь что frontend использует правильный URL

### Модель не загружена

```bash
# Проверить наличие модели
ls -lh models/document_inspector_yolo.pt

# Если модели нет, скопировать обученную модель
cp /path/to/best.pt models/document_inspector_yolo.pt

# Перезапустить backend
docker-compose restart backend
```

### Порты заняты

Измените порты в `.env` или `docker-compose.yml`:
- Backend: `BACKEND_PORT=8080`
- PostgreSQL: `POSTGRES_PORT=5434`
- Frontend: `FRONTEND_PORT=3000`

## 📝 Дополнительная документация

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [Docker Guide](./DOCKER_GUIDE.md)
- [Quick Start](./QUICKSTART.md)

## 🎯 Следующие шаги

1. ✅ Backend запущен и работает
2. ✅ Модель YOLOv8 загружена
3. ✅ Frontend адаптирован под backend API
4. 🔄 Протестировать на реальных документах
5. 🔄 Настроить production окружение
6. 🔄 Добавить мониторинг и логирование

---

**Статус**: ✅ Полностью рабочий
**Версия**: 1.0.0
**Команда**: InnovateX

