from requests import session

from entities.models import VkUser
from runner.tasks import update_users


class UserIdMiddleware:
    def process_request(self, request):
        viewer_id = request.GET.get('viewer_id', None)
        if viewer_id:
            session.user_id = viewer_id


class CreateUserMiddleware:
    def process_request(self, request):
        user_id = getattr(session, 'user_id', None)
        if user_id is not None and not VkUser.objects.filter(id=user_id).exists():
            update_users.delay([user_id])
