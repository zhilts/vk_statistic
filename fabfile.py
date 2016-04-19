from fabric.context_managers import lcd
from fabric.decorators import task
from fabric.operations import local
from fabric.api import settings


class Stashed(object):
    def __enter__(self):
        local('git stash')

    def __exit__(self, exc_type, exc_val, exc_tb):
        local('git stash pop')


@task()
def pysetup():
    with lcd('./vk_fetch'):
        local('fab pysetup')


@task()
def runserver():
    with lcd('./vk_fetch'):
        local('fab runserver')


@task()
def start():
    with lcd('vk_fetch'):
        local('gunicorn settings.wsgi --bind 0.0.0.0:$PORT')


def checkout(branch):
    with settings(warn_only=True):
        res = local('git rev-parse --verify {branch}'.format(branch=branch))
        branch_exists = res.succeeded
        if branch_exists:
            local('git checkout {branch} && git pull'.format(branch=branch))
        else:
            local('git checkout -b {branch} origin/{branch}'.format(branch=branch))


def git_current_branch():
    return local('git rev-parse --abbrev-ref HEAD', capture=True)


@task()
def deploy():
    start_branch = git_current_branch()
    deploy_branch = 'develop'
    with Stashed():
        checkout(deploy_branch)

        try:
            local('git remote add heroku git@heroku.com:vk-fetch.git ')
        except:
            pass
        local('git fetch --tags origin')
        local('git merge --log --no-edit tags/current-release')
        local('git push --force --set-upstream heroku {deploy_branch}:master'.format(deploy_branch=deploy_branch))
        checkout(start_branch)


@task()
def vk(command):
    with lcd('vk_fetch'):
        local('fab {command}'.format(command=command))


# ALIASES
@task()
def rdb():
    local('fab vk:rdb')


@task()
def start_fetching():
    local('fab vk:"manage:start_fetching"')
