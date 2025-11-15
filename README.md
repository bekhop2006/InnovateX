# 🔍 Document Inspector - Цифровой Инспектор

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Автоматическое обнаружение ключевых элементов в строительных документах с использованием Computer Vision (YOLOv8).

## 📋 Описание проекта

**Document Inspector** - это инструмент на базе Computer Vision, который автоматически находит и отмечает три ключевых элемента на строительных документах:

1. **Подписи** (Signatures)
2. **Печати/Штампы** (Stamps)
3. **QR-коды** (QR codes)

Проект использует YOLOv8 (You Only Look Once v8) для детекции объектов и FastAPI для предоставления REST API.

## 🎯 Возможности

- ✅ Автоматическое обнаружение подписей, печатей и QR-кодов
- ✅ Обработка многостраничных PDF документов
- ✅ REST API для интеграции с другими системами
- ✅ Визуализация результатов с bounding boxes
- ✅ Возврат результатов в структурированном JSON формате
- ✅ Настраиваемый порог уверенности (confidence threshold)

## 🏗️ Архитектура

```
InnovateX/
├── backend/
│   ├── main.py                          # FastAPI приложение
│   ├── requirements.txt                 # Зависимости
│   └── services/
│       └── document_inspector/          # Сервис Document Inspector
│           ├── __init__.py
│           ├── router.py                # API эндпоинты
│           ├── schemas.py               # Pydantic модели
│           ├── service.py               # Бизнес-логика
│           ├── detector.py              # YOLOv8 detector
│           ├── utils.py                 # Утилиты (PDF→Image)
│           ├── prepare_dataset.py       # Подготовка датасета
│           └── train_model.py           # Обучение модели
├── dataset/
│   ├── pdfs/                            # Исходные PDF документы
│   ├── selected_annotations.json        # Аннотации (ground truth)
│   └── yolo_dataset/                    # Подготовленный датасет
│       ├── images/
│       │   ├── train/
│       │   └── val/
│       ├── labels/
│       │   ├── train/
│       │   └── val/
│       └── data.yaml
├── models/
│   └── document_inspector_yolo.pt       # Обученная модель
└── README.md
```

## 🚀 Быстрый старт

### 1️⃣ Установка зависимостей

```bash
# Перейти в директорию backend
cd backend

# Создать виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt
```

### 2️⃣ Подготовка датасета

Конвертация PDF документов и аннотаций в формат YOLO:

```bash
cd backend/services/document_inspector
python prepare_dataset.py
```

Скрипт выполнит:
- Конвертацию страниц PDF в изображения
- Преобразование аннотаций в YOLO формат
- Разделение на train/val выборки (80/20)
- Создание `data.yaml` для обучения

Результат сохраняется в `dataset/yolo_dataset/`

### 3️⃣ Обучение модели

```bash
python train_model.py
```

Параметры обучения (можно изменить в `train_model.py`):
- **Модель**: `yolov8n.pt` (nano, быстрая)
- **Epochs**: 100
- **Image size**: 640
- **Batch size**: 16

Альтернативные модели:
- `yolov8s.pt` - small (больше точности, медленнее)
- `yolov8m.pt` - medium
- `yolov8l.pt` - large
- `yolov8x.pt` - extra large

После обучения модель сохраняется в `models/document_inspector_yolo.pt`

### 4️⃣ Запуск API сервера

```bash
# Вернуться в директорию backend
cd ../../..

# Запустить сервер
python main.py
```

Сервер запустится на `http://localhost:8000`

API документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Health Check

Проверка готовности сервиса:

```bash
GET /api/document-inspector/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "models/document_inspector_yolo.pt"
}
```

### Детекция элементов (JSON)

Обнаружение подписей, печатей и QR-кодов:

```bash
POST /api/document-inspector/detect
```

**Параметры:**
- `file`: PDF файл (multipart/form-data)
- `conf_threshold`: порог уверенности 0.0-1.0 (по умолчанию 0.25)

