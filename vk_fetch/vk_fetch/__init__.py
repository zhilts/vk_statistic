from requests import session


class UserIdMiddleware:
    def process_request(self, request):
        viewer_id = request.GET.get('viewer_id', None)
        if viewer_id:
            session.user_id = viewer_id
