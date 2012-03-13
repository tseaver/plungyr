# Event-based award of badges to users for useful activity.

def _(text): #XXX
    return text


class Badge(object):
    """ A badge that a user can earn.
    """
    level = identifier = name = description = None # defined by derived

    kw_needed = ()

    def can_award(self, user, **kw):
        for kwn in self.kw_needed:
            if kwn not in kw:
                return False
        return True

    def on_new_topic(self, user, **kw):
        return None, None

    def on_edit(self, user, **kw):
        return None, None

    def on_reply(self, user, **kw):
        return None, None

    def on_vote(self, user, **kw):
        return None, None

    def on_accept(self, user, **kw):
        return None, None


class RoleBadge(Badge):

    def can_award(self, user, **kw):
        return (super(RoleBadge, self).can_award(user, **kw) and
                self.identifier not in user.badges)


class Inquirer(RoleBadge):
    level = 'bronze'
    identifier = 'inquirer'
    title = _(u'Inquirer')
    description = _(u'First asked question'),

    def on_new_topic(self, user, **kw):
        return user, None


class Editor(RoleBadge):
    level = 'bronze'
    identifier = 'editor'
    title = _(u'Editor')
    description = _(u'First edited post'),

    def on_edit(self, user, **kw):
        return user, None


class Troubleshooter(RoleBadge):
    level = 'silver'
    identifier = 'troubleshooter'
    title = _(u'Troubleshooter')
    description = _(u'First answered post'),
    kw_needed = ('post',)

    def on_accept(self, user, **kw):
        return kw['post'].author, None


class Critic(RoleBadge):
    level = 'bronze'
    identifier = 'critic'
    title = _(u'Critic')
    description = _(u'First down vote'),
    kw_needed = ('post', 'delta')

    def on_vote(self, user, **kw):
        if kw['delta'] < 0 and user != kw['post'].author:
            return user, None
        return None, None


class SelfCritic(RoleBadge):
    level = 'silver'
    identifier = 'self_critic'
    title = _(u'Self Critic')
    description = _(u'First down vote on own reply or question'),
    kw_needed = ('post', 'delta')

    def on_vote(self, user, **kw):
        if kw['delta'] < 0 and user == kw['post'].author:
            return user, None
        return None, None


class Answer(Badge):
    _threshhold = 1e6

    def _has_badge(self, user, payload):
        for badge, awarded_for in user.badges.items():
            if badge == self.identifier and payload in awarded_for:
                return True
        return False

    def can_award(self, user, **kw):
        post = kw.get('post')
        if post is None or not post.is_answer or post.votes < self._threshhold:
            return False
        # Check that this badge is not already awarded for the post
        return not self._has_badge(user, post.identifier)

    def on_accept(self, user, topic, post):
        return user, post.identifier

    def on_vote(self, user, post, delta):
        return user, post.identifier


class NiceAnswer(Answer):
    level = 'bronze'
    identifier = 'nice_answer'
    title = _(u'Nice Answer')
    description = _(u'Answer was upvoted 10 times')
    _threshhold = 10


class GoodAnswer(Answer):
    level = 'silver'
    identifier = 'good_answer'
    title = _(u'Good Answer')
    description = _(u'Answer was upvoted 25 times')
    _threshhold = 25


class GreatAnswer(Answer):
    level = 'gold'
    identifier = 'great_answer'
    title = _(u'Great Answer')
    description = _(u'Answer was upvoted 75 times')
    _threshhold = 75


class UniqueAnswer(Answer):
    level = 'platinum'
    identifier = 'uniqe_answer'
    title = _(u'Unique Answer')
    description = _(u'Answer was upvoted 150 times')
    _threshhold = 150


class Reversal(Answer):
    level = 'gold'
    identifier = 'reversal'
    title = _(u'Reversal')
    description = _(u'Provided answer of +20 score to a question of -5 score')

    def can_award(self, user, **kw):
        topic = kw.get('topic')
        post = kw.get('post')
        if (post is None or topic is None or not post.is_answer or
            post.votes < 20 or topic.votes > -5):
            return False
        # Check that this badge is not already awarded for the post
        return not self._has_badge(user, post.identifier)


class SelfLearner(Answer):
    level = 'silver'
    identifier = 'self_learner'
    title = _(u'self_learner')
    description = _(u'Answered your own question with at least 4 upvotes')

    def can_award(self, user, **kw):
        topic = kw.get('topic')
        post = kw.get('post')
        if (post is None or topic is None or not post.is_answer or
            post.author != topic.author or post.votes < 4):
            return False
        # Check that this badge is not already awarded for the post
        return not self._has_badge(user, post.identifier)


BADGES = [
    Inquirer(),
    Editor(),
    Troubleshooter(),
    Critic(),
    SelfCritic(),
    NiceAnswer(),
    GoodAnswer(),
    GreatAnswer(),
    UniqueAnswer(),
    Reversal(),
    SelfLearner(),
]


BADGES_BY_ID = dict((x.identifier, x) for x in BADGES)


def award_badges(event, user, **kw):
    """Try to avard all badges for the given event.
    
    The events correspond to the `on_X` callbacks on the badges.
    """
    method = 'on_%s' % event
    for badge in BADGES:
        if not badge.can_award(user, **kw):
            continue
        found_user, payload = getattr(badge, method)(user, **kw)
        if found_user is not None:
            found_user.badges.setdefault(badge.identifier, []).append(payload)
            # inactive or banned users don't get messages.
            #if found_user.is_active and not found_user.is_banned:
                #UserMessage(found_user,
                #            _(u'You earned the "%s" badge') % badge.name)
