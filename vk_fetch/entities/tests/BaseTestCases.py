import unittest
from mixer.backend.django import Mixer


class BaseTestCases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCases, self).__init__(*args, **kwargs)
        self.mixer = Mixer()

        # def setUp(self):
        #     self.app.config['TESTING'] = True
        #     self.db.drop_all()
        #     self.db.create_all()
        #
        # def tearDown(self):
        #     self.db.session.commit()
        #     self.db.session.remove()
