# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import requests
from bs4 import BeautifulSoup
import sys

# load login from configfile and login in chyoa-site
def login(debug, session, config):
    login_data = config.login
    if not login_data:
        print("no login defined.")

    if login_data:
        login_url = login_data.get("login_url")
        if not login_url:
            print("no login-url defined.")

        if login_url:
            username = login_data.get("username")
            password = login_data.get("password")
            if username and password:
                if debug:
                    print(f"Username '{username}'")
                    print(f"Password '{password}'")

                # first call login-Site
                response = session.get(login_url)
                if debug:
                    print("GET Status:", response.status_code)

                # analyse HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # read hidden form fields
                login_payload = {}

                for field in soup.select("input[type=hidden]"):
                    name = field.get("name")
                    value = field.get("value", "")

                    if name:
                        login_payload[name] = value

                login_payload["auth_username"] = username
                login_payload["auth_password"] = password

                # Login durchführen
                login_response = session.post(
                    login_url,
                    data=login_payload,
                    headers={
                        "Referer": login_url,
                        "Origin": "https://chyoa.com"
                    }
                )

                if debug:
                    print("POST Status:", login_response.status_code)

                print(f"Sign up at {login_url} ...")

                if login_response.status_code != 200:
                    print(f"Login failed! Status code: {login_response.status_code}")
                    sys.exit(1)

                print("Login successful.")

    return
