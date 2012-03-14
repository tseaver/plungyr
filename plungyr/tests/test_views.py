import unittest

class _Base(unittest.TestCase):

    def setUp(self):
        from pyramid.testing import setUp
        self.config = setUp()

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()

    def failUnless(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertTrue(predicate)

    def failIf(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertFalse(predicate)


class ViewTests(_Base):

    def _callFUT(self, context, request):
        from ..views import plungyr_main
        return plungyr_main(context, request)
        

    def test_my_view(self):
        from pyramid.testing import DummyModel
        from pyramid.testing import DummyRequest
        context = DummyModel()
        request = DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['purl'], 'http://example.com/')
