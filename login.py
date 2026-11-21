# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup


def login(debug, session, config):
    """Log in to CHYOA using the configured credentials and shared session."""
    login_data = config.login
    if not login_data:
        if debug:
            print("No login configured.")
        return

    login_url = login_data.get("login_url")
    username = login_data.get("username")
    password = login_data.get("password")
    if not login_url:
        raise ValueError("No login URL configured.")
    if not username or not password:
        raise ValueError("Both username and password must be configured.")

    login_page = session.get(login_url)
    login_page.raise_for_status()
    soup = BeautifulSoup(login_page.text, "html.parser")
    form = soup.find("form", method=lambda value: value and value.lower() == "post")
    if form is None:
        raise ValueError("The login page does not contain a POST form.")

    username_field = next(
        (
            field
            for field in form.select("input[name]")
            if field.get("name", "").lower() in {"username", "auth_username", "email"}
        ),
        None,
    )
    password_field = form.select_one('input[type="password"][name]')
    if username_field is None or password_field is None:
        raise ValueError("The login form is missing its username or password field.")

    payload = {
        field["name"]: field.get("value", "")
        for field in form.select('input[type="hidden"][name]')
    }
    payload[username_field["name"]] = username
    payload[password_field["name"]] = password

    post_url = urljoin(login_page.url, form.get("action") or login_page.url)
    origin = "{uri.scheme}://{uri.netloc}".format(uri=urlsplit(login_page.url))
    login_response = session.post(
        post_url,
        data=payload,
        headers={"Referer": login_page.url, "Origin": origin},
    )
    login_response.raise_for_status()

    if debug:
        # test the success login in the settings
        settings_url = urljoin(login_page.url, "/settings")
        settings_response = session.get(settings_url)
        settings_response.raise_for_status()
        login_path = urlsplit(login_url).path.rstrip("/")
        settings_path = urlsplit(settings_response.url).path.rstrip("/")
        if settings_path == login_path:
            raise RuntimeError("Login failed: CHYOA redirected the session back to the login page.")
        if username.casefold() not in settings_response.text.casefold():
            raise RuntimeError("Login could not be verified: the configured username is missing from settings.")

    print("Login successful.")
