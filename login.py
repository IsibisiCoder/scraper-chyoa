# (c) 2025-2026 by IsibisiCoder, MIT-License, https://github.com/IsibisiCoder
import sys

# load login from configfile and login in chyoa-site
def login(debug, session, config):
    login_data = config.login
    if not login_data:
        print("no login defined.")

    login_with_username_and_password = False

    if login_data:
        login_url = login_data.get("login_url")
        if not login_url:
            print("no login-url defined.")

        if login_url:
            username = login_data.get("username")
            password = login_data.get("password")
            if username and password:
                login_with_username_and_password = True
                if debug:
                    print(f"Username '{username}'")
                    print(f"Password '{password}'")

        if login_with_username_and_password:
            login_payload = {
                'username': username,
                'password': password
            }

            print(f"Sign up at {login_url} ...")
            login_response = session.post(login_url, data=login_payload)

            if login_response.status_code != 200:
                print(f"Login failed! Status code: {login_response.status_code}")
                sys.exit(1)

            print("Login successful.")

    return
