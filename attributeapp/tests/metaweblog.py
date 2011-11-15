"""Test cases for Attributeapp's MetaWeblog API"""
from xmlrpclib import Binary
from xmlrpclib import Fault
from xmlrpclib import ServerProxy
from datetime import datetime
from tempfile import TemporaryFile

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.managers import DRAFT
from attributeapp.managers import PUBLISHED
from attributeapp.settings import UPLOAD_TO
from attributeapp.xmlrpc.metaweblog import authenticate
from attributeapp.xmlrpc.metaweblog import post_structure
from attributeapp.tests.utils import TestTransport


class MetaWeblogTestCase(TestCase):
    """Test cases for MetaWeblog"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        # Create data
        self.webmaster = User.objects.create_superuser(
            username='webmaster',
            email='webmaster@example.com',
            password='password')
        self.contributor = User.objects.create_user(
            username='contributor',
            email='contributor@example.com',
            password='password')
        self.site = Site.objects.get_current()
        self.attributes = [
            Attribute.objects.create(title='Attribute 1',
                                    slug='attribute-1'),
            Attribute.objects.create(title='Attribute 2',
                                    slug='attribute-2')]
        params = {'title': 'My attributetype 1', 'content': 'My content 1',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-1',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.attributetype_1 = Attributetype.objects.create(**params)
        self.attributetype_1.authors.add(self.webmaster)
        self.attributetype_1.attributes.add(*self.attributes)
        self.attributetype_1.sites.add(self.site)

        params = {'title': 'My attributetype 2', 'content': 'My content 2',
                  'creation_date': datetime(2010, 3, 15),
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-2'}
        self.attributetype_2 = Attributetype.objects.create(**params)
        self.attributetype_2.authors.add(self.webmaster)
        self.attributetype_2.attributes.add(self.attributes[0])
        self.attributetype_2.sites.add(self.site)
        # Instanciating the server proxy
        self.server = ServerProxy('http://localhost:8000/xmlrpc/',
                                  transport=TestTransport())

    def test_authenticate(self):
        self.assertRaises(Fault, authenticate, 'badcontributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'password')
        self.contributor.is_staff = True
        self.contributor.save()
        self.assertEquals(authenticate('contributor', 'password'),
                          self.contributor)
        self.assertRaises(Fault, authenticate, 'contributor',
                          'password', 'attributeapp.change_attributetype')
        self.assertEquals(authenticate('webmaster', 'password'),
                          self.webmaster)
        self.assertEquals(authenticate('webmaster', 'password',
                                       'attributeapp.change_attributetype'),
                          self.webmaster)

    def test_get_users_blogs(self):
        self.assertRaises(Fault, self.server.blogger.getUsersBlogs,
                          'apikey', 'contributor', 'password')
        self.assertEquals(self.server.blogger.getUsersBlogs(
            'apikey', 'webmaster', 'password'),
                          [{'url': 'http://example.com/',
                            'blogid': 1,
                            'blogName': 'example.com'}])

    def test_get_user_info(self):
        self.assertRaises(Fault, self.server.blogger.getUserInfo,
                          'apikey', 'contributor', 'password')
        self.webmaster.first_name = 'John'
        self.webmaster.last_name = 'Doe'
        self.webmaster.save()
        self.assertEquals(self.server.blogger.getUserInfo(
            'apikey', 'webmaster', 'password'),
                          {'firstname': 'John', 'lastname': 'Doe',
                           'url': 'http://example.com/authors/webmaster/',
                           'userid': self.webmaster.pk,
                           'nickname': 'webmaster',
                           'email': 'webmaster@example.com'})

    def test_get_authors(self):
        self.assertRaises(Fault, self.server.wp.getAuthors,
                          'apikey', 'contributor', 'password')
        self.assertEquals(self.server.wp.getAuthors(
            'apikey', 'webmaster', 'password'), [
                              {'user_login': 'webmaster',
                               'user_id': self.webmaster.pk,
                               'user_email': 'webmaster@example.com',
                               'display_name': 'webmaster'}])

    def test_get_attributes(self):
        self.assertRaises(Fault, self.server.metaWeblog.getAttributes,
                          1, 'contributor', 'password')
        self.assertEquals(
            self.server.metaWeblog.getAttributes('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/attributes/attribute-1/',
              'description': 'Attribute 1',
              'htmlUrl': 'http://example.com/attributes/attribute-1/',
              'attributeId': 1, 'parentId': 0,
              'attributeName': 'Attribute 1',
              'attributeDescription': ''},
             {'rssUrl': 'http://example.com/feeds/attributes/attribute-2/',
              'description': 'Attribute 2',
              'htmlUrl': 'http://example.com/attributes/attribute-2/',
              'attributeId': 2, 'parentId': 0,
              'attributeName': 'Attribute 2',
              'attributeDescription': ''}])
        self.attributes[1].parent = self.attributes[0]
        self.attributes[1].description = 'attribute 2 description'
        self.attributes[1].save()
        self.assertEquals(
            self.server.metaWeblog.getAttributes('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/attributes/attribute-1/',
              'description': 'Attribute 1',
              'htmlUrl': 'http://example.com/attributes/attribute-1/',
              'attributeId': 1, 'parentId': 0,
              'attributeName': 'Attribute 1',
              'attributeDescription': ''},
             {'rssUrl':
              'http://example.com/feeds/attributes/attribute-1/attribute-2/',
              'description': 'Attribute 2',
              'htmlUrl':
              'http://example.com/attributes/attribute-1/attribute-2/',
              'attributeId': 2, 'parentId': 1,
              'attributeName': 'Attribute 2',
              'attributeDescription': 'attribute 2 description'}])

    def test_new_attribute(self):
        attribute_struct = {'name': 'Attribute 3', 'slug': 'attribute-3',
                           'description': 'Attribute 3 description',
                           'parent_id': self.attributes[0].pk}
        self.assertRaises(Fault, self.server.wp.newAttribute,
                          1, 'contributor', 'password', attribute_struct)
        self.assertEquals(Attribute.objects.count(), 2)
        new_attribute_id = self.server.wp.newAttribute(
            1, 'webmaster', 'password', attribute_struct)
        self.assertEquals(Attribute.objects.count(), 3)
        attribute = Attribute.objects.get(pk=new_attribute_id)
        self.assertEquals(attribute.title, 'Attribute 3')
        self.assertEquals(attribute.description, 'Attribute 3 description')
        self.assertEquals(attribute.slug, 'attribute-3')
        self.assertEquals(attribute.parent.pk, 1)

    def test_get_recent_posts(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRecentPosts,
                          1, 'contributor', 'password', 10)
        self.assertEquals(len(self.server.metaWeblog.getRecentPosts(
            1, 'webmaster', 'password', 10)), 2)

    def test_delete_post(self):
        self.assertRaises(Fault, self.server.blogger.deletePost,
                          'apikey', 1, 'contributor', 'password', 'publish')
        self.assertEquals(Attributetype.objects.count(), 2)
        self.assertTrue(
            self.server.blogger.deletePost(
            'apikey', self.attributetype_1.pk, 'webmaster', 'password', 'publish'))
        self.assertEquals(Attributetype.objects.count(), 1)

    def test_get_post(self):
        self.assertRaises(Fault, self.server.metaWeblog.getPost,
                          1, 'contributor', 'password')
        post = self.server.metaWeblog.getPost(
            self.attributetype_1.pk, 'webmaster', 'password')
        self.assertEquals(post['title'], self.attributetype_1.title)
        self.assertEquals(post['description'], '<p>My content 1</p>')
        self.assertEquals(post['attributes'], ['Attribute 1', 'Attribute 2'])
        self.assertEquals(post['dateCreated'].value, '2010-01-01T00:00:00')
        self.assertEquals(post['link'],
                          'http://example.com/2010/01/01/my-attributetype-1/')
        self.assertEquals(post['permaLink'],
                          'http://example.com/2010/01/01/my-attributetype-1/')
        self.assertEquals(post['postid'], self.attributetype_1.pk)
        self.assertEquals(post['userid'], 'webmaster')
        self.assertEquals(post['mt_excerpt'], '')
        self.assertEquals(post['mt_allow_comments'], 1)
        self.assertEquals(post['mt_allow_pings'], 1)
        self.assertEquals(post['mt_keywords'], self.attributetype_1.tags)
        self.assertEquals(post['wp_author'], 'webmaster')
        self.assertEquals(post['wp_author_id'], self.webmaster.pk)
        self.assertEquals(post['wp_author_display_name'], 'webmaster')
        self.assertEquals(post['wp_password'], '')
        self.assertEquals(post['wp_slug'], self.attributetype_1.slug)

    def test_new_post(self):
        post = post_structure(self.attributetype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.newPost,
                          1, 'contributor', 'password', post, 1)
        self.assertEquals(Attributetype.objects.count(), 2)
        self.assertEquals(Attributetype.published.count(), 1)
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 1)
        self.assertEquals(Attributetype.objects.count(), 3)
        self.assertEquals(Attributetype.published.count(), 2)
        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)
        self.assertEquals(Attributetype.objects.count(), 4)
        self.assertEquals(Attributetype.published.count(), 2)

    def test_edit_post(self):
        post = post_structure(self.attributetype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.editPost,
                          1, 'contributor', 'password', post, 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)

        attributetype = Attributetype.objects.get(pk=new_post_id)
        self.assertEquals(attributetype.title, self.attributetype_2.title)
        self.assertEquals(attributetype.content, self.attributetype_2.html_content)
        self.assertEquals(attributetype.excerpt, self.attributetype_2.excerpt)
        self.assertEquals(attributetype.slug, self.attributetype_2.slug)
        self.assertEquals(attributetype.status, DRAFT)
        self.assertEquals(attributetype.password, self.attributetype_2.password)
        self.assertEquals(attributetype.comment_enabled, True)
        self.assertEquals(attributetype.pingback_enabled, True)
        self.assertEquals(attributetype.attributes.count(), 1)
        self.assertEquals(attributetype.authors.count(), 1)
        self.assertEquals(attributetype.authors.all()[0], self.webmaster)
        self.assertEquals(attributetype.creation_date, self.attributetype_2.creation_date)

        attributetype.title = 'Title edited'
        attributetype.creation_date = datetime(2000, 1, 1)
        post = post_structure(attributetype, self.site)
        post['attributes'] = ''
        post['description'] = 'Content edited'
        post['mt_excerpt'] = 'Content edited'
        post['wp_slug'] = 'slug-edited'
        post['wp_password'] = 'password'
        post['mt_allow_comments'] = 2
        post['mt_allow_pings'] = 0

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        self.assertEquals(response, True)
        attributetype = Attributetype.objects.get(pk=new_post_id)
        self.assertEquals(attributetype.title, post['title'])
        self.assertEquals(attributetype.content, post['description'])
        self.assertEquals(attributetype.excerpt, post['mt_excerpt'])
        self.assertEquals(attributetype.slug, 'slug-edited')
        self.assertEquals(attributetype.status, PUBLISHED)
        self.assertEquals(attributetype.password, 'password')
        self.assertEquals(attributetype.comment_enabled, False)
        self.assertEquals(attributetype.pingback_enabled, False)
        self.assertEquals(attributetype.attributes.count(), 0)
        self.assertEquals(attributetype.creation_date, datetime(2000, 1, 1))

        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        attributetype = Attributetype.objects.get(pk=new_post_id)
        self.assertEquals(attributetype.authors.count(), 1)
        self.assertEquals(attributetype.authors.all()[0], self.contributor)
        self.assertEquals(attributetype.creation_date, datetime(2000, 1, 1))

    def test_new_media_object(self):
        file_ = TemporaryFile()
        file_.write('My test content')
        file_.seek(0)
        media = {'name': 'attributeapp_test_file.txt',
                 'type': 'text/plain',
                 'bits': Binary(file_.read())}
        file_.close()

        self.assertRaises(Fault, self.server.metaWeblog.newMediaObject,
                          1, 'contributor', 'password', media)
        new_media = self.server.metaWeblog.newMediaObject(
            1, 'webmaster', 'password', media)
        self.assertTrue('/attributeapp_test_file' in new_media['url'])
        default_storage.delete('/'.join([
            UPLOAD_TO, new_media['url'].split('/')[-1]]))
