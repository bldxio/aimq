import resend

from ..config import config


class ResendError(Exception):
    pass


class ResendClient:
    def __init__(self):
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            api_key = config.resend_api_key
            if not api_key or not api_key.strip():
                raise ResendError("Resend API key not configured")
            resend.api_key = api_key
            self._initialized = True

    @property
    def client(self):
        self._ensure_initialized()
        return resend

    def send_email(self, **kwargs):
        self._ensure_initialized()
        try:
            return resend.Emails.send(kwargs)
        except Exception as e:
            raise ResendError(f"Failed to send email: {str(e)}")

    def download_attachment(self, download_url: str) -> bytes:
        import httpx

        self._ensure_initialized()
        headers = {"Authorization": f"Bearer {config.resend_api_key}"}

        try:
            response = httpx.get(
                download_url,
                headers=headers,
                timeout=60.0,
                follow_redirects=True,
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            raise ResendError(f"Failed to download attachment: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ResendError(f"Failed to download attachment: {str(e)}")


resend_client = ResendClient()
