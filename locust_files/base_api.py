# every call of the load test goes through this class, inside its own
# catch_response block, so the documented status (and a body fingerprint
# where one is cheap) is asserted at the call site and a task set is a
# single readable line. each method picks its own stats name, so the
# report groups by intent, not by url


def _verdict(response, expected_status, must_contain=None):
    if response.status_code != expected_status:
        response.failure(f"status {response.status_code} is not {expected_status}")
        return False
    if must_contain and must_contain not in (response.text or ""):
        response.failure(f"body misses {must_contain!r}")
        return False
    response.success()
    return True


class ReqResBaseApi:
    # ---------- users ----------
    def list_users(self, client, page):
        with client.get(
            "/api/users",
            params={"page": page},
            name="list users",
            catch_response=True,
        ) as response:
            _verdict(response, 200, '"per_page"')
        return response

    def get_user(self, client, user_id):
        with client.get(
            f"/api/users/{user_id}", name="get user", catch_response=True
        ) as response:
            _verdict(response, 200, "janet.weaver")
        return response

    def get_unknown_user(self, client, user_id):
        with client.get(
            f"/api/users/{user_id}",
            name="get unknown user (404)",
            catch_response=True,
        ) as response:
            _verdict(response, 404)
        return response

    def create_user(self, client, name, job):
        with client.post(
            "/api/users",
            json={"name": name, "job": job},
            name="create user",
            catch_response=True,
        ) as response:
            _verdict(response, 201, '"id"')
        return response

    def update_user(self, client, user_id, name, job):
        with client.put(
            f"/api/users/{user_id}",
            json={"name": name, "job": job},
            name="update user",
            catch_response=True,
        ) as response:
            _verdict(response, 200, '"updatedAt"')
        return response

    def delete_user(self, client, user_id):
        with client.delete(
            f"/api/users/{user_id}", name="delete user", catch_response=True
        ) as response:
            _verdict(response, 204)
        return response

    # ---------- auth ----------
    def login(self, client, email, password):
        with client.post(
            "/api/login",
            json={"email": email, "password": password},
            name="login",
            catch_response=True,
        ) as response:
            _verdict(response, 200, '"token"')
        return response

    def login_without_password(self, client, email):
        with client.post(
            "/api/login",
            json={"email": email},
            name="login refused (400)",
            catch_response=True,
        ) as response:
            _verdict(response, 400, "Missing password")
        return response

    def register(self, client, email, password):
        with client.post(
            "/api/register",
            json={"email": email, "password": password},
            name="register",
            catch_response=True,
        ) as response:
            _verdict(response, 200, '"id"')
        return response

    # ---------- other documented reads ----------
    def products(self, client):
        with client.get(
            "/api/products", name="products", catch_response=True
        ) as response:
            _verdict(response, 200, "cap")
        return response

    def unknown_colors(self, client):
        with client.get(
            "/api/unknown", name="unknown colors", catch_response=True
        ) as response:
            _verdict(response, 200, "cerulean")
        return response

    def delayed_users(self, client, delay):
        with client.get(
            "/api/users",
            params={"page": 1, "delay": delay},
            name="list users with delay",
            catch_response=True,
        ) as response:
            _verdict(response, 200)
        return response
