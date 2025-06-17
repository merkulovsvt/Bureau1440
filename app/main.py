import uuid
import uvicorn
from typing import List, Dict

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import load_questions

import time

app = FastAPI()

templates = Jinja2Templates(directory="templates")

sessions = {}


@app.get("/", response_class=HTMLResponse, tags=["WEB"])
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "lessons": ["AI", "Math", "Python"]
    })


@app.post("/", tags=["WEB"])
async def process_selection(request: Request, selected_lessons: List[str] = Form(...)):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "selected_lessons": [lesson.lower() for lesson in selected_lessons],
        "answers": {}
    }

    response = RedirectResponse(url="/exam", status_code=303)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.get("/exam", tags=["WEB"], response_class=HTMLResponse)
async def start_exam(request: Request):
    session_id = request.cookies.get("session_id")

    selected_lessons = sessions[session_id]["selected_lessons"]

    questions = load_questions(selected_lessons)

    return templates.TemplateResponse("exam.html", {
        "request": request,
        "questions": questions
    })


@app.post("/exam", tags=["WEB"], response_class=HTMLResponse)
async def process_answers(request: Request,
                          question_ids: List[int] = Form(...),
                          user_answers: List[str] = Form(...)):
    answers = []

    time.sleep(5)

    # for question_id, answer in zip(question_ids, user_answers):
    #     answers.append(Answer(
    #         id=question_id,
    #         q=row['lesson'],
    #         user_a=answer,
    #         real_a=row['answer']
    #     ))
    #
    # print(question_ids, answers)

    return RedirectResponse(url="/results", status_code=303)


@app.get("/results", response_class=HTMLResponse)
async def show_results(request: Request):
    return templates.TemplateResponse("results.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
