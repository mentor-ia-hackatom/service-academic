import logging
from fastapi import Request
from sqlalchemy.orm import Session

class DBSessionMixin:
    def __init__(self, session: Session):
        self.session = session

class AppDataAccess(DBSessionMixin):
    pass

class AppService(DBSessionMixin):
    def __init__(self, session: Session, request: Request):
        super().__init__(session)
        self.request = request 
        self.current_user_uuid = request.state.user.get('uuid') if hasattr(request.state, "user") else None