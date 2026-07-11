from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import settings
from app.schemas.review import OCRConfig
from app.services.cloud_runtime import runtime_dir
from app.services.file_parser import ParseError, parse_file

router = APIRouter(prefix="/api/v1", tags=["local-workspace"])
WORKSPACE_ID = "local-workspace"


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = "workspace_courses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    exam_date: Mapped[str] = mapped_column(String(20), default="")


class Conversation(Base):
    __tablename__ = "workspace_conversations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    course_id: Mapped[str | None] = mapped_column(ForeignKey("workspace_courses.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(160), default="新对话")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)


class Message(Base):
    __tablename__ = "workspace_messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("workspace_conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(20), default="completed")


class MemoryItem(Base):
    __tablename__ = "workspace_memory"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    course_id: Mapped[str | None] = mapped_column(ForeignKey("workspace_courses.id", ondelete="CASCADE"), nullable=True)
    kind: Mapped[str] = mapped_column(String(30), default="study_preference")
    content: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AgentTask(Base):
    __tablename__ = "workspace_agent_tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    course_id: Mapped[str | None] = mapped_column(ForeignKey("workspace_courses.id", ondelete="SET NULL"), nullable=True)
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="planned")
    plan_json: Mapped[str] = mapped_column(Text, default="[]")
    current_step: Mapped[int] = mapped_column(Integer, default=0)


