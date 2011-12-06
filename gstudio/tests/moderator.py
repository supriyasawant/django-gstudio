"""Test cases for Gstudio's moderator"""
from django.core import mail
from django.test import TestCase
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from gstudio.models import Nodetype
from gstudio.managers import PUBLISHED
from gstudio.moderator import NodetypeCommentModerator


class NodetypeCommentModeratorTestCase(TestCase):
    """Test cases for the moderator"""

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.nodetype_ct_id = ContentType.objects.get_for_model(Nodetype).pk

        params = {'title': 'My test nodetype',
                  'content': 'My test nodetype',
                  'slug': 'my-test-nodetype',
                  'status': PUBLISHED}
        self.nodetype = Nodetype.objects.create(**params)
        self.nodetype.sites.add(self.site)
        self.nodetype.authors.add(self.author)

    def test_email(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        self.assertEquals(len(mail.outbox), 0)
        moderator = NodetypeCommentModerator(Nodetype)
        moderator.email_reply = False
        moderator.email_authors = False
        moderator.mail_comment_notification_recipients = []
        moderator.email(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 0)
        moderator.email_reply = True
        moderator.email_authors = True
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.email(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 1)

    def test_do_email_notification(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        self.assertEquals(len(mail.outbox), 0)
        moderator = NodetypeCommentModerator(Nodetype)
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.do_email_notification(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 1)

    def test_do_email_authors(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        self.assertEquals(len(mail.outbox), 0)
        moderator = NodetypeCommentModerator(Nodetype)
        moderator.email_authors = True
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.do_email_authors(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 0)
        moderator.mail_comment_notification_recipients = []
        moderator.do_email_authors(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 1)

    def test_do_email_reply(self):
        comment = comments.get_model().objects.create(
            comment='My Comment 1', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        moderator = NodetypeCommentModerator(Nodetype)
        moderator.email_notification_reply = True
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.do_email_reply(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 0)

        comment = comments.get_model().objects.create(
            comment='My Comment 2', user_email='user_1@example.com',
            content_object=self.nodetype, is_public=True, site=self.site)
        moderator.do_email_reply(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 0)

        comment = comments.get_model().objects.create(
            comment='My Comment 3', user_email='user_2@example.com',
            content_object=self.nodetype, is_public=True, site=self.site)
        moderator.do_email_reply(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].bcc, [u'user_1@example.com'])

        comment = comments.get_model().objects.create(
            comment='My Comment 4', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        moderator.do_email_reply(comment, self.nodetype, 'request')
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].bcc, [u'user_1@example.com',
                                               u'user_2@example.com'])

    def test_moderate(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.nodetype, site=self.site)
        moderator = NodetypeCommentModerator(Nodetype)
        moderator.auto_moderate_comments = True
        moderator.spam_checker_backends = ()
        self.assertEquals(moderator.moderate(comment, self.nodetype, 'request'),
                          True)
        moderator.auto_moderate_comments = False
        self.assertEquals(moderator.moderate(comment, self.nodetype, 'request'),
                          False)
        self.assertEquals(comments.get_model().objects.filter(
            flags__flag='spam').count(), 0)
        moderator.spam_checker_backends = (
            'gstudio.spam_checker.backends.all_is_spam',)
        self.assertEquals(moderator.moderate(comment, self.nodetype, 'request'),
                          True)
        self.assertEquals(comments.get_model().objects.filter(
            flags__flag='spam').count(), 1)
