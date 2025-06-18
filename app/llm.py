import json
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

import ollama

from app.schemas import ModelResult

executor = ThreadPoolExecutor()

# model_name = 'owl/t-lite:instruct'
model_name = 'hf.co/bartowski/microsoft_Phi-4-mini-instruct-GGUF:Q8_0'
ollama.pull(model=model_name)

prompt = """
Ты - опытный преподаватель, который оценивает ответы пользователей по строгим критериям. 
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
- 9-10: Ответ полностью раскрывает тему, все ключевые аспекты учтены
- 7-8: Незначительные упущения второстепенных деталей
- 5-6: Отсутствуют некоторые важные элементы
- 3-4: Ответ поверхностный, много упущений
- 0-2: Ответ не соответствует вопросу

2. КРАСОЧНОСТЬ ИЗЛОЖЕНИЯ (0-10)
- 9-10: Богатый язык, яркие примеры, метафоры, аналогии
- 7-8: Хорошие описания и пояснения
- 5-6: Базовые примеры без детализации
- 3-4: Сухое перечисление фактов
- 0-2: Отсутствие попыток украсить речь

3. СТРУКТУРА ОТВЕТА (0-10)
- 9-10: Четкая логика, плавные переходы, хорошие связки
- 7-8: Понятная структура с небольшими шероховатостями
- 5-6: Базовое структурирование, но есть проблемы с логикой
- 3-4: Слабая организация мысли
- 0-2: Полностью хаотичное изложение

### Требования к выводу:
- Верни строго в JSON формате
- Для каждого критерия укажи:
  * Оценку (score)
  * Конструктивный комментарий (comment) с примерами
- Будь конкретным: указывай, что именно хорошо/плохо
- Сохраняй доброжелательный тон

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
