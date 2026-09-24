"""Tests for the SQLModel table definitions (BUI-24)."""

import os
import uuid

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test-secret-key")
os.environ.setdefault("SUPABASE_JWKS_URL", "https://example.supabase.co/auth/v1/.well-known/jwks.json")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")

import pytest  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine, select  # noqa: E402

from app.db.models import (  # noqa: E402
    Job,
    JobStatus,
    JobType,
    Message,
    MessageRole,
    Model,
    ModelSource,
    Revision,
    User,
)


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_revision_chain_via_parent_revision_id(session):
    user = User(id=uuid.uuid4(), email="a@example.com")
    session.add(user)
    session.commit()

    model = Model(user_id=user.id, name="Hook", source=ModelSource.GENERATED)
    session.add(model)
    session.commit()

    rev_a = Revision(
        model_id=model.id,
        parent_revision_id=None,
        label="Rev A",
        prompt="hook for a 25 mm rail",
        cad_code="result = None",
    )
    session.add(rev_a)
    session.commit()

    rev_b = Revision(
        model_id=model.id,
        parent_revision_id=rev_a.id,
        label="Rev B",
        prompt="make it wider",
        cad_code="result = None",
    )
    session.add(rev_b)
    session.commit()

    fetched = session.exec(select(Revision).where(Revision.label == "Rev B")).one()
    assert fetched.parent_revision_id == rev_a.id


def test_job_defaults_to_queued(session):
    user = User(id=uuid.uuid4(), email="b@example.com")
    session.add(user)
    session.commit()

    job = Job(user_id=user.id, type=JobType.GENERATE, input={"message": "make me a hook"})
    session.add(job)
    session.commit()
    session.refresh(job)

    assert job.status == JobStatus.QUEUED
    assert job.result is None


def test_message_links_to_model_and_optional_revision(session):
    user = User(id=uuid.uuid4(), email="c@example.com")
    session.add(user)
    session.commit()

    model = Model(user_id=user.id, name="Bracket", source=ModelSource.UPLOADED)
    session.add(model)
    session.commit()

    message = Message(model_id=model.id, role=MessageRole.USER, content="hi", revision_id=None)
    session.add(message)
    session.commit()
    session.refresh(message)

    assert message.revision_id is None
    assert message.role == MessageRole.USER
