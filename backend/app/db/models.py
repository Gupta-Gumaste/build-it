"""SQLModel table definitions.

`users.id` mirrors the id Supabase Auth assigns in `auth.users` — Supabase
owns authentication (password hashing, sessions), this table just holds the
app-level profile data joined to everything else.
"""

import uuid
from datetime import datetime, timezone
from enum import StrEnum

from sqlmodel import JSON, Column, Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ModelSource(StrEnum):
    GENERATED = "generated"
    UPLOADED = "uploaded"


class JobType(StrEnum):
    GENERATE = "generate"
    EDIT = "edit"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=_utcnow)


class Model(SQLModel, table=True):
    __tablename__ = "models"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    name: str
    source: ModelSource
    created_at: datetime = Field(default_factory=_utcnow)


class Revision(SQLModel, table=True):
    __tablename__ = "revisions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    model_id: uuid.UUID = Field(foreign_key="models.id", index=True)
    parent_revision_id: uuid.UUID | None = Field(default=None, foreign_key="revisions.id", index=True)
    label: str
    prompt: str
    specs: dict = Field(default_factory=dict, sa_column=Column(JSON))
    cad_code: str
    file_key: str | None = None
    thumbnail_key: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    type: JobType
    status: JobStatus = Field(default=JobStatus.QUEUED, index=True)
    input: dict = Field(default_factory=dict, sa_column=Column(JSON))
    result: dict | None = Field(default=None, sa_column=Column(JSON))
    error: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    model_id: uuid.UUID = Field(foreign_key="models.id", index=True)
    role: MessageRole
    content: str
    revision_id: uuid.UUID | None = Field(default=None, foreign_key="revisions.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
