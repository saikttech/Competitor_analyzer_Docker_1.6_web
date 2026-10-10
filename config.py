import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# ==============================================================================
# 🗄️ База данных и Очередь задач
# ==============================================================================
# Для локальной разработки: localhost (Docker пробрасывает порты)
# Для Docker Compose: db / redis (имена контейнеров)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/competitors_db"
)
REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# ==============================================================================
# 🤖 Настройки AI (LLM)
# ==============================================================================
# OpenAI (или совместимый прокси: ProxyAPI, OpenRouter)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://api.openai.com/v1"
)

# ==============================================================================
# 🔍 Поисковые API
# ==============================================================================
# Serper.dev (Google Search) — основной поисковик
# Получить ключ: https://serper.dev/ (2500 бесплатных запросов)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# ==============================================================================
# 🔒 Безопасность
# ==============================================================================
# API ключ для защиты эндпоинтов FastAPI
API_KEY = os.getenv("API_KEY", "sk-test-123")

# ==============================================================================
# 💻 Настройки Frontend (Streamlit)
# ==============================================================================
# Адрес, по которому Streamlit обращается к FastAPI
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ==============================================================================
# 📁 Пути
# ==============================================================================
# Корневая директория проекта (где лежит config.py)
BASE_DIR = Path(__file__).resolve().parent

# Папка для сохранения сгенерированных отчётов
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Папка для шрифтов (используется при генерации PDF)
FONTS_DIR = BASE_DIR / "fonts"
FONTS_DIR.mkdir(exist_ok=True)

# ==============================================================================
# ☁️ S3 Хранилище (Опционально)
# ==============================================================================
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "ru-central1")