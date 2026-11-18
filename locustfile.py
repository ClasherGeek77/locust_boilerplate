import os

from locust import FastHttpUser, between

from locust_files.api_auth import AuthFlow
from locust_files.api_users import UsersReadFlow, UsersWriteFlow

# same rule as the whole portfolio: no internet, the target is the local
# clone; --host or HOST overrides, the default is the reqresin clone
os.environ.setdefault("HOST", "http://localhost:40000")


class ReqResUser(FastHttpUser):
    # the clone answers fast on a 2 core machine, keep the think time
    # small so one run actually stresses it
    wait_time = between(0.2, 0.8)
    # weights on the flows themselves: reads dominate like a real client
    tasks = {UsersReadFlow: 6, UsersWriteFlow: 2, AuthFlow: 2}
