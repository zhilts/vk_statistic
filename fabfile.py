import re
from fabric.context_managers import lcd
from fabric.decorators import task
from fabric.operations import local
from fabric.api import settings

release_tag = 'current-release'


class Stashed(object):
    def __init__(self):
        super(Stashed, self).__init__()
        self.stashed = False

    def __enter__(self):
        try:
            local('git stash')
            self.stashed = True
        except:
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stashed:
            local('git stash pop')


class SshKey(object):
    def __init__(self, key_path):
        super(SshKey, self).__init__()
        self.key_path = key_path

    def __enter__(self):
        local('eval "$(ssh-agent -s)"')
        local('ssh-add {key_path}'.format(key_path=self.key_path))

    def __exit__(self, exc_type, exc_val, exc_tb):
        local('kill $SSH_AGENT_PID')


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
    deploy_branch = 'staging'
    with Stashed():
        checkout(deploy_branch)

        try:
            local('git remote add staging git@heroku.com:vk-fetch.git ')
        except:
            pass
        local('git fetch --tags origin')
        local('git merge --log --no-edit tags/{release_tag}'.format(release_tag=release_tag))
        local('git push --force --set-upstream staging {deploy_branch}:master'.format(deploy_branch=deploy_branch))
        checkout(start_branch)


@task()
def release_develop():
    start_branch = git_current_branch()
    tags_str = local('git tag -l --contains HEAD', capture=True)
    tags = re.compile('[\w-]+', re.MULTILINE).findall(tags_str)
    with Stashed():
        with SshKey('~/.ssh/id_rsa'):
            if release_tag not in tags:
                checkout('tags/{release_tag}'.format(release_tag=release_tag))
            local('git fetch origin')
            local('git merge --log --no-edit origin/develop')
            local('git tag -a "{release_tag}" -f')
            local('git push origin --tags -f')
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
