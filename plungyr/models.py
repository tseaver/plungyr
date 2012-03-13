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
    return datetime.utcnow()
    

def _hotness(created, votes):
    # algorithm from code.reddit.com by CondeNet, Inc.
    delta = created - datetime(1970, 1, 1)
    secs = (delta.days * 86400 + delta.seconds +
            (delta.microseconds / 1e6)) - 1134028003
    order = math.log(max(abs(votes), 1), 10)
    sign = 1 if votes > 0 else -1 if votes < 0 else 0
    return round(order + sign * secs / 45000, 7)


class Plungyr(Folder):
    __parent__ = __name__ = None
    def __init__(self):
        self['profiles'] = Folder()
        self['topics'] = Folder()


class Profile(Folder):

    def __init__(self):
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
        self.topic.hotness = _hotness(date, 0)
        self.edits += 1

        award_badges('edit', editor, post=self)
        editor.touch_activity(20)


class Topic(Folder):

    def __init__(self, title, text, user, date=None):
        self.title = title
        self.votes = 0
        self['question'] = question = Post(user, text, date, is_reply=False)
        self.author = question.author
        self.answer = None
        when = self.created = self.modified = question.created
        self.hotness = _hotness(when, 0)
        award_badges('new_topic', user, topic=self)

    @property
    def created(self):
        return self['question'].created

    @property
    def modified(self):
        return max([x.modified for x in self])

    def accept_answer(self, post):
        """Accept a post as answer.
        """
        if post.identifier not in self:
            raise ValueError('that post does not belong to the topic')
        if self.answer is not None:
            self.answer.is_answer = False
            loser = self.answer.author
            loser.reputation -= settings.REPUTATION_MAP['LOSE_ON_LOST_ANSWER']
        post.is_answer = True
        gainer = post.author
        gainer.reputation += settings.REPUTATION_MAP['GAIN_ON_ACCEPTED_ANSWER']
        self.answer_author = post.author
        self.answer_date = post.created
        self.answer = post
        award_badges('accept', post.author, topic=self, post=post)


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Plungyr()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
