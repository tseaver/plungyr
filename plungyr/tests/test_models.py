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

    def test_w_dates(self):
        from datetime import datetime
        _EPOCH = datetime(2012, 03, 11, 12, 0, 0)
        _CHECKING = [
            ((2012, 03, 12, 10, 0, 0)),
            ((2012, 03, 12, 11, 0, 0)),
            ((2012, 03, 12, 12, 0, 0)),
            ((2012, 03, 12, 13, 0, 0)),
            ((2012, 03, 12, 14, 0, 0)),
        ]
        last = -1e6
        for dateargs in _CHECKING:
            when = datetime(*dateargs)
            hotness = self._callFUT(when, 10)
            self.failUnless(hotness > last)
            last = hotness

    def test_w_votes(self):
        from datetime import datetime
        _EPOCH = datetime(2012, 03, 11, 12, 0, 0)
        _CHECKING = [
            ((2012, 03, 12, 12, 0, 0), -4),
            ((2012, 03, 12, 12, 0, 0), -1),
            ((2012, 03, 12, 12, 0, 0), 0),
            ((2012, 03, 12, 12, 0, 0), 1),
            ((2012, 03, 12, 12, 0, 0), 4),
        ]
        # Upvotes increase hotness
        last = -1e6
        for dateargs, votes in _CHECKING[2:]:
            when = datetime(*dateargs)
            hotness = self._callFUT(when, votes)
            self.failUnless(hotness > last)
            last = hotness
        # Downvotes also increase hotness
        last = -1e6
        for dateargs, votes in _CHECKING[0:3:-1]:
            when = datetime(*dateargs)
            hotness = self._callFUT(when, votes)
            self.failUnless(hotness > last)
            last = hotness


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


class _Monkey(object):

    def __init__(self, module, **replacements):
        self.module = module
        self.orig = {}
        self.replacements = replacements
        
    def __enter__(self):
        for k, v in self.replacements.items():
            orig = getattr(self.module, k, self)
            if orig is not self:
                self.orig[k] = orig
            setattr(self.module, k, v)

    def __exit__(self, *exc_info):
        for k, v in self.replacements.items():
            if k in self.orig:
                setattr(self.module, k, self.orig[k])
            else:
                delattr(self.module, k)
