import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from ..views import plungyr_main
        return plungyr_main(context, request)
        

    def test_my_view(self):
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['purl'], 'http://example.com/')
