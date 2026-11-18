from locust import task, TaskSet

from locust_files import get_locust_base_api


# the auth contract: two good paths and the documented refusal
class AuthFlow(TaskSet):
    def on_start(self):
        self.api = get_locust_base_api()

    @task(3)
    def login(self):
        self.api.login(self.client, "eve.holt@reqres.in", "cityslicka")

    @task(1)
    def login_refused(self):
        self.api.login_without_password(self.client, "eve.holt@reqres.in")

    @task(2)
    def register(self):
        self.api.register(self.client, "eve.holt@reqres.in", "pistol")
