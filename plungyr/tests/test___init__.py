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


class Test_root_factory(_Base):

    def _callFUT(self, request):
        from .. import root_factory
        return root_factory(request)

    def test_no_existing_app_root(self):
        from pyramid.testing import DummyRequest
        _root = {}
        class _Conn(object):
            def root(self):
                return _root
        request = DummyRequest(_zodb_conn=_Conn())
        root = self._callFUT(request)
        self.failUnless(root is _root['app_root'])

    def test_w_existing_app_root(self):
        from pyramid.testing import DummyRequest
        _robj = object()
        _root = {'app_root': _robj}
        class _Conn(object):
            def root(self):
                return _root
        request = DummyRequest(_zodb_conn=_Conn())
        root = self._callFUT(request)
        self.failUnless(root is _robj)
