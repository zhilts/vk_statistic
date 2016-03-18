from fabric.decorators import task
from fabric.operations import local


@task()
def pysetup():
    local('./pysetup.sh')