class CourseFile(Base):
    __tablename__ = "workspace_files"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    course_id: Mapped[str] = mapped_column(ForeignKey("workspace_courses.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="ready")
    page_count: Mapped[int] = mapped_column(Integer, default=0)


class KnowledgeChunk(Base):
    __tablename__ = "workspace_knowledge_chunks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    course_id: Mapped[str] = mapped_column(ForeignKey("workspace_courses.id", ondelete="CASCADE"), index=True)
    file_id: Mapped[str] = mapped_column(ForeignKey("workspace_files.id", ondelete="CASCADE"), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    page_number: Mapped[int] = mapped_column(Integer)
    section_title: Mapped[str] = mapped_column(String(255), default="")
    text: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def initialize_platform_database() -> None:
    Base.metadata.create_all(engine)


def database_ready() -> bool:
    try:
        with engine.connect() as connection: connection.exec_driver_sql("SELECT 1")
        return True
    except Exception: return False


def db_session():
    with SessionLocal() as db: yield db


class CourseBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    exam_date: str = ""


class ConversationBody(BaseModel):
    title: str = Field(default="新对话", max_length=160)
    course_id: str | None = None


class MessageBody(BaseModel):
    content: str = Field(min_length=1, max_length=50000)


class MemoryBody(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    kind: str = "study_preference"
    course_id: str | None = None


class AgentBody(BaseModel):
    goal: str = Field(min_length=3, max_length=2000)
    course_id: str | None = None


class SearchBody(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


def _course(db: Session, course_id: str) -> Course:
    item = db.get(Course, course_id)
    if not item: raise HTTPException(status_code=404, detail="课程不存在")
    return item


@router.get("/workspace")
def workspace_info():
    return {"id": WORKSPACE_ID, "mode": "local", "api_key_persistence": "browser_only", "version": settings.app_version}


@router.get("/courses")
def list_courses(db: Session = Depends(db_session)):
    return [{"id": x.id, "name": x.name, "description": x.description, "exam_date": x.exam_date} for x in db.scalars(select(Course))]


@router.post("/courses", status_code=201)
def create_course(body: CourseBody, db: Session = Depends(db_session)):
    item = Course(id=str(uuid4()), **body.model_dump()); db.add(item); db.commit()
    return {"id": item.id, **body.model_dump()}


@router.delete("/courses/{course_id}", status_code=204)
def remove_course(course_id: str, db: Session = Depends(db_session)):
    item = _course(db, course_id); db.delete(item); db.commit()


ALLOWED_FILES = {".pdf", ".pptx", ".docx", ".md", ".txt", ".png", ".jpg", ".jpeg"}


@router.get("/courses/{course_id}/files")
def list_files(course_id: str, db: Session = Depends(db_session)):
    _course(db, course_id)
    return [{"id": x.id, "filename": x.filename, "status": x.status, "page_count": x.page_count} for x in db.scalars(select(CourseFile).where(CourseFile.course_id == course_id))]


@router.post("/courses/{course_id}/files", status_code=201)
async def upload_file(course_id: str, uploaded: UploadFile = File(...), db: Session = Depends(db_session)):
    _course(db, course_id)
    original = Path(uploaded.filename or "upload").name; suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED_FILES: raise HTTPException(status_code=400, detail="不支持该文件类型")
    content = await uploaded.read()
    if not content or len(content) > settings.max_upload_bytes: raise HTTPException(status_code=413, detail="文件为空或超过大小限制")
    target_dir = runtime_dir(settings.upload_dir) / WORKSPACE_ID / course_id; target_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{suffix}"; path = (target_dir / stored_name).resolve()
    if target_dir.resolve() not in path.parents: raise HTTPException(status_code=400, detail="文件路径无效")
    path.write_bytes(content)
    try: parsed = parse_file(path, OCRConfig())
    except ParseError as exc: path.unlink(missing_ok=True); raise HTTPException(status_code=400, detail="文件解析失败") from exc
    item = CourseFile(id=str(uuid4()), course_id=course_id, filename=original, stored_name=stored_name, page_count=len(parsed.pages)); db.add(item); count = 0
    for page in parsed.pages:
        for text in _chunks(page.text):
            db.add(KnowledgeChunk(id=str(uuid4()), course_id=course_id, file_id=item.id, file_name=original, page_number=page.page_number, section_title=_title(text), text=text, content_hash=hashlib.sha256(text.encode()).hexdigest())); count += 1
    db.commit(); return {"id": item.id, "filename": original, "status": "ready", "page_count": item.page_count, "chunks": count}


def _chunks(text: str, limit: int = 1400) -> list[str]:
    paragraphs = [x.strip() for x in re.split(r"\n\s*\n|(?<=[。！？])\s+", text) if x.strip()]; chunks = []; current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) > limit: chunks.append(current); current = ""
        current = f"{current}\n{paragraph}".strip()
    if current: chunks.append(current)
    return chunks


def _title(text: str) -> str:
    first = text.splitlines()[0].strip()[:80]
    return first if len(first) >= 3 and not re.fullmatch(r"[\d\W_]+", first) else "材料片段"


@router.post("/courses/{course_id}/search")
def search_course(course_id: str, body: SearchBody, db: Session = Depends(db_session)):
    _course(db, course_id); terms = {x.lower() for x in re.findall(r"[\w\u4e00-\u9fff]{2,}", body.query)}
    candidates = db.scalars(select(KnowledgeChunk).where(KnowledgeChunk.course_id == course_id)).all()
    ranked = sorted(candidates, key=lambda x: sum(term in x.text.lower() for term in terms), reverse=True)
    matches = [x for x in ranked if any(term in x.text.lower() for term in terms)][:body.top_k]
    return {"query": body.query, "answer": "\n\n".join(x.text[:500] for x in matches) if matches else "课程资料中没有找到足够依据。", "citations": [{"chunk_id": x.id, "file_name": x.file_name, "page_number": x.page_number, "section_title": x.section_title, "excerpt": x.text[:300]} for x in matches]}


@router.get("/conversations")
def conversations(db: Session = Depends(db_session)):
    return [{"id": x.id, "title": x.title, "course_id": x.course_id, "archived": x.archived} for x in db.scalars(select(Conversation))]


@router.post("/conversations", status_code=201)
def create_conversation(body: ConversationBody, db: Session = Depends(db_session)):
    if body.course_id: _course(db, body.course_id)
    item = Conversation(id=str(uuid4()), **body.model_dump()); db.add(item); db.commit(); return {"id": item.id, **body.model_dump()}


def _conversation(db: Session, item_id: str) -> Conversation:
    item = db.get(Conversation, item_id)
    if not item: raise HTTPException(status_code=404, detail="对话不存在")
    return item


@router.get("/conversations/{item_id}/messages")
def messages(item_id: str, db: Session = Depends(db_session)):
    _conversation(db, item_id); return [{"id": x.id, "role": x.role, "content": x.content, "state": x.state} for x in db.scalars(select(Message).where(Message.conversation_id == item_id))]


@router.post("/conversations/{item_id}/messages", status_code=201)
def add_message(item_id: str, body: MessageBody, db: Session = Depends(db_session)):
    item = _conversation(db, item_id); user_message = Message(id=str(uuid4()), conversation_id=item.id, role="user", content=body.content)
    reply_text = "尚未配置AI模型，请前往设置连接你的模型。课程知识库和 ExamForge 本地功能仍可使用。"
    reply = Message(id=str(uuid4()), conversation_id=item.id, role="assistant", content=reply_text); db.add_all([user_message, reply]); db.commit()
    return {"message": {"id": user_message.id, "role": "user", "content": body.content}, "reply": {"id": reply.id, "role": "assistant", "content": reply_text, "citations": []}, "needs_model_config": True}


@router.get("/memory")
def memory(db: Session = Depends(db_session)):
    return [{"id": x.id, "kind": x.kind, "content": x.content, "course_id": x.course_id, "enabled": x.enabled} for x in db.scalars(select(MemoryItem))]


@router.post("/memory", status_code=201)
def add_memory(body: MemoryBody, db: Session = Depends(db_session)):
    if body.course_id: _course(db, body.course_id)
    item = MemoryItem(id=str(uuid4()), **body.model_dump()); db.add(item); db.commit(); return {"id": item.id, **body.model_dump(), "enabled": True}


@router.get("/agent/tasks")
def tasks(db: Session = Depends(db_session)):
    return [{"id": x.id, "goal": x.goal, "status": x.status, "course_id": x.course_id} for x in db.scalars(select(AgentTask))]


@router.post("/agent/tasks", status_code=201)
def add_task(body: AgentBody, db: Session = Depends(db_session)):
    if body.course_id: _course(db, body.course_id)
    steps = ["分析课程资料", "识别重点和薄弱项", "生成学习计划", "跟踪完成情况"]
    item = AgentTask(id=str(uuid4()), goal=body.goal, course_id=body.course_id, plan_json=json.dumps(steps, ensure_ascii=False)); db.add(item); db.commit()
    return {"id": item.id, "goal": item.goal, "status": item.status, "steps": steps}


@router.get("/workspace/export")
def export_workspace(db: Session = Depends(db_session)):
    output = runtime_dir(settings.output_dir) / "CampusAIWorkspace-workspace.json"
    payload = {"version": settings.app_version, "courses": [{"id": x.id, "name": x.name, "description": x.description, "exam_date": x.exam_date} for x in db.scalars(select(Course))], "conversations": [{"id": x.id, "title": x.title, "course_id": x.course_id} for x in db.scalars(select(Conversation))], "memory": [{"content": x.content, "kind": x.kind, "course_id": x.course_id} for x in db.scalars(select(MemoryItem))]}
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return FileResponse(output, filename="CampusAIWorkspace-workspace.json")


@router.delete("/workspace", status_code=204)
def clear_workspace(db: Session = Depends(db_session)):
    for model in (KnowledgeChunk, CourseFile, Message, Conversation, MemoryItem, AgentTask, Course): db.query(model).delete()
    db.commit(); shutil.rmtree(runtime_dir(settings.upload_dir) / WORKSPACE_ID, ignore_errors=True)