**Пример запроса (curl):**
```bash
curl -X POST "http://localhost:8000/api/document-inspector/detect?conf_threshold=0.5" \
  -F "file=@/path/to/document.pdf"
```

**Пример запроса (Python):**
```python
import requests

url = "http://localhost:8000/api/document-inspector/detect"
files = {"file": open("document.pdf", "rb")}
params = {"conf_threshold": 0.5}

response = requests.post(url, files=files, params=params)
result = response.json()
print(result)
```

**Ответ:**
```json
{
  "document_name": "example.pdf",
  "total_pages": 3,
  "pages": [
    {
      "page_number": 1,
      "page_size": {
        "width": 1190,
        "height": 1684
      },
      "annotations": [
        {
          "id": "detection_1",
          "category": "signature",
          "bbox": {
            "x": 510.5,
            "y": 146.2,
            "width": 250.0,
            "height": 98.9
          },
          "confidence": 0.95
        },
        {
          "id": "detection_2",
          "category": "stamp",
          "bbox": {
            "x": 709.0,
            "y": 1184.0,
            "width": 208.8,
            "height": 218.1
          },
          "confidence": 0.92
        }
      ]
    }
  ],
  "processing_time": 2.45
}
```

### Детекция с визуализацией (Image)

Возвращает изображение с нарисованными bounding boxes:

```bash
POST /api/document-inspector/detect-visualize
```

**Параметры:**
- `file`: PDF файл (multipart/form-data)
- `conf_threshold`: порог уверенности 0.0-1.0 (по умолчанию 0.25)
- `page_number`: номер страницы для визуализации (по умолчанию 1)

**Пример запроса (curl):**
```bash
curl -X POST "http://localhost:8000/api/document-inspector/detect-visualize?page_number=1" \
  -F "file=@/path/to/document.pdf" \
  --output result.png
```

**Пример запроса (Python):**
```python
import requests
from PIL import Image
from io import BytesIO

url = "http://localhost:8000/api/document-inspector/detect-visualize"
files = {"file": open("document.pdf", "rb")}
params = {"conf_threshold": 0.5, "page_number": 1}

response = requests.post(url, files=files, params=params)

# Сохранить изображение
image = Image.open(BytesIO(response.content))
image.save("result.png")
```

## 🔧 Конфигурация

### Настройка обучения

Отредактируйте параметры в `backend/services/document_inspector/train_model.py`:

```python
# Выбор модели
MODEL_NAME = "yolov8n.pt"  # yolov8n, yolov8s, yolov8m, yolov8l, yolov8x

# Параметры обучения
EPOCHS = 100      # Количество эпох
IMGSZ = 640       # Размер изображения
BATCH = 16        # Размер батча
```

### Настройка API

Отредактируйте `backend/.env` (создайте файл при необходимости):

```env
HOST=0.0.0.0
PORT=8000
APP_ENV=development
```

## 📊 Формат данных

### Входной формат (Аннотации)

Аннотации в `dataset/selected_annotations.json`:

```json
{
  "document.pdf": {
    "page_1": {
      "page_size": {"width": 1190, "height": 1684},
      "annotations": [
        {
          "annotation_1": {
            "category": "signature",
            "bbox": {"x": 100, "y": 200, "width": 150, "height": 80},
            "area": 12000
          }
        }
      ]
    }
  }
}
```

### YOLO формат (для обучения)

Текстовые файлы `.txt` в `dataset/yolo_dataset/labels/`:

```
class_id x_center y_center width height
0 0.523456 0.678901 0.125678 0.047890
```

Где:
- `class_id`: 0=signature, 1=stamp, 2=qr
- Остальные значения нормализованы [0, 1]

## 📈 Метрики качества

После обучения модель оценивается по метрикам:

- **mAP50**: Mean Average Precision при IoU=0.5
- **mAP50-95**: mAP при IoU от 0.5 до 0.95
- **Precision**: Точность (TP / (TP + FP))
- **Recall**: Полнота (TP / (TP + FN))

