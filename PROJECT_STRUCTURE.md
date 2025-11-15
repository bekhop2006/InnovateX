# 📁 Структура проекта Document Inspector

Полная документация структуры проекта "Цифровой Инспектор".

## 📂 Корневая структура

```
InnovateX/
├── backend/                           # Backend приложение
├── dataset/                           # Датасет и аннотации
├── models/                            # Обученные модели
├── README.md                          # Главная документация
├── QUICKSTART.md                      # Быстрый старт
├── CONTRIBUTING.md                    # Руководство для контрибьюторов
├── PROJECT_STRUCTURE.md              # Этот файл
└── .gitignore                         # Git ignore файл
```

## 🔧 Backend Structure

```
backend/
├── main.py                            # FastAPI приложение (entry point)
├── database.py                        # Database setup
├── requirements.txt                   # Python dependencies
│
├── models/                            # SQLAlchemy models
│   ├── user.py
│   └── account.py
│
└── services/                          # Microservices architecture
    ├── auth/                          # Authentication service
    ├── account/                       # Account management
    ├── cart/                          # Shopping cart
    ├── product/                       # Product catalog
    ├── transaction/                   # Transactions
    ├── crypto/                        # Crypto operations
    │
    └── document_inspector/            # 🎯 НОВЫЙ СЕРВИС
        ├── __init__.py                # Package initializer
        ├── router.py                  # API endpoints (REST)
        ├── schemas.py                 # Pydantic models
        ├── service.py                 # Business logic
        ├── detector.py                # YOLOv8 detector class
        ├── utils.py                   # PDF utilities
        │
        ├── prepare_dataset.py         # Dataset preparation script
        ├── train_model.py             # Model training script
        ├── test_api.py                # API testing script
        └── example_usage.py           # Usage examples
```

## 📊 Dataset Structure

```
dataset/
├── pdfs/                              # 📄 Original PDF documents
│   ├── АПЗ-.pdf
│   ├── письмо-.pdf
│   ├── отр-1.pdf
│   └── ... (40+ PDFs)
│
├── selected_annotations.json          # 🏷️ Ground truth annotations
├── masked_annotations.json            # Alternative annotations
│
└── yolo_dataset/                      # 🤖 Prepared for YOLO training
    ├── data.yaml                      # Dataset config
    │
    ├── images/
    │   ├── train/                     # Training images (80%)
    │   │   ├── document_page_1.jpg
    │   │   └── ...
    │   └── val/                       # Validation images (20%)
    │       ├── document_page_5.jpg
    │       └── ...
    │
    └── labels/
        ├── train/                     # Training labels (YOLO format)
        │   ├── document_page_1.txt
        │   └── ...
        └── val/                       # Validation labels
            ├── document_page_5.txt
            └── ...
```

## 🤖 Models Directory

```
models/
├── .gitkeep                           # Keeps directory in git
└── document_inspector_yolo.pt         # 🎯 Trained YOLOv8 model
                                       # (gitignored, ~6-100MB depending on version)
```

## 📡 API Endpoints

### Document Inspector Service

**Base URL:** `/api/document-inspector`

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/health` | Health check и статус модели |
| POST | `/detect` | Детекция элементов (JSON response) |
| POST | `/detect-visualize` | Детекция с визуализацией (Image response) |

## 🔄 Data Flow

### 1️⃣ Подготовка датасета

```
PDFs + Annotations (JSON)
        ↓
prepare_dataset.py
        ↓
Images + YOLO Labels
        ↓
dataset/yolo_dataset/
```

### 2️⃣ Обучение модели

```
yolo_dataset/
        ↓
train_model.py (YOLOv8)
        ↓
Trained Model (models/document_inspector_yolo.pt)
```

### 3️⃣ Inference через API

```
Client → POST /detect (PDF file)
        ↓
FastAPI Router (router.py)
        ↓
Service Layer (service.py)
        ↓
PDF → Images (utils.py)
        ↓
YOLOv8 Detector (detector.py)
        ↓
