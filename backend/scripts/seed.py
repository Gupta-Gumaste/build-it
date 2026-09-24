"""Seed the local database with a test user and a sample model.

Usage:
    uv run python scripts/seed.py
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.db.models import Model, ModelSource, Revision, User
from app.db.session import get_engine

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_EMAIL = "test@example.com"


def main() -> None:
    with Session(get_engine()) as session:
        user = session.exec(select(User).where(User.id == TEST_USER_ID)).first()
        if user is None:
            user = User(id=TEST_USER_ID, email=TEST_USER_EMAIL)
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Created user {user.email} ({user.id})")
        else:
            print(f"User {user.email} ({user.id}) already exists")

        model = session.exec(select(Model).where(Model.user_id == user.id)).first()
        if model is None:
            model = Model(user_id=user.id, name="Sample hook", source=ModelSource.GENERATED)
            session.add(model)
            session.commit()
            session.refresh(model)

            revision = Revision(
                model_id=model.id,
                parent_revision_id=None,
                label="Rev A",
                prompt="hook for a 25 mm diameter bed rail, holds 2 kg",
                specs={"attaches_to": "25mm rail", "load_kg": 2},
                cad_code=(
                    'import cadquery as cq\n'
                    'result = cq.Workplane("XY").box(40, 20, 5)\n'
                ),
            )
            session.add(revision)
            session.commit()
            print(f"Created model {model.name!r} ({model.id}) with revision {revision.label}")
        else:
            print(f"Model {model.name!r} ({model.id}) already exists")


if __name__ == "__main__":
    main()
