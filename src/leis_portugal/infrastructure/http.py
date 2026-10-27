"""Cliente HTTP comum: intervalo mínimo entre pedidos e novas tentativas."""

from __future__ import annotations

import time
from typing import Any

import requests

from leis_portugal.errors import FetchError


USER_AGENT = "leis-portugal/0.1 (+https://github.com/joaobarrosodev/leis-portugal)"


class HttpClient:
    """Sessão HTTP educada para fontes públicas.

    - espera `min_interval` segundos entre pedidos da mesma sessão;
    - repete com espera exponencial em erros de rede, 5xx e 429;
    - qualquer outra resposta diferente de 200 é um `FetchError`.

    Não é partilhável entre threads: cada thread usa a sua instância.
    """

    def __init__(
        self,
        *,
        session: requests.Session | None = None,
        timeout: float = 60,
        min_interval: float = 0.0,
        max_retries: int = 3,
        max_backoff: float = 60,
        sleep=time.sleep,
    ) -> None:
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.timeout = timeout
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.max_backoff = max_backoff
        self._sleep = sleep
        self._last_request = 0.0

    def _throttle(self) -> None:
        wait = self.min_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            self._sleep(wait)
        self._last_request = time.monotonic()

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        for attempt in range(self.max_retries + 1):
            self._throttle()
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            except requests.RequestException as exc:
                if attempt == self.max_retries:
                    raise FetchError(f"Falha de acesso a {url}: {exc}") from exc
            else:
                retryable = response.status_code >= 500 or response.status_code == 429
                if not retryable:
                    if response.status_code != 200:
                        raise FetchError(f"HTTP {response.status_code} para {url}")
                    return response
                if attempt == self.max_retries:
                    raise FetchError(f"HTTP {response.status_code} para {url}")
            self._sleep(min(self.max_backoff, 2 ** (attempt + 1)))
        raise FetchError(f"Falha de acesso a {url}")  # pragma: no cover

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", url, **kwargs)
