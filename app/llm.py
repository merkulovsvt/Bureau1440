import json
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

import ollama

from app.schemas import ModelResult
from app.utils import model_name

executor = ThreadPoolExecutor()

prompt = """
### Задача:
Ты - эксперт по оценке ответов пользователей по строгим критериям. 
Проведи детальный анализ ответа пользователя в сравнении с эталонным ответом.

### Инструкции по оценке:
1. Анализируй ответ по трем критериям (каждый 0-10 баллов)
2. Для каждого критерия приведи развернутый комментарий
3. Будь объективным, но конструктивным в оценке

### Данные для анализа:
[ВОПРОС]
{question}

[ЭТАЛОННЫЙ ОТВЕТ]
{reference_answer}

[ОТВЕТ ПОЛЬЗОВАТЕЛЯ]
{user_answer}

### Критерии оценки:

1. ПОЛНОТА ОТВЕТА (0-10)
- 0: Ответ совершенно не соответствует вопросу или отсутствует.
- 1-3: Ответ по теме вопроса, но неполный, отсутствуют ключевые моменты
- 4-6: Основные моменты раскрыты, но есть пробелы
- 7-8: Ответ достаточно полный, небольшие недочеты
- 9-10: Исчерпывающий ответ, все аспекты раскрыты

2. КРАСОЧНОСТЬ ИЗЛОЖЕНИЯ (0-10)
- 0: Текст нечитаем или полностью лишен смысла.
- 1-3: Сухое перечисление фактов
- 4-6: Присутствуют элементы описания
- 7-8: Хорошие примеры и пояснения
- 9-10: Отличные примеры, метафоры, аналогии

3. СТРУКТУРА ОТВЕТА (0-10)
- 0: Полное отсутствие структуры, текст хаотичен.
- 1-3: Хаотичное изложение
- 4-6: Базовая структура присутствует
- 7-8: Четкая структура с небольшими недочетами
- 9-10: Логичная структура, правильные связки

### Требования к выводу:
- Верни строго в JSON формате
- Для каждого критерия укажи:
  * Оценку (score)
  * Конструктивный комментарий (comment) с примерами
- Будь конкретным: указывай, что именно хорошо/плохо
- Сохраняй нейтральный тон

Пример вывода:
{{
  "completeness": {{
    "score": 8,
    "comment": "Студент хорошо раскрыл основные аспекты, но не упомянул важный момент про X. Рекомендую добавить..."
  }},
  "colorfulness": {{
    "score": 6,
    "comment": "Присутствуют базовые примеры, но не хватает ярких сравнений. Например, можно было провести аналогию с Y..."
  }},
  "structure": {{
    "score": 9,
    "comment": "Отличная логика изложения. Особенно хорошо сделан переход от A к B. Единственное - в части C можно было..."
  }}
}}
"""


def evaluate_answer(question: str, user_answer: str, reference_answer: str) -> ModelResult:
    response = ollama.generate(
        model=model_name,
        prompt=prompt.format(question=question,
                             reference_answer=reference_answer,
                             user_answer=user_answer),
        format='json',
        options={'temperature': 0.7},
        keep_alive='-1m'
    )

    evaluation = json.loads(response['response'])

    result_dict = {
        "Completeness": {
            "mark": evaluation.get('completeness', {}).get("score", -1),
            "comment": evaluation.get("completeness", {}).get("comment", "ERROR")
        },
        "Colorfulness": {
            "mark": evaluation.get('colorfulness', {}).get("score", -1),
            "comment": evaluation.get("colorfulness", {}).get("comment", "ERROR")
        },
        "Structure": {
            "mark": evaluation.get('structure', {}).get("score", -1),
            "comment": evaluation.get("structure", {}).get("comment", "ERROR")
        }
    }

    return ModelResult(**result_dict)


async def evaluate_answer_async(question: str, user_answer: str, reference_answer: str) -> ModelResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        evaluate_answer,
        question,
        user_answer,
        reference_answer
    )
