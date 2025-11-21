"""
Database Schemas for SignifyLearn

Each Pydantic model maps to a MongoDB collection (collection name is the lowercase
class name).
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class Userprofile(BaseModel):
    """Collection: userprofile"""
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    points: int = Field(0, ge=0, description="Total points accumulated")
    level: int = Field(1, ge=1, description="Current level")
    streak: int = Field(0, ge=0, description="Learning streak in days")
    badges: List[str] = Field(default_factory=list, description="Badge ids earned")
    favorites: List[str] = Field(default_factory=list, description="Gesture ids favorited")
    accessibility: dict = Field(default_factory=lambda: {
        "darkMode": False,
        "highContrast": False,
        "fontScale": 1.0,
        "reducedMotion": False,
    })


class Gesture(BaseModel):
    """Collection: gesture"""
    name: str = Field(..., description="Gesture name")
    category: str = Field(..., description="Category such as A-Z, Numbers, Basic Words")
    difficulty: str = Field("Pemula", description="Pemula / Menengah / Lanjutan")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    video_url: Optional[str] = Field(None, description="Gesture video URL")
    steps: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    examples: List[str] = Field(default_factory=list, description="Example usage sentences")


class Module(BaseModel):
    """Collection: module"""
    title: str
    subtitle: Optional[str] = None
    cover: Optional[str] = None
    content: List[dict] = Field(
        default_factory=list,
        description="List of content blocks: {type: text|image|video, value: str}"
    )


class Quizquestion(BaseModel):
    """Collection: quizquestion"""
    module_id: Optional[str] = Field(None, description="Related module id")
    prompt: str
    media_url: Optional[str] = None
    choices: List[str]
    answer_index: int = Field(..., ge=0, description="Index of correct choice")


class Progress(BaseModel):
    """Collection: progress"""
    user_id: str
    module_id: Optional[str] = None
    quiz_id: Optional[str] = None
    completed: bool = False
    score: Optional[int] = None
    detail: Optional[dict] = None
