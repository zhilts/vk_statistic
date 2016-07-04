from entities.models import VkGroup, VkPost, VkUser
from entities.tests.BaseTestCases import BaseTestCases

from sure import it

from entities.views import UserListView


class TestUserListView(BaseTestCases):
    def setUp(self):
        super(TestUserListView, self).setUp()
        self.df = df = lambda x: None

        df.group = self.mixer.blend(VkGroup)

    def __generate_users_and_posts(self, user_count=5, post_count=5):
        df = self.df
        df.posts = self.mixer.cycle(post_count).blend(VkPost)
        df.users = self.mixer.cycle(user_count).blend(VkUser)
        count = 0
        for user in df.users:
            for index in range(count):
                post = df.posts[index % post_count]
                post.likes.add(user)
            count += 1

    def test__get_queryset__returns_limited_users(self):
        df = self.df
        self.__generate_users_and_posts(user_count=20)
        request = lambda: None
        request.GET = dict()

        # request.GET['']

        res = UserListView(request=request, kwargs=dict(group_id=df.group.pk)).get_queryset()

        assert it(res).should_not.have.length_of(10)

    # def test__get_queryset__
