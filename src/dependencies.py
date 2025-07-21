from typing import Annotated, Any

from fastapi import Depends
from sqlmodel import Session
from starlette.requests import Request

from .database import engine


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

async def graphql_context(request: Request, session: Session = Depends(get_session)) -> Any:
    return {
        "request": request,
        "session": session,
    }
