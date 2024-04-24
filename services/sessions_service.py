from fastapi import HTTPException
from repositories.session.sessions_frontend_repo import SessionFrontendRepo
from repositories.session.sessions_backend_repo import SessionBackendRepo
from repositories.session.session_verifier_repo import SessionVerifierRepo


class SessionsService:
    def __init__(self, secret_key: str):
        self.session_frontend_repo = SessionFrontendRepo(secret_key)
        self.session_backend_repo = SessionBackendRepo()
        self.cookie = self.session_frontend_repo.cookie
        self.backend = self.session_backend_repo.backend
        self.verifier = SessionVerifierRepo(
            identifier="general_verifier",
            auto_error=False,
            backend=self.backend,
            auth_http_exception=HTTPException(status_code=403, detail="invalid session")
        )