Результаты обучения сохраняются в `runs/train/document_inspector/`

## 🧪 Тестирование

### Тест через API

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/document-inspector/health")
print(response.json())

# Детекция
with open("test_document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/document-inspector/detect",
        files={"file": f},
        params={"conf_threshold": 0.3}
    )
    print(response.json())
```

### Тест inference напрямую

```python
from ultralytics import YOLO
from PIL import Image

# Загрузить модель
model = YOLO("models/document_inspector_yolo.pt")

# Запустить inference
results = model.predict("test_image.jpg", conf=0.25)

# Вывести результаты
for result in results:
    result.show()  # Показать изображение
    print(result.boxes)  # Координаты боксов
```

## 🛠️ Технологии

### Backend
- **FastAPI** - современный веб-фреймворк
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер

### Computer Vision
- **Ultralytics YOLOv8** - object detection
- **PyMuPDF (fitz)** - обработка PDF
- **Pillow (PIL)** - обработка изображений
- **OpenCV** - компьютерное зрение

### ML
- **PyTorch** - deep learning framework
- **CUDA** - GPU acceleration (опционально)

## 📝 Примеры использования

### Интеграция в Python приложение

```python
from document_inspector.detector import DocumentDetector
from document_inspector.utils import pdf_to_images

# Инициализация детектора
detector = DocumentDetector("models/document_inspector_yolo.pt")

# Конвертация PDF в изображения
images = pdf_to_images("document.pdf")

# Обработка каждой страницы
for image, page_num in images:
    detections = detector.detect(image, conf_threshold=0.5)
    
    print(f"Page {page_num}: {len(detections)} detections")
    for det in detections:
        print(f"  - {det['category']}: {det['confidence']:.2%}")
```

### Batch обработка

```python
import os
from pathlib import Path

pdf_dir = Path("documents/")
results = {}

for pdf_file in pdf_dir.glob("*.pdf"):
    print(f"Processing {pdf_file.name}...")
    
    response = requests.post(
        "http://localhost:8000/api/document-inspector/detect",
        files={"file": open(pdf_file, "rb")}
    )
    
    results[pdf_file.name] = response.json()

# Сохранить результаты
import json
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## 🐛 Troubleshooting

### Проблема: Model not loaded

**Решение:** Убедитесь, что модель обучена и находится в `models/document_inspector_yolo.pt`

```bash
# Проверить наличие модели
ls models/document_inspector_yolo.pt

# Если нет, обучить модель
cd backend/services/document_inspector
python train_model.py
```

### Проблема: Out of memory при обучении

**Решение:** Уменьшите batch size в `train_model.py`:

```python
BATCH = 8  # Вместо 16
```

### Проблема: Низкая точность детекции

**Решение:**
1. Увеличьте количество эпох обучения
2. Используйте более крупную модель (yolov8s.pt вместо yolov8n.pt)
3. Увеличьте размер датасета
4. Настройте аугментацию данных

### Проблема: PDF не конвертируется

**Решение:** Проверьте, что установлен PyMuPDF:

```bash
pip install pymupdf --upgrade
```

## 📄 Требования к сдаче

✅ **Презентация**: Визуализация подхода, методов и результатов

✅ **Видео**: Демонстрация решения (до 3 минут)

✅ **Код**: Доступ к репозиторию на GitHub

✅ **README.md**: Инструкции по запуску (этот файл)

✅ **requirements.txt**: Список зависимостей

✅ **Визуальный результат**: API возвращает изображения с bounding boxes

## 👥 Авторы

**InnovateX Team**

## 📜 Лицензия

MIT License

## 🙏 Благодарности

- Ultralytics за YOLOv8
- FastAPI за отличный фреймворк
- Организаторам хакатона за интересную задачу

---

**Дата создания:** Ноябрь 2025

**Задача:** Автоматизация рутинной части инспекции строительных документов

