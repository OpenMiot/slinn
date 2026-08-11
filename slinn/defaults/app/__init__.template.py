from slinn.api import AppApi, ProjectApi


project = ProjectApi('.')
app = AppApi('./{name}', project)
