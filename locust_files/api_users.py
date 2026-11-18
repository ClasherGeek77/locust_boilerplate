from locust import SequentialTaskSet, task, TaskSet

from locust_files import get_locust_base_api


# the read flows, weighted like a curious client: list more than inspect.
# every call asserts its own documented contract inside base_api, so a
# task set line is one intent and nothing else
class UsersReadFlow(TaskSet):
    def on_start(self):
        self.api = get_locust_base_api()

    @task(3)
    def list_a_page(self):
        self.api.list_users(self.client, 1)

    @task(2)
    def get_one_user(self):
        self.api.get_user(self.client, 2)

    @task(1)
    def get_missing_user_is_404(self):
        self.api.get_unknown_user(self.client, 23)

    @task(2)
    def products(self):
        self.api.products(self.client)

    @task(1)
    def colors(self):
        self.api.unknown_colors(self.client)


# the write flow in order, the reference pattern for a journey:
# create, update, delete. the clone answers create with the documented
# id "4" and stores nothing, like live reqres is stateless
class UsersWriteFlow(SequentialTaskSet):
    def on_start(self):
        self.api = get_locust_base_api()

    @task
    def create_user(self):
        response = self.api.create_user(self.client, "load-user", "tester")
        self.created = response.json()

    @task
    def update_user(self):
        self.api.update_user(
            self.client, self.created["id"], "load-user", "senior tester"
        )

    @task
    def delete_user(self):
        self.api.delete_user(self.client, self.created["id"])

    @task
    def sleep_probe(self):
        # the documented delay parameter: same contract, slower server
        self.api.delayed_users(self.client, 1)
