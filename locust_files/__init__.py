from locust_files.base_api import ReqResBaseApi


# the reference style: one place that hands every task set the same
# client wrapper, so a changed contract is touched in one file
def get_locust_base_api():
    return ReqResBaseApi()
