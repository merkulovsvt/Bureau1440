import csv
from pathlib import Path
from typing import List

from schemas import Question, ExamResult


def load_questions(lessons: List[str]) -> List[Question]:
    questions = []

    csv_path = Path('data/questions.csv')

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['lesson'] in lessons:
                questions.append(Question(
                    id=row['id'],
                    lesson=row['lesson'],
                    question=row['question'],
                    answer=row['answer']
                ))
    return questions


def save_results(result: ExamResult):
    results_path = Path('data/results.csv')

    write_header = not results_path.exists() or results_path.stat().st_size == 0

    with open(results_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if write_header:
            writer.writerow(['datetime', 'form_data', 'ai_solution'])

        writer.writerow([
            result.datetime,
            json.dumps(result.form_data, ensure_ascii=False),
            json.dumps([r.dict() for r in result.ai_solution], ensure_ascii=False)
        ])
