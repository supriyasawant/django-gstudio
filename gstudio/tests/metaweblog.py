"""Test cases for Gstudio's MetaWeblog API"""
from xmlrpclib import Binary
from xmlrpclib import Fault
from xmlrpclib import ServerProxy
from datetime import datetime
from tempfile import TemporaryFile

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.managers import DRAFT
from gstudio.managers import PUBLISHED
from gstudio.settings import UPLOAD_TO
from gstudio.xmlrpc.metaweblog import authenticate
from gstudio.xmlrpc.metaweblog import post_structure
from gstudio.tests.utils import TestTransport


class MetaWeblogTestCase(TestCase):
    """Test cases for MetaWeblog"""
    urls = 'gstudio.tests.urls'

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
        self.metatypes = [
            Metatype.objects.create(title='Metatype 1',
                                    slug='metatype-1'),
            Metatype.objects.create(title='Metatype 2',
                                    slug='metatype-2')]
        params = {'title': 'My objecttype 1', 'content': 'My content 1',
                  'tags': 'gstudio, test', 'slug': 'my-objecttype-1',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.objecttype_1 = Objecttype.objects.create(**params)
        self.objecttype_1.authors.add(self.webmaster)
        self.objecttype_1.metatypes.add(*self.metatypes)
        self.objecttype_1.sites.add(self.site)

        params = {'title': 'My objecttype 2', 'content': 'My content 2',
                  'creation_date': datetime(2010, 3, 15),
                  'tags': 'gstudio, test', 'slug': 'my-objecttype-2'}
        self.objecttype_2 = Objecttype.objects.create(**params)
        self.objecttype_2.authors.add(self.webmaster)
        self.objecttype_2.metatypes.add(self.metatypes[0])
        self.objecttype_2.sites.add(self.site)
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
                          'password', 'gstudio.change_objecttype')
        self.assertEquals(authenticate('webmaster', 'password'),
                          self.webmaster)
        self.assertEquals(authenticate('webmaster', 'password',
                                       'gstudio.change_objecttype'),
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

    def test_get_metatypes(self):
        self.assertRaises(Fault, self.server.metaWeblog.getMetatypes,
                          1, 'contributor', 'password')
        self.assertEquals(
            self.server.metaWeblog.getMetatypes('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/metatypes/metatype-1/',
              'description': 'Metatype 1',
              'htmlUrl': 'http://example.com/metatypes/metatype-1/',
              'metatypeId': 1, 'parentId': 0,
              'metatypeName': 'Metatype 1',
              'metatypeDescription': ''},
             {'rssUrl': 'http://example.com/feeds/metatypes/metatype-2/',
              'description': 'Metatype 2',
              'htmlUrl': 'http://example.com/metatypes/metatype-2/',
              'metatypeId': 2, 'parentId': 0,
              'metatypeName': 'Metatype 2',
              'metatypeDescription': ''}])
        self.metatypes[1].parent = self.metatypes[0]
        self.metatypes[1].description = 'metatype 2 description'
        self.metatypes[1].save()
        self.assertEquals(
            self.server.metaWeblog.getMetatypes('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/metatypes/metatype-1/',
              'description': 'Metatype 1',
              'htmlUrl': 'http://example.com/metatypes/metatype-1/',
              'metatypeId': 1, 'parentId': 0,
              'metatypeName': 'Metatype 1',
              'metatypeDescription': ''},
             {'rssUrl':
              'http://example.com/feeds/metatypes/metatype-1/metatype-2/',
              'description': 'Metatype 2',
              'htmlUrl':
              'http://example.com/metatypes/metatype-1/metatype-2/',
              'metatypeId': 2, 'parentId': 1,
              'metatypeName': 'Metatype 2',
              'metatypeDescription': 'metatype 2 description'}])

    def test_new_metatype(self):
        metatype_struct = {'name': 'Metatype 3', 'slug': 'metatype-3',
                           'description': 'Metatype 3 description',
                           'parent_id': self.metatypes[0].pk}
        self.assertRaises(Fault, self.server.wp.newMetatype,
                          1, 'contributor', 'password', metatype_struct)
        self.assertEquals(Metatype.objects.count(), 2)
        new_metatype_id = self.server.wp.newMetatype(
            1, 'webmaster', 'password', metatype_struct)
        self.assertEquals(Metatype.objects.count(), 3)
        metatype = Metatype.objects.get(pk=new_metatype_id)
        self.assertEquals(metatype.title, 'Metatype 3')
        self.assertEquals(metatype.description, 'Metatype 3 description')
        self.assertEquals(metatype.slug, 'metatype-3')
        self.assertEquals(metatype.parent.pk, 1)

    def test_get_recent_posts(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRecentPosts,
                          1, 'contributor', 'password', 10)
        self.assertEquals(len(self.server.metaWeblog.getRecentPosts(
            1, 'webmaster', 'password', 10)), 2)

    def test_delete_post(self):
        self.assertRaises(Fault, self.server.blogger.deletePost,
                          'apikey', 1, 'contributor', 'password', 'publish')
        self.assertEquals(Objecttype.objects.count(), 2)
        self.assertTrue(
            self.server.blogger.deletePost(
            'apikey', self.objecttype_1.pk, 'webmaster', 'password', 'publish'))
        self.assertEquals(Objecttype.objects.count(), 1)

    def test_get_post(self):
        self.assertRaises(Fault, self.server.metaWeblog.getPost,
                          1, 'contributor', 'password')
        post = self.server.metaWeblog.getPost(
            self.objecttype_1.pk, 'webmaster', 'password')
        self.assertEquals(post['title'], self.objecttype_1.title)
        self.assertEquals(post['description'], '<p>My content 1</p>')
        self.assertEquals(post['metatypes'], ['Metatype 1', 'Metatype 2'])
        self.assertEquals(post['dateCreated'].value, '2010-01-01T00:00:00')
        self.assertEquals(post['link'],
                          'http://example.com/2010/01/01/my-objecttype-1/')
        self.assertEquals(post['permaLink'],
                          'http://example.com/2010/01/01/my-objecttype-1/')
        self.assertEquals(post['postid'], self.objecttype_1.pk)
        self.assertEquals(post['userid'], 'webmaster')
        self.assertEquals(post['mt_excerpt'], '')
        self.assertEquals(post['mt_allow_comments'], 1)
        self.assertEquals(post['mt_allow_pings'], 1)
        self.assertEquals(post['mt_keywords'], self.objecttype_1.tags)
        self.assertEquals(post['wp_author'], 'webmaster')
        self.assertEquals(post['wp_author_id'], self.webmaster.pk)
        self.assertEquals(post['wp_author_display_name'], 'webmaster')
        self.assertEquals(post['wp_password'], '')
        self.assertEquals(post['wp_slug'], self.objecttype_1.slug)

    def test_new_post(self):
        post = post_structure(self.objecttype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.newPost,
                          1, 'contributor', 'password', post, 1)
        self.assertEquals(Objecttype.objects.count(), 2)
        self.assertEquals(Objecttype.published.count(), 1)
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 1)
        self.assertEquals(Objecttype.objects.count(), 3)
        self.assertEquals(Objecttype.published.count(), 2)
        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)
        self.assertEquals(Objecttype.objects.count(), 4)
        self.assertEquals(Objecttype.published.count(), 2)

    def test_edit_post(self):
        post = post_structure(self.objecttype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.editPost,
                          1, 'contributor', 'password', post, 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)

        objecttype = Objecttype.objects.get(pk=new_post_id)
        self.assertEquals(objecttype.title, self.objecttype_2.title)
        self.assertEquals(objecttype.content, self.objecttype_2.html_content)
        self.assertEquals(objecttype.excerpt, self.objecttype_2.excerpt)
        self.assertEquals(objecttype.slug, self.objecttype_2.slug)
        self.assertEquals(objecttype.status, DRAFT)
        self.assertEquals(objecttype.password, self.objecttype_2.password)
        self.assertEquals(objecttype.comment_enabled, True)
        self.assertEquals(objecttype.pingback_enabled, True)
        self.assertEquals(objecttype.metatypes.count(), 1)
        self.assertEquals(objecttype.authors.count(), 1)
        self.assertEquals(objecttype.authors.all()[0], self.webmaster)
        self.assertEquals(objecttype.creation_date, self.objecttype_2.creation_date)

        objecttype.title = 'Title edited'
        objecttype.creation_date = datetime(2000, 1, 1)
        post = post_structure(objecttype, self.site)
        post['metatypes'] = ''
        post['description'] = 'Content edited'
        post['mt_excerpt'] = 'Content edited'
        post['wp_slug'] = 'slug-edited'
        post['wp_password'] = 'password'
        post['mt_allow_comments'] = 2
        post['mt_allow_pings'] = 0

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        self.assertEquals(response, True)
        objecttype = Objecttype.objects.get(pk=new_post_id)
        self.assertEquals(objecttype.title, post['title'])
        self.assertEquals(objecttype.content, post['description'])
        self.assertEquals(objecttype.excerpt, post['mt_excerpt'])
        self.assertEquals(objecttype.slug, 'slug-edited')
        self.assertEquals(objecttype.status, PUBLISHED)
        self.assertEquals(objecttype.password, 'password')
        self.assertEquals(objecttype.comment_enabled, False)
        self.assertEquals(objecttype.pingback_enabled, False)
        self.assertEquals(objecttype.metatypes.count(), 0)
        self.assertEquals(objecttype.creation_date, datetime(2000, 1, 1))

        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        objecttype = Objecttype.objects.get(pk=new_post_id)
        self.assertEquals(objecttype.authors.count(), 1)
        self.assertEquals(objecttype.authors.all()[0], self.contributor)
        self.assertEquals(objecttype.creation_date, datetime(2000, 1, 1))

    def test_new_media_object(self):
        file_ = TemporaryFile()
        file_.write('My test content')
        file_.seek(0)
        media = {'name': 'gstudio_test_file.txt',
                 'type': 'text/plain',
                 'bits': Binary(file_.read())}
        file_.close()

        self.assertRaises(Fault, self.server.metaWeblog.newMediaObject,
                          1, 'contributor', 'password', media)
        new_media = self.server.metaWeblog.newMediaObject(
            1, 'webmaster', 'password', media)
        self.assertTrue('/gstudio_test_file' in new_media['url'])
        default_storage.delete('/'.join([
            UPLOAD_TO, new_media['url'].split('/')[-1]]))
