from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


class TransactionsGet(Service):
    def reply(self):
        db = self.context._p_jar.db()
        return json_compatible(db.undoLog(0, 100))
        return db.undoLog(0, 100, filter=(lambda user_name: "Plone _perftest"))

        # return {
        #     "@id": f"{self.context.absolute_url()}/@transactions",
        #     "items": []
        # }
