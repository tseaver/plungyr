import datetime
import math

from persistent import Persistent
from repoze.folder import Folder
from ZODB.blob import Blob

from .badges import award_badges

_NOW = None
def _now():
    if _NOW is not None:
        return _NOW
    return datetime.datetime.utcnow() #pragma NO COVERAGE


_EPOCH = datetime.datetime(1970, 1, 1)
_BASETIME = 1134028003 # 2005-12-8T007:46:42Z

def hotness(created, votes, epoch=None):
    if epoch is None:
        epoch = _EPOCH
    # algorithm from code.reddit.com by CondeNet, Inc.
    delta = created - epoch
    secs = (delta.days * 86400 + delta.seconds +
            (delta.microseconds / 1e6)) - _BASETIME
    order = math.log(max(abs(votes), 1), 10)
    sign = 1 if votes > 0 else -1 if votes < 0 else 0
    return round(order + sign * secs / 45000, 7)


class Plungyr(Folder):
    __parent__ = __name__ = None
    def __init__(self):
        super(Plungyr, self).__init__()
        self['profiles'] = Folder()


class Profile(Folder):

    def __init__(self):
        super(Profile, self).__init__()
        self.badges = {}    #badge_type -> counter
        self.counter = 0    #activity
        self.photo = None
        self.last_activity = _now()

    def touch_activity(self, points):
        self.counter += points
        self.last_activity = _now()


class Photo(Persistent):

    blob = None
    def __init__(self, file=None):
        if file is not None:
            self.blob = Blob(file)


class Post(Folder):

    def __init__(self, author, text, date=None, is_reply=True):
        super(Post, self).__init__()
        self.author = author
        self.editor = None
        self.text = text
        self.author = author
        self.is_deleted = False
        self.is_answer = False
        self.is_question = not is_reply
        if date is None:
            date = _now()
        self.created = self.modified = date
        self.votes = 0
        self.edits = 0
        self.comment_count = 0
        author.touch_activity(50)
        if is_reply:
            award_badges('reply', author, post=self)

    def edit(self, new_text, editor=None, date=None):
        """Update the post contents
        
        - (NOT YET) moves the current one into the attic.
        """
        if editor is None:
            editor = self.author
        if date is None:
            date = _now()

        #PostRevision(self)
        self.text = new_text
        self.editor = editor
        self.modified = date
        if self.__parent__:
            self.__parent__.hotness = hotness(date, 0)
        self.edits += 1

        award_badges('edit', editor, post=self)
        editor.touch_activity(20)


class Topic(Folder):

    def __init__(self, title, text, user, date=None):
        super(Topic, self).__init__()
        self.title = title
        self.votes = 0
        self['question'] = question = Post(user, text, date, is_reply=False)
        self.author = question.author
        self.answer = None
        self.hotness = hotness(self.created, 0)
        award_badges('new_topic', user, topic=self)

    @property
    def created(self):
        return self['question'].created

    @property
    def modified(self):
        return max([x.modified for x in self.values()])

    def accept_answer(self, post):
        """Accept a post as answer.
        """
        if post.__parent__ is not self:
            raise ValueError('that post does not belong to the topic')
        if self.answer is not None:
            self.answer.is_answer = False
            # XXX
            #loser = self.answer.author
            #loser.reputation -= settings.REPUTATION_MAP['LOSE_ON_LOST_ANSWER']
        post.is_answer = True
        # XXX
        #gainer = post.author
        #gainer.reputation += settings.REPUTATION_MAP['GAIN_ON_ACCEPTED_ANSWER']
        self.answer = post
        award_badges('accept', post.author, topic=self, post=post)


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Plungyr()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
