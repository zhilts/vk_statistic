from fabric.context_managers import lcd
from fabric.decorators import task
from fabric.operations import local


@task()
def pysetup():
    with lcd('./vk_fetch'):
        local('fab pysetup')