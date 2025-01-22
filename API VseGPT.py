import asyncio
from openai import AsyncOpenAI
from typing import List

# Конфигурация
API_KEY = "ваш_API_ключ"  # Замените на ваш API-ключ
BASE_URL = "https://api.vsegpt.ru/v1"
MAX_CHUNK_SIZE = 2000  # Максимальная длина текста для одного запроса
SLEEP_TIME = 1  # Задержка между запросами

# Инициализация клиента
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

# Шаблон для запросов
PROMPT_CONSPECT_WRITER = """
Привет!
Ты опытный технический писатель. Ниже, я предоставляю тебе полный текст лекции а так же ту часть,
с которой ты будешь работать.

Ты великолепно знаешь русский язык и отлично владеешь этой темой.

Тема занятия: {topic}

Полный текст лекции:
{full_text}

Сейчас я дам тебе ту часть, с котороый ты будешь работать. Я попрошу тебя написать конспект лекции.
А так же блоки кода.

Ты пишешь в формате Markdown. Начни с заголовка 2го уровня.
В тексте используй заголовки 3го уровня.

Используй блоки кода по необходимости.

Отрезок текста с которым ты работаешь, с которого ты будешь работать:
{text_to_work}
"""

async def get_ai_request(prompt: str, model: str = "openai/gpt-4o-mini", max_tokens: int = 16000, temperature: float = 0.7) -> str:
    """
    Отправляет асинхронный запрос к API VseGPT и возвращает ответ.
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return ""

def split_text(text: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> List[str]:
    """
    Разделяет текст на части заданного размера.
    """
    if not text:
        return []
    
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size должен быть положительным числом")
    
    return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def save_to_markdown(data: List[str], output_file: str = "output.md"):
    """
    Сохраняет результаты в формате Markdown.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as md_file:
            for item in data:
                if item:  # Пропускаем пустые результаты
                    md_file.write(f"---\n{item}\n---\n")
        print(f"Файл успешно сохранен: {output_file}")
    except IOError as e:
        print(f"Ошибка при записи файла: {e}")

async def process_chunk(chunk: str, full_text: str, topic: str) -> str:
    """
    Обрабатывает один фрагмент текста.
    """
    prompt = PROMPT_CONSPECT_WRITER.format(
        topic=topic,
        full_text=full_text,
        text_to_work=chunk
    )
    result = await get_ai_request(prompt)
    await asyncio.sleep(SLEEP_TIME)
    return result

async def main():
    from HW_27_data import DATA  # Импортируем данные из файла hw_27_data.py

    # Объединяем весь текст в одну строку
    full_text = " ".join([item["text"] for item in DATA])
    topic = "Bootstrap"

    # Разделяем текст на части
    chunks = split_text(full_text)

    # Параллельная обработка фрагментов
    tasks = [process_chunk(chunk, full_text, topic) for chunk in chunks]
    results = await asyncio.gather(*tasks)

    # Сохраняем результаты в Markdown
    save_to_markdown(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Произошла ошибка: {e}")