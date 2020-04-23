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
        name="Image 01 MB GET",
    )


def image_01mb_get_scale_large(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-1mb/@@images/image/large",
        headers=headers,
        name="Image 01 MB GET (Scale Large)",
    )


def image_01mb_get_scale_preview(self):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Content-Type": "application/json",
    }
    self.client.get(
        "/testfolder-read/image-1mb/@@images/image/preview",
        headers=headers,
        name="Image 01 MB GET (Scale Preview)",
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
        name="Image 02 MB GET",
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
        name="Image 03 MB GET",
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
        image_01mb_get_scale_large: 20,
        image_01mb_get_scale_preview: 20,
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
