import os
import json
import redis.asyncio as redis
from dotenv import load_dotenv
from typing import Dict, Optional

from app.schemas import Question, Answer, ModelResult

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=os.getenv("REDIS_DB"),
    decode_responses=True
)


async def get_session_data(session_id: str) -> Optional[Dict]:
    session_data = await redis_client.hgetall(f"session:{session_id}")
    if not session_data:
        return None

    session_data["selected_lessons"] = json.loads(session_data.get("selected_lessons", '{}'))
    session_data["questions"] = [Question.model_validate(item) for item in
                                 json.loads(session_data.get("questions", '{}'))]
    session_data["answers"] = [Answer.model_validate(item) for item in
                               json.loads(session_data.get("answers", '{}'))]
    session_data["model_results"] = [ModelResult.model_validate(item) for item in
                                     json.loads(session_data.get("model_results", '{}'))]

    return session_data


async def save_session_data(session_id: str, session_data: Dict):
    session_data_to_save = {
        "selected_lessons": json.dumps(session_data.get("selected_lessons", [])),
        "questions": json.dumps([item.model_dump() for item in session_data.get("questions", [])]),
        "answers": json.dumps([item.model_dump() for item in session_data.get("answers", [])]),
        "model_results": json.dumps([item.model_dump() for item in session_data.get("model_results", [])])
    }

    await redis_client.hset(f"session:{session_id}", mapping=session_data_to_save)
