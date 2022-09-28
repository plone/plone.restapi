import binascii
import sys
from datetime import datetime as dt
from plone.restapi.services import Service


class TransactionsGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        total_num_of_transactions = (
            self.context._p_jar.db().undoInfo(0, sys.maxsize).__len__()
        )
        total_transactions = self.context._p_jar.db().undoInfo(
            0, total_num_of_transactions
        )

        for transaction in total_transactions:
            transaction["username"] = transaction["user_name"]
            del transaction["user_name"]
            transaction["time"] = t = dt.fromtimestamp(
                int(transaction["time"])
            ).isoformat()
            desc = transaction["description"]
            tid = transaction["id"]
            if desc:
                desc = desc.split()
                d1 = desc[0]
                desc = " ".join(desc[1:])
                if len(desc) > 60:
                    desc = desc[:56] + " ..."
                tid = f"{encode64(tid)} {t} {d1} {desc}"
            else:
                tid = f"{encode64(tid)} {t}"
            transaction["id"] = tid

        return total_transactions


def encode64(s, b2a=binascii.b2a_base64):
    if len(s) < 58:
        return b2a(s).decode("ascii")
    r = []
    a = r.append
    for i in range(0, len(s), 57):
        a(b2a(s[i : i + 57])[:-1])
    return (b"".join(r)).decode("ascii")
