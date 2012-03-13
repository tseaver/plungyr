import unittest

class _Base(unittest.TestCase):

    def _makeOne(self):
        return self._getTargetClass()()

    def _makeUser(self, *badges):
        class _User(object):
            pass
        user = _User()
        user.badges = dict((x, [None]) for x in badges)
        return user

    def _makeTopic(self, author, votes=0):
        class _Topic(object):
            pass
        topic = _Topic()
        topic.author = author
        topic.votes = votes
        return topic

    def _makePost(self, author,
                  identifier='testpost', is_answer=False, votes=0):
        class _Post(object):
            pass
        post = _Post()
        post.author = author
        post.is_answer = is_answer
        post.identifier = identifier
        post.votes = votes
        return post

    def failUnless(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertTrue(predicate)

    def failIf(self, predicate):
        # Suppress unittest nannyism
        super(_Base, self).assertFalse(predicate)


class BadgeTests(_Base):

    def _getTargetClass(self):
        from ..badges import Badge
        return Badge

    def test_can_award_wo_kw_needed(self):
        badge = self._makeOne()
        self.failUnless(badge.can_award(self._makeUser()))

    def test_can_award_w_kw_needed_missing(self):
        badge = self._makeOne()
        badge.kw_needed = ('needed',)
        self.failIf(badge.can_award(object()))

    def test_can_award_w_kw_needed_provided(self):
        badge = self._makeOne()
        badge.kw_needed = ('needed',)
        self.failUnless(badge.can_award(object(), needed=object()))

    def test_on_new_topic(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        self.assertEqual(badge.on_new_topic(user, topic=topic), (None, None))

    def test_on_edit(self):
        badge = self._makeOne()
        user = self._makeUser()
        post = self._makePost(user)
        self.assertEqual(badge.on_edit(user, post=post), (None, None))

    def test_on_reply(self):
        badge = self._makeOne()
        user = self._makeUser()
        post = self._makePost(user)
        self.assertEqual(badge.on_reply(user, post=post), (None, None))

    def test_on_vote(self):
        badge = self._makeOne()
        user = self._makeUser()
        post = self._makePost(user)
        self.assertEqual(badge.on_vote(user, post=post, delta=1), (None, None))

    def test_on_accept(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        post = self._makePost(user)
        self.assertEqual(badge.on_accept(user, topic=topic, post=post),
                        (None, None))


class RoleBadgeTests(_Base):

    def _getTargetClass(self):
        from ..badges import RoleBadge
        return RoleBadge

    def test_can_award_wo_kw_needed_user_has_no_badges(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        self.failUnless(badge.can_award(self._makeUser()))

    def test_can_award_wo_kw_needed_user_has_badge(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        self.failIf(badge.can_award(self._makeUser('testing')))

    def test_can_award_w_kw_needed_missing_user_has_no_badges(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        badge.kw_needed = ('needed',)
        self.failIf(badge.can_award(self._makeUser()))

    def test_can_award_w_kw_needed_provided_user_has_no_badges(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        badge.kw_needed = ('needed',)
        self.failUnless(badge.can_award(self._makeUser(), needed=object()))

    def test_can_award_w_kw_needed_provided_user_has_badge(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        badge.kw_needed = ('needed',)
        self.failIf(badge.can_award(self._makeUser('testing'), needed=object()))


class InquirerTests(_Base):

    def _getTargetClass(self):
        from ..badges import Inquirer
        return Inquirer

    def test_on_new_topic(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        self.assertEqual(badge.on_new_topic(user, topic=topic), (user, None))


class EditorTests(_Base):

    def _getTargetClass(self):
        from ..badges import Editor
        return Editor

    def test_on_edit(self):
        badge = self._makeOne()
        user = self._makeUser()
        post = self._makePost(user)
        self.assertEqual(badge.on_edit(user, post=post), (user, None))


class TroubleshooterTests(_Base):

    def _getTargetClass(self):
        from ..badges import Troubleshooter
        return Troubleshooter

    def test_on_accept(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        post = self._makePost(user)
        self.assertEqual(badge.on_accept(user, topic=topic, post=post),
                        (user, None))


class CriticTests(_Base):

    def _getTargetClass(self):
        from ..badges import Critic
        return Critic

    def test_on_vote_same_user_upvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(author, post=post, delta=1),
                         (None, None))

    def test_on_vote_same_user_downvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(author, post=post, delta=-1),
                         (None, None))

    def test_on_vote_different_user_upvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        critic = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(critic, post=post, delta=1),
                         (None, None))

    def test_on_vote_different_user_downvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        critic = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(critic, post=post, delta=-1),
                         (critic, None))


class SelfCriticTests(_Base):

    def _getTargetClass(self):
        from ..badges import SelfCritic
        return SelfCritic

    def test_on_vote_same_user_upvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(author, post=post, delta=1),
                         (None, None))

    def test_on_vote_same_user_downvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(author, post=post, delta=-1),
                         (author, None))

    def test_on_vote_different_user_upvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        critic = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(critic, post=post, delta=1),
                         (None, None))

    def test_on_vote_different_user_downvote(self):
        badge = self._makeOne()
        author = self._makeUser()
        critic = self._makeUser()
        post = self._makePost(author)
        self.assertEqual(badge.on_vote(critic, post=post, delta=-1),
                         (None, None))


class AnswerTests(_Base):

    def _getTargetClass(self):
        from ..badges import Answer
        return Answer

    def test_can_award_no_post(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        self.failIf(badge.can_award(user))

    def test_can_award_w_post_not_is_answer(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user)
        self.failIf(badge.can_award(user, post=post))

    def test_can_award_w_post_is_answer_no_votes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True)
        self.failIf(badge.can_award(user, post=post))

    def test_can_award_w_post_is_answer_w_votes_user_has_no_badges(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=1e6+1)
        self.failUnless(badge.can_award(user, post=post))

    def test_can_award_w_post_is_answer_w_votes_user_has_badge(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=1e6+1)
        user.badges['testing'] = ids = []
        ids.append(post.identifier)
        self.failIf(badge.can_award(user, post=post))

    def test_on_accept(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        post = self._makePost(user)
        self.assertEqual(badge.on_accept(user, topic=topic, post=post),
                        (user, post.identifier))

    def test_on_vote(self):
        badge = self._makeOne()
        user = self._makeUser()
        topic = self._makeTopic(user)
        post = self._makePost(user)
        self.assertEqual(badge.on_vote(user, post=post, delta=1),
                        (user, post.identifier))


class ReversalTests(_Base):

    def _getTargetClass(self):
        from ..badges import Reversal
        return Reversal

    def test_can_award_no_post(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        self.failIf(badge.can_award(user))

    def test_can_award_w_post_no_topic(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user)
        self.failIf(badge.can_award(user, post=post))

    def test_can_award_w_post_not_is_answer(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user)
        topic = self._makeTopic(user)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_no_post_upvotes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True)
        topic = self._makeTopic(user)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_w_post_upvotes_no_topic_downvotes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=21)
        topic = self._makeTopic(user)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_w_post_upvotes_w_topic_downvotes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=21)
        topic = self._makeTopic(user, votes=-6)
        self.failUnless(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_upvotes_w_topic_downvotes_user_has_badge(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=21)
        topic = self._makeTopic(user, votes=-6)
        user.badges['testing'] = ids = []
        ids.append(post.identifier)
        self.failIf(badge.can_award(user, post=post, topic=topic))


class SelfLearnerTests(_Base):

    def _getTargetClass(self):
        from ..badges import SelfLearner
        return SelfLearner

    def test_can_award_no_post(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        self.failIf(badge.can_award(user))

    def test_can_award_w_post_no_topic(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user)
        self.failIf(badge.can_award(user, post=post))

    def test_can_award_w_post_not_is_answer(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user)
        topic = self._makeTopic(user)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_not_question_author(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True)
        author = self._makeUser()
        topic = self._makeTopic(author)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_no_post_upvotes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True)
        topic = self._makeTopic(user)
        self.failIf(badge.can_award(user, post=post, topic=topic))

    def test_can_award_w_post_is_answer_w_post_upvotes(self):
        badge = self._makeOne()
        badge.identifier = 'testing'
        user = self._makeUser()
        post = self._makePost(user, is_answer=True, votes=4)
        topic = self._makeTopic(user)
        self.failUnless(badge.can_award(user, post=post, topic=topic))


class Test_award_badges(_Base):

    def _callFUT(self, event, user, **kw):
        from ..badges import award_badges
        award_badges(event, user, **kw)

    def test_new_topic(self):
        user = self._makeUser()
        topic = self._makeTopic(user)
        self._callFUT('new_topic', user, topic=topic)
        self.assertEqual(user.badges, {'inquirer': [None]})
