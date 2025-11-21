import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="SignifyLearn API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "SignifyLearn Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# Simple data models for requests
class QueryOptions(BaseModel):
    limit: Optional[int] = 20
    category: Optional[str] = None
    search: Optional[str] = None


@app.get("/api/gestures")
def list_gestures(limit: int = 20, category: Optional[str] = None, search: Optional[str] = None):
    """List gestures with optional filters"""
    filt = {}
    if category:
        filt["category"] = category
    if search:
        filt["name"] = {"$regex": search, "$options": "i"}
    try:
        docs = get_documents("gesture", filt, limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gestures/{gesture_id}")
def get_gesture(gesture_id: str):
    try:
        doc = db["gesture"].find_one({"_id": ObjectId(gesture_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Gesture not found")
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class FavoritePayload(BaseModel):
    user_id: str


@app.post("/api/gestures/{gesture_id}/favorite")
def add_favorite(gesture_id: str, payload: FavoritePayload):
    try:
        db["userprofile"].update_one(
            {"_id": ObjectId(payload.user_id)},
            {"$addToSet": {"favorites": gesture_id}},
            upsert=True,
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/modules")
def list_modules(limit: int = 20):
    try:
        docs = get_documents("module", {}, limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quizzes")
def list_quizzes(limit: int = 20):
    try:
        docs = get_documents("quizquestion", {}, limit)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class QuizSubmit(BaseModel):
    user_id: Optional[str] = None
    answers: List[int]


@app.post("/api/quiz/{quiz_id}/submit")
def submit_quiz(quiz_id: str, body: QuizSubmit):
    try:
        quiz = db["quizquestion"].find_one({"_id": ObjectId(quiz_id)})
        if not quiz:
            raise HTTPException(404, "Quiz not found")
        correct = 1 if quiz.get("answer_index") == (body.answers[0] if body.answers else -1) else 0
        score = int(correct * 100)
        progress_doc = {
            "user_id": body.user_id or "guest",
            "quiz_id": quiz_id,
            "completed": True,
            "score": score,
        }
        create_document("progress", progress_doc)
        return {"score": score, "correct": bool(correct)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/schema")
def get_schema_definitions():
    """Expose schema file for tooling and admin viewer"""
    from schemas import Userprofile, Gesture, Module, Quizquestion, Progress
    return {
        "collections": [
            {"name": "userprofile", "fields": list(Userprofile.model_fields.keys())},
            {"name": "gesture", "fields": list(Gesture.model_fields.keys())},
            {"name": "module", "fields": list(Module.model_fields.keys())},
            {"name": "quizquestion", "fields": list(Quizquestion.model_fields.keys())},
            {"name": "progress", "fields": list(Progress.model_fields.keys())},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
