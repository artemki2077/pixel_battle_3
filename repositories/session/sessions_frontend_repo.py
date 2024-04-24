from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters


class SessionFrontendRepo:
    def __init__(self, secret_key: str):
        self.cookie_params = CookieParameters()
        self.cookie = SessionCookie(
            cookie_name="cookie",
            identifier="general_verifier",
            auto_error=False,
            secret_key=secret_key,
            cookie_params=self.cookie_params,
        )