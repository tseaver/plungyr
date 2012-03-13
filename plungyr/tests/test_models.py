import unittest

_MARKER = object()


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


class PhotoTests(_Base):

    def _getTargetClass(self):
        from ..models import Photo
        return Photo

    def _makeOne(self, file=_MARKER):
        if file is _MARKER:
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
        from .. import models
        WHEN = datetime.now()
        user = _User()
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
        WHEN = datetime.now()
        user = _User()
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

    def test_edit_no_date_no_editor_no___parent__(self):
        from datetime import datetime
        from datetime import timedelta
        from .. import models
        BEFORE = datetime.now()
        AFTER = BEFORE + timedelta(1)
        user = _User()
        with _Monkey(models, _NOW=BEFORE):
            post = self._makeOne(user, 'TEXT')
        with _Monkey(models, _NOW=AFTER):
            post.edit('NEW TEXT')
        self.failUnless(post.editor is user)
        self.assertEqual(post.modified, AFTER)
        self.assertEqual(user.points, 70)
        self.assertEqual(user.badges, {'editor': [None]})

    def test_edit_w_date_w_editor_w___parent__(self):
        from datetime import datetime
        from datetime import timedelta
        from repoze.folder import Folder
        from .. import models
        parent = Folder()
        BEFORE = datetime.now()
        AFTER = BEFORE + timedelta(1)
        author = _User()
        editor = _User()
        with _Monkey(models, _NOW=BEFORE):
            parent['testing'] = post = self._makeOne(author, 'TEXT')
        post.edit('NEW TEXT', editor, AFTER)
        self.failUnless(post.editor is editor)
        self.assertEqual(post.modified, AFTER)
        self.assertEqual(author.points, 50)
        self.assertEqual(editor.points, 20)
        self.assertEqual(editor.badges, {'editor': [None]})
        self.failUnless('hotness' in parent.__dict__)


class TopicTests(_Base):

    def _getTargetClass(self):
        from ..models import Topic
        return Topic

    def _makeOne(self, title, text, user, date=None):
        return self._getTargetClass()(title, text, user, date)

    def test_ctor_no_date(self):
        from datetime import datetime
        from .. import models
        WHEN = datetime.now()
        user = _User()
        with _Monkey(models, _NOW=WHEN):
            topic = self._makeOne('TITLE', 'TEXT', user)
        self.assertEqual(topic.title, 'TITLE')
        self.assertEqual(topic.votes, 0)
        self.assertEqual(topic.author, user)
        self.assertEqual(topic.answer, None)
        self.assertEqual(topic.hotness, models.hotness(WHEN, 0))
        self.assertEqual(topic.created, WHEN)
        self.assertEqual(topic.modified, WHEN)
        question = topic['question']
        self.assertEqual(question.author, user)
        self.assertEqual(question.text, 'TEXT')
        self.assertEqual(question.created, WHEN)
        self.assertEqual(question.modified, WHEN)
        self.assertEqual(question.is_question, True)
        self.assertEqual(question.is_answer, False)

    def test_accept_answer_w_non_contained_answer(self):
        from ..models import Post
        author = _User()
        topic = self._makeOne('TITLE', 'TEXT', author)
        shooter = _User()
        bogus = Post(shooter, 'ANSWER')
        self.assertRaises(ValueError, topic.accept_answer, bogus)

    def test_accept_answer_w_real_answer(self):
        from ..models import Post
        author = _User()
        topic = self._makeOne('TITLE', 'TEXT', author)
        shooter = _User()
        reply = topic['reply'] = Post(shooter, 'ANSWER')
        topic.accept_answer(reply)
        self.failUnless(topic.answer is reply)
        self.failUnless(reply.is_answer)

    def test_accept_answer_w_prior_answer(self):
        from ..models import Post
        author = _User()
        topic = self._makeOne('TITLE', 'TEXT', author)
        shooter = _User()
        good = topic['good'] = Post(shooter, 'ANSWER')
        topic.accept_answer(good)
        better = topic['better'] = Post(shooter, 'ANSWER')
        topic.accept_answer(better)
        self.failUnless(topic.answer is better)
        self.failIf(good.is_answer)
        self.failUnless(better.is_answer)


class _User(object):
    def __init__(self):
        self.points = 0
        self.badges = {}
    def touch_activity(self, points):
        self.points += points


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
