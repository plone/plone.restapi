from locust import HttpUser, task

class QuerystringSearchAnonymousUser(HttpUser):

    @task
    def querystring_search_root(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4=",
            "Content-Type": "application/json",
        }
        self.client.post(
            "/@querystring-search",
            headers=headers,
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"]
                    }
                ]
            },
            name="Querystring Search (Root)",
        )


    @task
    def querystring_search_root_fullobjects_true(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4=",
            "Content-Type": "application/json",
        }
        self.client.post(
            "/@querystring-search",
            headers=headers,
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"]
                    }
                ],
                "fullobjects": 1
            },
            name="Querystring Search (Root, Fullobjects=1)",
        )


    @task
    def querystring_search_content(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4=",
            "Content-Type": "application/json",
        }
        self.client.post(
            "/testfolder-read/document/@querystring-search",
            headers=headers,
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"]
                    }
                ]
            },
            name="Querystring Search (Content)",
        )


    @task
    def querystring_search_content_fullobjects_true(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic YWRtaW46YWRtaW4=",
            "Content-Type": "application/json",
        }
        self.client.post(
            "/testfolder-read/document/@querystring-search",
            headers=headers,
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"]
                    }
                ],
                "fullobjects": 1
            },
            name="Querystring Search (Content, Fullobjects=1)",
        )
