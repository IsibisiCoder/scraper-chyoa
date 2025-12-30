import sys

# load login from configfile and login in chyoa-site
def login(debug, session, config):
    login = config.get("login")
    if not login:
        print(f"Kein Login definiert.")

    loginWithUsernameAndPassword = False

    if login:
        login_url = login.get("login_url")
        if not login_url:
            print(f"Keine Login-Url definiert.")

        if login_url:
            username = login.get("username")
            password = login.get("password")
            if username and password:
                loginWithUsernameAndPassword = True
                if debug:
                    print(f"Username '{username}'")
                    print(f"Password '{password}'")

        if loginWithUsernameAndPassword:
            login_payload = {
                'username': username,
                'password': password
            }

            print(f"Melde dich an bei {login_url} ...")
            login_response = session.post(login_url, data=login_payload)

            if login_response.status_code != 200:
                print(f"Login fehlgeschlagen! Statuscode: {login_response.status_code}")
                sys.exit(1)

            print("Login erfolgreich.")

    return
