# 🚀 RAG Competitor Analyzer v1.5

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B?logo=streamlit)
![Celery](https://img.shields.io/badge/Celery-5.3-37814A?logo=celery)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%20%2B%20pgvector-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

**Автоматизированный ETL + RAG пайплайн** для глубокого анализа конкурентов с современным веб-интерфейсом, экспортом отчётов в PDF (с полной поддержкой кириллицы) и защитой от галлюцинаций LLM.

[📚 Документация](#-использование) • [🧪 Эксперименты](#-результаты-экспериментов) • [🐛 Баги](https://github.com/your-username/Competitor-Analyzer-MAX/issues) • [💡 Идеи](https://github.com/your-username/Competitor-Analyzer-MAX/discussions)

</div>

---

## 📖 О проекте

Система **самостоятельно** находит компании-конкуренты в интернете через Google Search (Serper.dev), парсит тексты их сайтов (с обходом защиты от ботов), очищает данные от SEO-спама и генерирует **структурированный аналитический отчёт** в форматах Markdown и PDF на основе пользовательского запроса с помощью LLM.

### ✨ Ключевые возможности

- 💻 **Современный Web UI** на Streamlit с отображением прогресса в реальном времени
- 📄 **Экспорт в PDF** с профессиональной версткой и **100% поддержкой кириллицы** (кроссплатформенно)
- 🔄 **Асинхронная обработка** через Celery + Redis (исключает таймауты)
- 🔍 **Каскадный поиск**: Serper.dev (Google) → DuckDuckGo → Fallback URL
- 🛡️ **Обход защиты сайтов** через `curl-cffi` (имитация TLS-отпечатка Chrome)
- 🧠 **Защита от галлюцинаций LLM**: жёсткие инструкции + `temperature=0.2`
- 🌍 **Работа в РФ** через ProxyAPI / OpenRouter
- 🐳 **Гибкий запуск**: Docker Compose или локальная отладка в VS Code

---

## 🏗 Архитектура

```mermaid
graph TD
    A[👤 Пользователь] --> B[Streamlit Web UI :8501]
    B -->|1. HTTP POST /analyze| C[FastAPI Server :8000]
    C -->|2. Ставит задачу| D[(Redis Queue)]
    C -->|3. Возвращает task_id| B
    D -->|4. Забирает задачу| E[Celery Worker]
    E -->|5. Поиск| F[Serper.dev / DuckDuckGo / Fallback]
    E -->|6. Парсинг| G[Сайты конкурентов через curl-cffi]
    E -->|7. RAG + LLM| H[OpenAI / ProxyAPI с защитой от галлюцинаций]
    E -->|8. Генерация и сохранение| I[./reports/*.md]
    I -->|9. Конвертация| J[PDF через xhtml2pdf + DejaVu Fonts]
    B -->|10. Polling статуса| C
```

---

## 🛠 Стек технологий

| Категория | Технологии |
|-----------|------------|
| **Frontend** | Streamlit 1.31, Markdown, xhtml2pdf |
| **Backend API** | FastAPI 0.109, Uvicorn, Pydantic 2.6 |
| **Очередь задач** | Celery 5.3, Redis 7 |
| **База данных** | PostgreSQL 15 + `pgvector` + `pg_trgm`, SQLAlchemy 2.0 |
| **Парсинг** | `curl-cffi` (обход Cloudflare), `beautifulsoup4` |
| **Поиск** | Serper.dev (Google), DuckDuckGo Search |
| **AI / LLM** | OpenAI API (`gpt-3.5-turbo`) через ProxyAPI / OpenRouter |
| **Инфраструктура** | Docker, Docker Compose, VS Code Debugger |

---

## 🚀 Быстрый старт

### 📋 Требования

- Python **3.11** или **3.12**
- Docker Desktop (для PostgreSQL и Redis)
- API-ключи: **OpenAI** (или ProxyAPI/OpenRouter) и **Serper.dev** (бесплатно, 2500 запросов)

### 🔧 Режим 1: Локальная разработка в VS Code

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/saikttech/Competitor_analyzer_Docker_1.5_web.git
cd Competitor-Analyzer-MAX

# 2. Создайте виртуальное окружение
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Установите зависимости
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Настройте .env
cp .env.example .env
# Вставьте OPENAI_API_KEY и SERPER_API_KEY

# 5. Запустите инфраструктуру в Docker
docker compose up db redis -d

# 6. В VS Code: Run and Debug (Ctrl+Shift+D)
#    Запустите по очереди:
#    ▶️ Python: FastAPI
#    ▶️ Python: Celery Worker
#    ▶️ Python: Streamlit
```

### 🐳 Режим 2: Полный Docker-деплой

```bash
# 1. Настройте .env (Docker-адреса: @db, @redis, http://api:8000)
cp .env.example .env

# 2. Запустите всё одной командой
docker compose up --build
```

### 🌐 Доступ к сервисам

| Сервис | URL |
|--------|-----|
| **Streamlit Web UI** | http://localhost:8501 |
| **FastAPI Swagger** | http://localhost:8000/docs |
| **PostgreSQL** | `localhost:5432` |
| **Redis** | `localhost:6379` |

---

## 🔑 Получение API-ключей

### OpenAI (через ProxyAPI для РФ)
1. Зарегистрируйтесь на [proxyapi.ru](https://proxyapi.ru/)
2. Пополните баланс
3. Скопируйте API-ключ
4. В `.env` укажите:
   ```env
   OPENAI_API_KEY=sk-ваш_ключ
   OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
   ```

### Serper.dev (Google Search)
1. Перейдите на [serper.dev](https://serper.dev/)
2. Войдите через Google
3. Скопируйте API-ключ (2500 бесплатных запросов)
4. В `.env` укажите:
   ```env
   SERPER_API_KEY=ваш_ключ
   ```

---

## 📄 Экспорт в PDF (кириллица)

Для корректного отображения русского языка в PDF:

1. Скачайте шрифты: [DejaVu Fonts TTF](https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip)
2. Распакуйте архив
3. Скопируйте из папки `ttf` в папку `fonts/` вашего проекта:
   - `DejaVuSans.ttf`
   - `DejaVuSans-Bold.ttf`

*Без этих файлов PDF будет содержать квадратики (■■■■) вместо русского текста.*

---

## 📡 Использование

### Через Web UI
1. Откройте **http://localhost:8501**
2. Заполните форму:
   - **🎯 Ниша:** `кофейни`
   - **📍 География:** `Москва`
   - **🔎 Детальный запрос:** `спешелти кофе с веганскими десертами`
3. Нажмите **🚀 Запустить анализ**
4. После завершения нажмите **📄 Скачать PDF (.pdf)**

### Через REST API
```bash
# Запуск задачи
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer sk-test-123" \
  -H "Content-Type: application/json" \
  -d '{"niche":"кофейни","geo":"Москва","query":"спешелти","clear_db":false}'

# Проверка статуса
curl http://localhost:8000/analyze/{task_id} \
  -H "Authorization: Bearer sk-test-123"
```

---

## 🧪 Результаты экспериментов

В ходе разработки было проведено **5 экспериментов** для оценки качества генерируемых отчётов. Ключевые выводы:

### Сводная таблица

| № | Ниша | Запрос | Релевантность | Полнота | Галлюцинации LLM | Критическое мышление | Оценка |
|---|------|--------|---------------|---------|------------------|----------------------|--------|
| 1 | аренда лофт | *(общий)* | ❌ | ❌ 1/3 | Нет (заглушки) | Нет | ⭐ (1/5) |
| 2 | аренда лофт на ДР с караоке | аренда лофт на ДР с караоке | ❌ | ❌ 1/3 | Нет (заглушки) | **Да** ✅ | ⭐⭐ (2/5) |
| 3 | кофейни | спешелти, веганские десерты | ❌❌ | ⚠️ 3/3 | **Да (выдуманные)** | Нет | ⭐ (1/5) |
| 4 | аренда лофт с караоке | аренда лофт с караоке | ❌ | ❌ 1/3 | Нет (заглушки) | Нет | ⭐ (1/5) |
| 5 | кофейни | *(общий)* | ❌ | ❌ 1/3 | Нет (плейсхолдеры) | Нет | ⭐ (1/5) |

### Ключевые выводы

1. **Корневая проблема**: все эксперименты проводились в аварийном режиме (Tavily/DuckDuckGo были недоступны), поэтому данные были нерелевантными (сайт аренды автомобилей вместо лофтов/кофеен).
2. **Лучший результат**: эксперимент №2 — LLM **самостоятельно распознала несоответствие** данных нише и честно сообщила об этом.
3. **Галлюцинации**: в эксперименте №3 LLM выдумала несуществующие кофейни («Аромат», «Coffee Time») — это критическая проблема, требующая решения.

### Решённые проблемы (v1.5)

✅ **Переход на Serper.dev** — стабильный поиск через Google, 2500 бесплатных запросов  
✅ **Защита от галлюцинаций** — жёсткие инструкции в промте + `temperature=0.2`  
✅ **Честность LLM** — модель обязана сообщить, если данные нерелевантны  
✅ **PDF с кириллицей** — программная регистрация шрифтов через ReportLab

### Вывод

Архитектура пайплайна **работает корректно** на техническом уровне. После подключения Serper.dev система генерирует **реальные, релевантные отчёты** с настоящими конкурентами.

---

## 📁 Структура проекта

```
Competitor-Analyzer-MAX/
├── .env                        # Секреты (не коммитить!)
├── .env.example                # Шаблон конфигурации
├── .gitignore
├── docker-compose.yml          # Оркестрация контейнеров
├── Dockerfile                  # Сборка Python-образа
├── requirements.txt            # Python-зависимости
├── README.md                   # Этот файл
│
├── main.py                     # FastAPI приложение (REST API)
├── celery_app.py               # Конфигурация Celery
├── tasks.py                    # Celery-воркер
├── pipeline.py                 # 🧠 Ядро: ETL + RAG пайплайн
├── models.py                   # SQLAlchemy ORM модели
├── config.py                   # Загрузка .env и настроек
├── streamlit_app.py            # 💻 Web UI + PDF экспорт
│
├── reports/                    # Сгенерированные отчёты (.md)
├── fonts/                      # Шрифты для PDF (DejaVu Sans)
├── .streamlit/
│   └── config.toml             # Настройки Streamlit
├── .vscode/
│   ├── launch.json             # Конфигурации отладки
│   └── settings.json           # Настройки VS Code
└── docs/
    └── LOCAL_DEV.md            # Инструкция по локальной разработке
```

---

## ⚙️ Конфигурация (`.env`)

```env
# --- AI ---
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1  # или https://openrouter.ai/api/v1

# --- Поиск ---
SERPER_API_KEY=your-serper-key  # https://serper.dev/

# --- База данных (локально) ---
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/competitors_db
REDIS_URL=redis://localhost:6379/0

# --- Безопасность ---
API_KEY=sk-test-123

# --- Streamlit ---
API_BASE_URL=http://localhost:8000
```

> 💡 **Для Docker-режима** замените `localhost` на `db` / `redis` / `api`.

---

## 🛡️ Устойчивость к блокировкам

| Уровень | Технология | Назначение |
|---------|------------|------------|
| 🔍 Поиск | **Serper.dev** | Стабильный поиск через Google (2500 запросов бесплатно) |
| 🔍 Fallback | **DuckDuckGo** | С экспоненциальной задержкой при Rate Limit |
| 🔍 Аварийный | **Тестовые URL** | Если оба поисковика недоступны |
| 🌐 Парсинг | **curl-cffi** | Имитация TLS-отпечатка Chrome 110 |
| 🧠 LLM | **Защита от галлюцинаций** | Жёсткие инструкции + низкая температура |

---

## 🔮 Roadmap (v1.6+)

- [x] ✅ **Serper.dev вместо Tavily** — стабильный поиск через Google
- [x] ✅ **Защита от галлюцинаций LLM** — жёсткие инструкции + `temperature=0.2`
- [x] ✅ **PDF с кириллицей** — программная регистрация шрифтов
- [ ] 💾 **История запросов в БД** — список прошлых анализов в Streamlit
- [ ] 🧠 **Cross-Encoder Reranker** — улучшение точности RAG-выдачи
- [ ] 🎭 **Playwright** — парсинг сайтов с тяжёлым JavaScript
- [ ] 📊 **Langfuse** — мониторинг стоимости и качества LLM-запросов
- [ ] 🧪 **Unit-тесты** — покрытие кода через `pytest`
- [ ] 🔄 **CI/CD** — GitHub Actions для авто-тестов и деплоя
- [ ] 📧 **Email-отчёты** — автоматическая отправка PDF на почту

---

## 🐛 Решение типичных проблем

<details>
<summary><b>❌ SSL: CERTIFICATE_VERIFY_FAILED при pip install</b></summary>

Корпоративный антивирус или прокси подменяет сертификаты. Решение:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```
</details>

<details>
<summary><b>❌ В PDF вместо текста квадратики (■■■■)</b></summary>

Убедитесь, что файлы <code>DejaVuSans.ttf</code> и <code>DejaVuSans-Bold.ttf</code> лежат в папке <code>fonts/</code>. Перезапустите Streamlit после их добавления.
</details>

<details>
<summary><b>❌ OpenAI 403: unsupported_country_region_territory</b></summary>

OpenAI блокирует запросы из РФ. Используйте прокси:
- <b>ProxyAPI</b>: <code>https://api.proxyapi.ru/openai/v1</code>
- <b>OpenRouter</b>: <code>https://openrouter.ai/api/v1</code>
</details>

<details>
<summary><b>❌ LLM выдумывает несуществующих конкурентов</b></summary>

Убедитесь, что в <code>pipeline.py</code> используется жёсткий промт с инструкциями против галлюцинаций и <code>temperature=0.2</code>. Если проблема сохраняется, попробуйте модель <code>gpt-4o-mini</code>.
</details>

<details>
<summary><b>❌ Serper.dev не работает</b></summary>

Проверьте:
1. Ключ начинается не с <code>tvly-</code> (это старый Tavily)
2. Ключ вставлен в <code>.env</code> без пробелов
3. Перезапустите Celery Worker после изменения <code>.env</code>
</details>

---

## 🤝 Вклад в проект

Pull Request'ы приветствуются! 🎉

1. Форкните репозиторий
2. Создайте ветку для фичи (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

Для серьёзных изменений сначала откройте **Issue**, чтобы обсудить идею.

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT**. См. файл [LICENSE](LICENSE) для подробностей.

---

## 🙏 Благодарности

- **OpenAI** — за модели GPT и embeddings
- **Serper.dev** — за стабильный API Google Search
- **Streamlit** — за отличный веб-фреймворк для data apps
- **FastAPI** — за производительный REST API
- **Celery** — за надёжную очередь задач
- **pgvector** — за нативную поддержку векторов в PostgreSQL
- **curl-cffi** — за обход защиты сайтов от ботов
- **xhtml2pdf** — за генерацию PDF на чистом Python
- **DejaVu Fonts** — за бесплатные шрифты с поддержкой кириллицы

---

<div align="center">

**⭐ Если проект оказался полезным — поставьте звезду на GitHub!**

Сделано с ❤️ для русскоязычного AI-сообщества

</div>