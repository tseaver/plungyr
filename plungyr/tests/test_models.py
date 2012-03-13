import unittest


class _Base(unittest.TestCase):

    def failUnless(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertTrue(predicate)

    def failIf(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertFalse(predicate)


class Test__hotness(_Base):

    def _callFUT(self, created, votes):
        from ..models import hotness
        return hotness(created, votes)

    def test_it(self):
        from datetime import datetime
        _EPOCH = datetime(2012, 03, 11, 12, 0, 0)
        _CHECKING = [
            ((2012, 03, 12, 12, 0, 0), 0, 0.0),
        ]
        for dateargs, votes, expected in _CHECKING:
            when = datetime(*dateargs)
            self.assertEqual(self._callFUT(when, votes), expected)


class PlungyrTests(_Base):

    def _getTargetClass(self):
        from ..models import Plungyr
        return Plungyr

    def _makeOne(self):
        return self._getTargetClass()()

    def test_ctor(self):
        from repoze.folder import Folder
        plungyr = self._makeOne()
        self.assertEqual(plungyr.__name__, None)
        self.assertEqual(plungyr.__parent__, None)
        self.failUnless(isinstance(plungyr['profiles'], Folder))
