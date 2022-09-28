import binascii
import transaction
from plone.restapi.services import Service
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from zExceptions import BadRequest


class TransactionsPatch(Service):
    def reply(self):
        body = json_body(self.request)
        message = revert(self.context, body["transaction_ids"])
        return json_compatible(message)


def revert(context, transactions_info=()):
    """ """
    tids = []
    descriptions = []

    for tid in transactions_info:
        tid = tid.split()
        if tid:
            tids.append(decode64(tid[0]))
            descriptions.append(tid[-1])

    if tids:
        ts = transaction.get()
        ts.note("Undo %s" % " ".join(descriptions))
        context._p_jar.db().undoMultiple(tids)
        try:
            ts.commit()
        except Exception:
            raise BadRequest({"errors": "Failed in undoing transactions"})

    msg = "Transactions have been reverted successfully."
    return {"message": msg}


def decode64(s, a2b=binascii.a2b_base64):
    __traceback_info__ = len(s), repr(s)
    return a2b(s + "\n")
