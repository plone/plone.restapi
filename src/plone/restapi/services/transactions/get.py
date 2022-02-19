from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


class TransactionsGet(Service):
    def reply(self):
        # get parameters
        start = self.request.form.get("start", 0)
        end = self.request.form.get("end", 100)
        try:
            start = int(start)
        except ValueError as e:
            self.request.response.setStatus(422)
            return dict(
                error=dict(
                    type="Invalid parameter 'start'",
                    message=e.args[0],
                )
            )
        try:
            end = int(end)
        except ValueError as e:
            self.request.response.setStatus(422)
            return dict(
                error=dict(
                    type="Invalid parameter 'end'",
                    message=e.args[0],
                )
            )

        db = self.context._p_jar.db()
        return json_compatible(db.undoLog(start, end))
        return db.undoLog(0, 100, filter=(lambda user_name: "Plone _perftest"))

        # return {
        #     "@id": f"{self.context.absolute_url()}/@transactions",
        #     "items": []
        # }
