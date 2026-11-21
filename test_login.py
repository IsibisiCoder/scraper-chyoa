from types import SimpleNamespace

import pytest

from login import login


class FakeResponse:
    def __init__(self, url, text=""):
        self.url = url
        self.text = text

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, settings_url, settings_text="reader"):
        self.settings_url = settings_url
        self.settings_text = settings_text
        self.get_calls = []
        self.post_call = None

    def get(self, url):
        self.get_calls.append(url)
        if len(self.get_calls) == 1:
            return FakeResponse(
                url,
                """
                <form method="POST" action="/auth/login">
                  <input type="hidden" name="_token" value="csrf-token">
                  <input type="text" name="username">
                  <input type="password" name="password">
                </form>
                """,
            )
        return FakeResponse(self.settings_url, self.settings_text)

    def post(self, url, data, headers):
        self.post_call = (url, data, headers)
        return FakeResponse("https://chyoa.com/")


def test_login_uses_current_form_fields_and_verifies_session():
    session = FakeSession("https://chyoa.com/settings")
    config = SimpleNamespace(
        login={
            "login_url": "https://chyoa.com/auth/login",
            "username": "reader",
            "password": "secret",
        }
    )

    login(False, session, config)

    post_url, payload, headers = session.post_call
    assert post_url == "https://chyoa.com/auth/login"
    assert payload == {
        "_token": "csrf-token",
        "username": "reader",
        "password": "secret",
    }
    assert headers["Referer"] == "https://chyoa.com/auth/login"
    assert headers["Origin"] == "https://chyoa.com"
    assert session.get_calls == [
        "https://chyoa.com/auth/login",
        "https://chyoa.com/settings",
    ]


def test_login_fails_if_settings_redirects_back_to_login():
    session = FakeSession("https://chyoa.com/auth/login")
    config = SimpleNamespace(
        login={
            "login_url": "https://chyoa.com/auth/login",
            "username": "reader",
            "password": "secret",
        }
    )

    with pytest.raises(RuntimeError, match="redirected.*login page"):
        login(False, session, config)


def test_login_fails_if_settings_does_not_show_configured_username():
    session = FakeSession("https://chyoa.com/settings", settings_text="Account settings")
    config = SimpleNamespace(
        login={
            "login_url": "https://chyoa.com/auth/login",
            "username": "reader",
            "password": "secret",
        }
    )

    with pytest.raises(RuntimeError, match="username is missing"):
        login(False, session, config)
