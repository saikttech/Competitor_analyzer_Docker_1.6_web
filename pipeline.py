import uuid
import logging
import time
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Подавление предупреждения asyncio на Windows
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import requests as http_requests
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL

logger = logging.getLogger(__name__)

# Инициализация OpenAI
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# Абсолютный путь к папке reports
REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

logger.info(f"📁 Папка для отчётов: {REPORTS_DIR}")
logger.info(f"🔑 OpenAI Base URL: {OPENAI_BASE_URL}")

# Проверка доступных поисковых API
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if SERPER_API_KEY:
    logger.info("✅ Serper.dev (Google Search) доступен")
else:
    logger.warning("⚠️ SERPER_API_KEY не найден. Serper.dev недоступен.")


# ==============================================================================
# 🔍 ПОИСКОВЫЕ МОДУЛИ
# ==============================================================================

def search_with_serper(query: str, limit: int = 5) -> List[str]:
    """Поиск через Serper.dev API (Google Search) — основной метод"""
    logger.info(f"🔍 Serper (Google): {query}")

    try:
        response = http_requests.post(
            "https://google.serper.dev/search",
            json={
                "q": query,
                "gl": "ru",
                "hl": "ru",
                "num": limit
            },
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        urls = []

        for item in data.get("organic", []):
            link = item.get("link", "")
            if link.startswith("http"):
                urls.append(link)
                title = item.get("title", "Без заголовка")
                logger.info(f"   {len(urls)}. {link} — {title}")

        logger.info(f"✅ Serper нашёл {len(urls)} результатов")
        return urls

    except http_requests.exceptions.HTTPError as e:
        logger.error(f"❌ Ошибка Serper HTTP: {e.response.status_code} — {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"❌ Ошибка Serper: {type(e).__name__}: {e}")
        return []


def search_with_duckduckgo(query: str, limit: int = 5) -> List[str]:
    """Поиск через DuckDuckGo (fallback)"""
    logger.info(f"🔍 DuckDuckGo (fallback): {query}")

    try:
        from duckduckgo_search import DDGS
        time.sleep(1.5)
        ddgs = DDGS()
        results = ddgs.text(query, max_results=limit)

        if not results:
            logger.warning("   ⚠️ DuckDuckGo вернул пустой результат")
            return []

        urls = []
        for r in results:
            if isinstance(r, dict):
                url = r.get('href') or r.get('link') or r.get('url')
                if url and url.startswith('http'):
                    urls.append(url)

        logger.info(f"✅ DuckDuckGo нашёл {len(urls)} результатов")
        for i, url in enumerate(urls, 1):
            logger.info(f"   {i}. {url}")
        return urls

    except Exception as e:
        error_str = str(e).lower()
        if "ratelimit" in error_str or "403" in error_str:
            logger.warning(f"⚠️ DuckDuckGo заблокировал запросы (Rate Limit)")
        else:
            logger.error(f"❌ Ошибка DuckDuckGo: {type(e).__name__}: {e}")
        return []


def search_competitors(niche: str, geo: str, query: str, limit: int = 5) -> List[str]:
    """Каскадный поиск конкурентов: Serper → DuckDuckGo → Fallback"""
    search_query = f"{niche} {geo} {query}"
    logger.info(f"\n🔎 Итоговый поисковый запрос: '{search_query}'")

    # Приоритет 1: Serper.dev (Google Search)
    if SERPER_API_KEY:
        logger.info("🥇 Пробуем Serper.dev (Google Search)...")
        urls = search_with_serper(search_query, limit)
        if urls:
            return urls
        logger.warning("⚠️ Serper не вернул результатов, переключаюсь на DuckDuckGo...")

    # Приоритет 2: DuckDuckGo
    logger.info("🥈 Пробуем DuckDuckGo...")
    urls = search_with_duckduckgo(search_query, limit)
    if urls:
        return urls

    # Приоритет 3: Аварийный режим
    logger.warning("🚨 Все поисковики не дали результатов. Включаю аварийный режим.")
    fallback_urls = [
        "https://bash.today/",
        "https://surprise.me/msk/loft/",
        "https://www.afisha.ru/msk/place/loft/"
    ]
    logger.info(f"✅ Использовано {len(fallback_urls)} тестовых URL")
    return fallback_urls


# ==============================================================================
# 🌐 ПАРСИНГ
# ==============================================================================

def parse_website(url: str) -> Optional[str]:
    """Парсинг текста с сайта с обходом защиты от ботов"""
    logger.info(f"🌐 Парсинг: {url}")

    try:
        response = curl_requests.get(
            url,
            impersonate="chrome110",
            timeout=15.0,
            allow_redirects=True
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Удаление мусорных элементов
        for element in soup(["script", "style", "nav", "footer", "header",
                             "aside", "iframe", "noscript", "form", "svg"]):
            element.decompose()

        text = soup.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())

        if len(text) > 5000:
            text = text[:5000] + "..."

        logger.info(f"✅ Получено {len(text)} символов")
        return text

    except Exception as e:
        logger.warning(f"❌ Ошибка парсинга {url}: {type(e).__name__}: {e}")
        return None


# ==============================================================================
# 🧠 ГЕНЕРАЦИЯ ОТЧЁТА
# ==============================================================================

def generate_report(niche: str, geo: str, query: str, collected_data: str) -> str:
    """Генерация отчёта через LLM с ЖЁСТКОЙ защитой от галлюцинаций"""
    logger.info("🧠 Генерация отчёта через OpenAI...")

    prompt = f"""Ты — профессиональный бизнес-аналитик с 10-летним опытом.

⚠️ КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА (СТРОГО СОБЛЮДАТЬ):
1. Внимательно проанализируй предоставленные ниже "Данные конкурентов".
2. ЕСЛИ эти данные НЕ СООТВЕТСТВУЮТ запрошенной нише "{niche}" (например, текст про аренду автомобилей при запросе о кофейнях или лофтах), ты ДОЛЖЕН честно написать об этом в самом первом абзаце отчёта.
3. ЗАПРЕЩЕНО выдумывать несуществующие компании, названия или факты.
4. ЗАПРЕЩЕНО использовать заглушки вроде "Конкурент 2", "[Название]", "Описание сильной стороны". Если в данных только 1 компания — пиши только про неё.
5. ЗАПРЕЩЕНО давать абсурдные рекомендации (например, "добавьте веганские десерты к аренде автомобилей").
6. Если данных недостаточно для полноценного анализа, честно напиши: "На основе предоставленных данных невозможно провести полный анализ конкурентов в нише '{niche}'. Рекомендуется повторить поиск с другими параметрами."

Если данные релевантны и достаточны, сформируй структурированный отчёт в Markdown формате:

## 📊 Краткое резюме рынка
(2-3 предложения о реальном состоянии рынка на основе предоставленных данных)

## 🏆 Найденные конкуренты
(Перечисли ТОЛЬКО те компании, которые реально упомянуты в данных. Для каждой: название, сильные стороны, особенности. Не выдумывай!)

## 💡 Рекомендации по улучшению
(3-5 конкретных рекомендаций, основанных ИСКЛЮЧИТЕЛЬНО на предоставленных данных)

## ⚠️ Потенциальные риски
(2-3 реальных риска)

## 📈 Итоговые выводы
(Краткое резюме)

---

Данные конкурентов (тексты с их сайтов):
{collected_data}

---

Ниша: {niche}
Регион: {geo}
Запрос пользователя: {query}

Отвечай на русском языке. Будь конкретным, практичным и ЧЕСТНЫМ."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )

        report = response.choices[0].message.content
        logger.info(f"✅ Отчёт сгенерирован ({len(report)} символов)")
        return report

    except Exception as e:
        logger.error(f"❌ Ошибка генерации отчёта: {type(e).__name__}: {e}")
        logger.error("   Полная трассировка:", exc_info=True)
        raise


# ==============================================================================
# 🚀 ОСНОВНОЙ ПАЙПЛАЙН
# ==============================================================================

def run_pipeline(niche: str, geo: str, query: str, clear_db: bool) -> Dict:
    """Основной ETL + RAG пайплайн"""
    logger.info("=" * 60)
    logger.info(f"🚀 Запуск пайплайна анализа конкурентов")
    logger.info(f"   Ниша: {niche}")
    logger.info(f"   География: {geo}")
    logger.info(f"   Запрос: {query}")
    logger.info(f"   Очистка БД: {clear_db}")
    logger.info(f"   Папка отчётов: {REPORTS_DIR}")
    logger.info("=" * 60)

    # === ЭТАП 1: Поиск конкурентов ===
    logger.info("\n📍 ЭТАП 1: Поиск конкурентов...")
    urls = search_competitors(niche, geo, query)

    if not urls:
        raise ValueError("❌ Не найдено конкурентов (даже в аварийном режиме).")

    # === ЭТАП 2: Парсинг сайтов ===
    logger.info(f"\n📍 ЭТАП 2: Парсинг {len(urls)} сайтов...")
    collected_data = []
    successful_parses = 0

    for i, url in enumerate(urls, 1):
        logger.info(f"\n[{i}/{len(urls)}] Обработка: {url}")
        text = parse_website(url)

        if text and len(text) > 100:
            collected_data.append(f"Источник: {url}\nСодержимое:\n{text}")
            successful_parses += 1
        else:
            logger.warning(f"   ⚠️ Пропущен (недостаточно данных)")

    logger.info(f"\n✅ Успешно спарсено: {successful_parses}/{len(urls)} сайтов")

    if not collected_data:
        raise ValueError("❌ Не удалось получить данные с сайтов конкурентов.")

    full_text = "\n\n" + "=" * 60 + "\n\n".join(collected_data)

    # === ЭТАП 3: Генерация отчёта ===
    logger.info("\n📍 ЭТАП 3: Генерация отчёта через AI...")
    report_markdown = generate_report(niche, geo, query, full_text)

    # === ЭТАП 4: Сохранение отчёта ===
    logger.info("\n📍 ЭТАП 4: Сохранение отчёта...")
    filename = f"report_{uuid.uuid4().hex[:8]}.md"
    file_path = REPORTS_DIR / filename

    logger.info(f"   Путь сохранения: {file_path}")

    try:
        file_path.write_text(report_markdown, encoding="utf-8")

        if file_path.exists():
            file_size = file_path.stat().st_size
            logger.info(f"✅ Отчёт успешно сохранён: {file_path} ({file_size} байт)")
        else:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Файл не создан по пути {file_path}")
            raise RuntimeError("Не удалось сохранить файл отчёта")

    except Exception as e:
        logger.error(f"❌ Ошибка сохранения: {type(e).__name__}: {e}")
        logger.error("   Полная трассировка:", exc_info=True)
        raise

    logger.info("\n" + "=" * 60)
    logger.info("🎉 Пайплайн завершён успешно!")
    logger.info("=" * 60 + "\n")

    return {
        "competitors_found": len(urls),
        "competitors_parsed": successful_parses,
        "report_path": str(file_path),
        "report_filename": filename,
        "report_size_bytes": file_path.stat().st_size,
        "summary": report_markdown[:1000] + "..." if len(report_markdown) > 1000 else report_markdown,
        "full_report": report_markdown
    }