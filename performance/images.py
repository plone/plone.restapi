from locust import HttpLocust, TaskSet, between


def image_01mb_get(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-1mb/@@images/image.jpeg",
        headers=headers,
        name="Image 1 MB GET",
    )


def image_02mb_get(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-2mb/@@images/image.jpeg",
        headers=headers,
        name="Image 2 MB GET",
    )


def image_03mb_get(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-3mb/@@images/image.jpeg",
        headers=headers,
        name="Image 3 MB GET",
    )


def image_10mb_get(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-10mb/@@images/image.jpeg",
        headers=headers,
        name="Image 10 MB GET",
    )


class UserBehavior(TaskSet):
    tasks = {
        image_01mb_get: 10,
        image_02mb_get: 10,
        image_03mb_get: 10,
        image_10mb_get: 5,
    }

    def on_start(self):
        # login(self)
        pass

    def on_stop(self):
        # logout(self)
        pass


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
