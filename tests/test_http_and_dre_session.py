from __future__ import annotations

import json
from typing import Any

import pytest
import requests

from leis_portugal.errors import FetchError
from leis_portugal.infrastructure.http import HttpClient
from leis_portugal.sources.dre.client import DreApiError, DreClient, DreSession


class FakeResponse:
    def __init__(self, status: int = 200, body: Any = None, text: str | None = None, content_type: str = "application/json") -> None:
        self.status_code = status
        self._body = body
        self.text = text if text is not None else json.dumps(body)
        self.content = self.text.encode("utf-8")
        self.headers = {"Content-Type": content_type}
        self.url = "https://example.org"

    def json(self) -> Any:
        if self._body is None:
            raise ValueError("não é JSON")
        return self._body


class FakeSession:
    """Substitui requests.Session: devolve as respostas por ordem e regista os pedidos."""

    def __init__(self, responses: list[Any]) -> None:
        self.responses = list(responses)
        self.requests: list[tuple[str, str, dict]] = []
        self.headers: dict[str, str] = {}

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.requests.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _client(responses: list[Any], **options: Any) -> tuple[HttpClient, FakeSession, list[float]]:
    session = FakeSession(responses)
    sleeps: list[float] = []
    return HttpClient(session=session, sleep=sleeps.append, **options), session, sleeps


def test_retries_server_errors_and_network_failures_then_succeeds():
    client, session, sleeps = _client([FakeResponse(503), requests.ConnectionError("rede"), FakeResponse(200, {"ok": True})], max_retries=3)
    assert client.get("https://example.org").json() == {"ok": True}
    assert len(session.requests) == 3
    assert sleeps == [2, 4]


def test_client_errors_are_not_retried():
    client, session, _ = _client([FakeResponse(404)], max_retries=3)
    with pytest.raises(FetchError, match="HTTP 404"):
        client.get("https://example.org/x")
    assert len(session.requests) == 1


def test_gives_up_after_max_retries():
    client, session, _ = _client([FakeResponse(429), FakeResponse(429)], max_retries=1)
    with pytest.raises(FetchError, match="HTTP 429"):
        client.get("https://example.org")
    assert len(session.requests) == 2


def test_user_agent_identifies_the_project():
    client, session, _ = _client([])
    assert session.headers["User-Agent"].startswith("leis-portugal/")
    assert client.session is session


SCREEN_JS = (
    'controller.callDataAction("DataActionGetDataAndApplicationSettings", "screenservices/dr/Home/WB_Serie1_List/'
    'DataActionGetDataAndApplicationSettings", "HASH123", function(){})'
)


def _dre_session(post_responses: list[FakeResponse]) -> tuple[DreSession, FakeSession]:
    responses = [
        FakeResponse(text='var AnonymousCSRFToken = "TOKEN";', content_type="text/javascript"),
        FakeResponse(body=[{"versionToken": "MODULE"}]),
        FakeResponse(text=SCREEN_JS, content_type="text/javascript"),
        *post_responses,
    ]
    client, session, _ = _client(responses)
    return DreSession(client), session


def test_handshake_discovers_endpoint_and_posts_screen_state():
    session, http = _dre_session([FakeResponse(body={"data": {"DiarioByDiaList": {"List": [{"DiplomaLegiList": {"List": [{"LinkSitemap": "/dr/detalhe/lei/1-2026-1"}]}}]}}})])
    documents = DreClient(session).documents_by_date("2026-10-20")
    assert documents == [{"LinkSitemap": "/dr/detalhe/lei/1-2026-1"}]
    method, url, kwargs = http.requests[-1]
    assert method == "POST"
    assert url.endswith("/dr/screenservices/dr/Home/WB_Serie1_List/DataActionGetDataAndApplicationSettings")
    assert kwargs["json"]["versionInfo"] == {"moduleVersion": "MODULE", "apiVersion": "HASH123"}
    assert kwargs["json"]["viewName"] == "Home.home"
    assert kwargs["headers"]["X-CSRFToken"] == "TOKEN"


def test_html_answer_is_an_api_error_not_an_empty_day():
    retry_handshake = [
        FakeResponse(text='var AnonymousCSRFToken = "TOKEN";', content_type="text/javascript"),
        FakeResponse(body=[{"versionToken": "MODULE"}]),
        FakeResponse(text=SCREEN_JS, content_type="text/javascript"),
    ]
    html = FakeResponse(text="<html>erro</html>", content_type="text/html")
    session, _ = _dre_session([html, *retry_handshake, html])
    with pytest.raises(DreApiError, match="em vez de JSON"):
        DreClient(session).documents_by_date("2026-10-20")


def test_missing_list_means_the_dre_changed_shape():
    session, _ = _dre_session([FakeResponse(body={"data": {"Outra": 1}})])
    with pytest.raises(DreApiError, match="DiarioByDiaList"):
        DreClient(session).documents_by_date("2026-10-20")


def test_renamed_action_names_the_declared_actions():
    handshake = [
        FakeResponse(text='"X-CSRFToken","TOKEN"', content_type="text/javascript"),
        FakeResponse(body={"versionToken": "MODULE"}),
        FakeResponse(text='callDataAction("DataActionOutraCoisa", "screenservices/x", "H")', content_type="text/javascript"),
    ]
    # O cliente repete o handshake uma vez (pode ter sido um deploy a meio) antes de desistir.
    responses = handshake + handshake
    client, _, _ = _client(responses)
    with pytest.raises(DreApiError, match="DataActionOutraCoisa"):
        DreClient(DreSession(client)).documents_by_date("2026-10-20")
