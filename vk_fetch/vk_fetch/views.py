from django.http import HttpResponse
from django.shortcuts import redirect


def main_user(user_id, viewer_id):
    # todo: TBD
    return HttpResponse('Works')


def main_view(request):
    def get_param(name):
        return int(request.GET.get(name))

    viewer_id = get_param('viewer_id')
    user_id = get_param('user_id')
    group_id = get_param('group_id')
    if user_id != 0:
        return main_user(user_id, viewer_id)
    elif group_id != 0:
        return redirect('users-by-group-as-user', group_id=group_id, viewer_id=viewer_id)
    raise NotImplementedError
