import re
from fabric.api import settings
from fabric.context_managers import lcd
from fabric.decorators import task
from fabric.operations import local

KEY_PATH_ENV = 'HEROKU_KEY'


class Stashed(object):
    def __init__(self):
        super(Stashed, self).__init__()
        self.stashed = False

    def __enter__(self):
        with settings(warn_only=True):
            result = local('git diff-index --quiet HEAD --')
            if result.return_code == 0:
                self.stashed = False
            else:
                self.stashed = True
                local('git stash')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stashed:
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
def start(mode='release'):
    with lcd('vk_fetch'):
        if mode == 'release':
            local('gunicorn settings.wsgi --bind 0.0.0.0:$PORT')
        else:
            local('./pyenv.sh gunicorn settings.wsgi --bind 0.0.0.0:$PORT')


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
    with Stashed():
        checkout('master')

        with settings(warn_only=True):
            local('git remote add staging git@heroku.com:vk-fetch.git ')
        local('git fetch origin')
        local('git pull origin master')
        local('git fetch staging')
        local('git merge --log --no-edit release')
        local('git push --force --set-upstream staging master:master')
        local('heroku run fab migrate')
        local('heroku run fab collectstatic')
        checkout(start_branch)


@task()
def release_develop():
    start_branch = git_current_branch()
    with Stashed():
        checkout('release')

        local('git fetch origin')
        local('git merge --log --no-edit origin/develop')
        local('git push --set-upstream origin release')

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
def migrate():
    local('fab vk:migrate')


@task()
def start_fetching():
    local('fab vk:"manage:start_fetching"')


@task()
def collectstatic():
    local('fab vk:"manage:\'collectstatic --noinput\'"')
