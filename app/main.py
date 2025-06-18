import uuid
import uvicorn
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas import Answer, ExamResult
from app.utils import load_questions, save_results
from app.llm import evaluate_answer, evaluate_answer_async
from app.sessions import save_session_data, get_session_data

app = FastAPI()

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "lessons": ["AI", "Math", "Python"]
    })


@app.post("/", response_class=RedirectResponse)
async def process_selection(request: Request, selected_lessons: List[str] = Form(...)):
    session_id = str(uuid.uuid4())
    session_data = {
        "selected_lessons": [lesson.lower() for lesson in selected_lessons],
        "questions": [],
        "answers": [],
        "model_results": [],
    }
    await save_session_data(session_id, session_data)

    response = RedirectResponse(url="/exam", status_code=303)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/exam", response_class=HTMLResponse)
async def start_exam(request: Request):
    session_id = request.cookies.get("session_id")
    session_data = await get_session_data(session_id)

    if not session_id or not session_data:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    selected_lessons = session_data["selected_lessons"]

    questions = await load_questions(lessons=selected_lessons)
    return templates.TemplateResponse("exam.html", {
        "request": request,
        "questions": questions
    })


@app.post("/exam", response_class=RedirectResponse)
async def process_answers(request: Request,
                          question_ids: List[int] = Form(...),
                          user_answers: List[str] = Form(...)):
    session_id = request.cookies.get("session_id")
    session_data = await get_session_data(session_id)

    if not session_id or not session_data:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    questions = await load_questions(ids=question_ids)

    answers = [Answer(id=i,
                      q=question.question,
                      user_a=user_answers[i],
                      real_a=question.answer)
               for i, question in enumerate(questions)]

    model_results = await asyncio.gather(*[
        evaluate_answer_async(answer.q, answer.user_a, answer.real_a)
        for answer in answers
    ])

    session_data["questions"] = questions
    session_data["answers"] = answers
    session_data["model_results"] = model_results
    await save_session_data(session_id, session_data)

    return RedirectResponse(url="/results", status_code=303)


@app.get("/results", response_class=HTMLResponse)
async def show_results(request: Request):
    session_id = request.cookies.get("session_id")
    session_data = await get_session_data(session_id)

    if not session_id or not session_data:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    answers = session_data["answers"]
    questions = session_data["questions"]
    model_results = session_data["model_results"]

    await save_results(ExamResult(datetime=datetime.now(),
                                  form_data=answers,
                                  ai_solution=model_results))

    return templates.TemplateResponse("results.html", {
        "request": request,
        "results_data": list(zip(answers, questions, model_results))
    })

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="localhost", port=8000, reload=True)
