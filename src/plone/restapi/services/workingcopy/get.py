from plone.restapi.serializer.working_copy import WorkingCopyInfo
from plone.restapi.services import Service


class GetWorkingCopy(Service):
    def reply(self):
        baseline, working_copy = WorkingCopyInfo(self.context).get_working_copy_info()

        return {"working_copy": working_copy, "working_copy_of": baseline}
