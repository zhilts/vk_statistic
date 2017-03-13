from entities.models import VkUser
from runner.tasks import update_users


class CreateUserMiddleware:
    def process_request(self, request):
        user_id = request.GET.get('viewer_id', None)
        if user_id is not None and not VkUser.objects.filter(id=user_id).exists():
            update_users.delay([user_id])


class CurrentUserMiddleware:
    def process_request(self, request):
        user_id = request.GET.get('viewer_id', None)
        print(user_id)
        if user_id is not None:
            request.session['user_id'] = user_id