JSON Response ← Client
```

### 4️⃣ Inference с визуализацией

```
Client → POST /detect-visualize (PDF file)
        ↓
Service Layer
        ↓
PDF → Image → YOLOv8 → Annotated Image
        ↓
PNG Response ← Client
```

## 🎯 Классы детекции

| ID | Класс | Описание |
|----|-------|----------|
| 0 | `signature` | Подписи |
| 1 | `stamp` | Печати/штампы |
| 2 | `qr` | QR-коды |

## 📦 Основные зависимости

```
FastAPI >= 0.104.0          # Web framework
Uvicorn >= 0.24.0           # ASGI server
Pydantic >= 2.5.0           # Data validation

Ultralytics >= 8.0.0        # YOLOv8
PyMuPDF >= 1.23.0           # PDF processing
Pillow >= 10.0.0            # Image processing
OpenCV >= 4.8.0             # Computer vision

PyTorch >= 2.14.0           # Deep learning (auto-installed with ultralytics)
```

## 🚀 Скрипты и команды

### Подготовка датасета
```bash
cd backend/services/document_inspector
python prepare_dataset.py
```

### Обучение модели
```bash
python train_model.py
```

### Запуск API сервера
```bash
cd backend
python main.py
```

### Тестирование API
```bash
cd backend/services/document_inspector
python test_api.py
```

### Примеры использования
```bash
python example_usage.py
```

## 📄 Файлы конфигурации

| Файл | Назначение |
|------|------------|
| `requirements.txt` | Python зависимости |
| `data.yaml` | YOLO dataset config |
| `.env` | Environment variables (не в git) |
| `.gitignore` | Git ignore rules |

## 🔐 Переменные окружения

Создайте `.env` файл в `backend/`:

```env
# App
APP_ENV=development
HOST=0.0.0.0
PORT=8000

# Document Inspector
YOLO_MODEL_PATH=models/document_inspector_yolo.pt
CONFIDENCE_THRESHOLD=0.25
```

## 📊 Результаты обучения

После обучения создается структура:

```
runs/
└── train/
    └── document_inspector/
        ├── weights/
        │   ├── best.pt              # Best model
        │   └── last.pt              # Last epoch
        ├── results.png              # Training curves
        ├── confusion_matrix.png     # Confusion matrix
        ├── val_batch0_pred.jpg      # Validation predictions
        └── ...
```

## 🧪 Тестовые файлы

```
backend/services/document_inspector/
├── test_api.py              # API integration tests
├── example_usage.py         # Usage examples
└── test_result.png          # Example output (generated)
```

## 📝 Документация

| Файл | Содержание |
|------|-----------|
| `README.md` | Полная документация проекта |
| `QUICKSTART.md` | Быстрый старт (5 минут) |
| `CONTRIBUTING.md` | Руководство для контрибьюторов |
| `PROJECT_STRUCTURE.md` | Структура проекта (этот файл) |

## 🎨 Frontend (опционально)

Для создания веб-интерфейса можно добавить:

```
frontend/
├── index.html
├── app.js
└── styles.css
```

API уже готов для интеграции с любым frontend фреймворком (React, Vue, Angular).

## 🐳 Docker (будущее расширение)

```
InnovateX/
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## 📈 Метрики и мониторинг

Можно добавить:
- Prometheus metrics
- Grafana dashboards  
- Logging (structured logs)
- APM (Application Performance Monitoring)

## 🔒 Безопасность

- Валидация входных файлов (только PDF)
- Ограничение размера файла
- Rate limiting
- CORS настройки
- Secure headers

## ⚡ Production Considerations

1. **Gunicorn/Uvicorn workers**
2. **Nginx reverse proxy**
3. **SSL/TLS certificates**
4. **Load balancing**
5. **Caching (Redis)**
6. **Database connection pooling**
7. **Model versioning**

---

**Версия:** 1.0.0  
**Дата:** Ноябрь 2025  
**Статус:** ✅ Production Ready

