from plone.restapi.services import Service
from plone.restapi.serializer.working_copy import WorkingCopyInfo


class GetWorkingCopy(Service):
    def reply(self):
        baseline, working_copy = WorkingCopyInfo(self.context).get_working_copy_info()

        return {"working_copy": working_copy, "working_copy_of": baseline}
