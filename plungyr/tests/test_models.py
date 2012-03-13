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


class ProfileTests(_Base):

    def _getTargetClass(self):
        from ..models import Profile
        return Profile

    def _makeOne(self):
        return self._getTargetClass()()

    def test_ctor(self):
        from datetime import datetime
        from .. import models
        WHEN = datetime.now()
        with _Monkey(models, _NOW=WHEN):
            profile = self._makeOne()
            self.assertEqual(profile.badges, {})
            self.assertEqual(profile.counter, 0)
            self.assertEqual(profile.photo, None)
            self.assertEqual(profile.last_activity, WHEN)

    def test_touch_activity(self):
        from datetime import datetime
        from datetime import timedelta
        from .. import models
        BEFORE = datetime.now()
        AFTER = BEFORE + timedelta(1)
        with _Monkey(models, _NOW=BEFORE):
            profile = self._makeOne()
        with _Monkey(models, _NOW=AFTER):
            profile.touch_activity(20)
            self.assertEqual(profile.counter, 20)
            self.assertEqual(profile.last_activity, AFTER)


_marker = object()
class PhotoTests(_Base):

    def _getTargetClass(self):
        from ..models import Photo
        return Photo

    def _makeOne(self, file=_marker):
        if file is _marker:
            return self._getTargetClass()()
        return self._getTargetClass()(file)

    def test_ctor_no_file(self):
        photo = self._makeOne()
        self.assertEqual(photo.blob, None)

    def test_ctor_w_file(self):
        from ZODB.blob import Blob
        FILE = 'FILE'
        photo = self._makeOne(FILE)
        self.failUnless(isinstance(photo.blob, Blob))
        self.assertEqual(photo.blob.open().read(), FILE)


class PostTests(_Base):

    def _getTargetClass(self):
        from ..models import Post
        return Post

    def _makeOne(self, author, text, date=None, is_reply=True):
        return self._getTargetClass()(author, text, date, is_reply)

    def test_ctor_no_date_not_reply(self):
        from datetime import datetime
        from pyramid.testing import DummyModel
        from .. import models
        WHEN = datetime.now()
        user = DummyModel(points=0, badges={})
        def touch_activity(points):
            user.points += points
        user.touch_activity = touch_activity
        with _Monkey(models, _NOW=WHEN):
            post = self._makeOne(user, 'TEXT', is_reply=False)
            self.failUnless(post.author is user)
            self.assertEqual(post.editor, None)
            self.assertEqual(post.text, 'TEXT')
            self.assertEqual(post.is_deleted, False)
            self.assertEqual(post.is_answer, False)
            self.assertEqual(post.is_question, True)
            self.assertEqual(post.created, WHEN)
            self.assertEqual(post.modified, WHEN)
            self.assertEqual(post.votes, 0)
            self.assertEqual(post.edits, 0)
            self.assertEqual(post.comment_count, 0)
            self.assertEqual(user.points, 50)

    def test_ctor_w_date_and_is_reply(self):
        from datetime import datetime
        from pyramid.testing import DummyModel
        WHEN = datetime.now()
        user = DummyModel(points=0, badges={})
        def touch_activity(points):
            user.points += points
        user.touch_activity = touch_activity
        post = self._makeOne(user, 'TEXT', WHEN, is_reply=True)
        self.failUnless(post.author is user)
        self.assertEqual(post.editor, None)
        self.assertEqual(post.text, 'TEXT')
        self.assertEqual(post.is_deleted, False)
        self.assertEqual(post.is_answer, False)
        self.assertEqual(post.is_question, False)
        self.assertEqual(post.created, WHEN)
        self.assertEqual(post.modified, WHEN)
        self.assertEqual(post.votes, 0)
        self.assertEqual(post.edits, 0)
        self.assertEqual(post.comment_count, 0)
        self.assertEqual(user.points, 50)
        self.assertEqual(user.badges, {}) #no badge currenly does 'on_reply'


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
