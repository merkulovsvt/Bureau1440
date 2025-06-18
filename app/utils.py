import csv
import json
import aiofiles
from typing import List
from pathlib import Path

from app.schemas import Question, ExamResult


async def load_questions(lessons: List[str] = None, ids: List[int] = None) -> List[Question]:
    csv_path = Path(__file__).parent / "data" / "questions.csv"

    questions = []
    async with aiofiles.open(csv_path, mode='r', encoding='utf-8') as file:
        content = await file.read()
        reader = csv.DictReader(content.splitlines())

        for row in reader:
            if lessons and row['lesson'].lower() in [lesson.lower() for lesson in lessons]:
                questions.append(Question(
                    id=row['id'],
                    lesson=row['lesson'],
                    question=row['question'],
                    answer=None
                ))
            elif ids and int(row['id']) in ids:
                questions.append(Question(
                    id=row['id'],
                    lesson=row['lesson'],
                    question=row['question'],
                    answer=row['answer']
                ))

    return questions


async def save_results(result: ExamResult) -> None:
    results_path = Path(__file__).parent / "data" / "results.csv"
    write_header = not results_path.exists() or results_path.stat().st_size == 0

    async with aiofiles.open(results_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if write_header:
            await writer.writerow(['datetime', 'form_data', 'ai_solution'])

        await writer.writerow([
            result.datetime,
            json.dumps([elem.model_dump() for elem in result.form_data], ensure_ascii=False),
            json.dumps([elem.model_dump() for elem in result.ai_solution], ensure_ascii=False)
        ])
