"""Test cases for Relationapp's MetaWeblog API"""
from xmlrpclib import Binary
from xmlrpclib import Fault
from xmlrpclib import ServerProxy
from datetime import datetime
from tempfile import TemporaryFile

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.storage import default_storage

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.managers import DRAFT
from relationapp.managers import PUBLISHED
from relationapp.settings import UPLOAD_TO
from relationapp.xmlrpc.metaweblog import authenticate
from relationapp.xmlrpc.metaweblog import post_structure
from relationapp.tests.utils import TestTransport


class MetaWeblogTestCase(TestCase):
    """Test cases for MetaWeblog"""
    urls = 'relationapp.tests.urls'

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
        self.relations = [
            Relation.objects.create(title='Relation 1',
                                    slug='relation-1'),
            Relation.objects.create(title='Relation 2',
                                    slug='relation-2')]
        params = {'title': 'My relationtype 1', 'content': 'My content 1',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-1',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.relationtype_1 = Relationtype.objects.create(**params)
        self.relationtype_1.authors.add(self.webmaster)
        self.relationtype_1.relations.add(*self.relations)
        self.relationtype_1.sites.add(self.site)

        params = {'title': 'My relationtype 2', 'content': 'My content 2',
                  'creation_date': datetime(2010, 3, 15),
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-2'}
        self.relationtype_2 = Relationtype.objects.create(**params)
        self.relationtype_2.authors.add(self.webmaster)
        self.relationtype_2.relations.add(self.relations[0])
        self.relationtype_2.sites.add(self.site)
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
                          'password', 'relationapp.change_relationtype')
        self.assertEquals(authenticate('webmaster', 'password'),
                          self.webmaster)
        self.assertEquals(authenticate('webmaster', 'password',
                                       'relationapp.change_relationtype'),
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

    def test_get_relations(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRelations,
                          1, 'contributor', 'password')
        self.assertEquals(
            self.server.metaWeblog.getRelations('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/relations/relation-1/',
              'description': 'Relation 1',
              'htmlUrl': 'http://example.com/relations/relation-1/',
              'relationId': 1, 'parentId': 0,
              'relationName': 'Relation 1',
              'relationDescription': ''},
             {'rssUrl': 'http://example.com/feeds/relations/relation-2/',
              'description': 'Relation 2',
              'htmlUrl': 'http://example.com/relations/relation-2/',
              'relationId': 2, 'parentId': 0,
              'relationName': 'Relation 2',
              'relationDescription': ''}])
        self.relations[1].parent = self.relations[0]
        self.relations[1].description = 'relation 2 description'
        self.relations[1].save()
        self.assertEquals(
            self.server.metaWeblog.getRelations('apikey',
                                                 'webmaster', 'password'),
            [{'rssUrl': 'http://example.com/feeds/relations/relation-1/',
              'description': 'Relation 1',
              'htmlUrl': 'http://example.com/relations/relation-1/',
              'relationId': 1, 'parentId': 0,
              'relationName': 'Relation 1',
              'relationDescription': ''},
             {'rssUrl':
              'http://example.com/feeds/relations/relation-1/relation-2/',
              'description': 'Relation 2',
              'htmlUrl':
              'http://example.com/relations/relation-1/relation-2/',
              'relationId': 2, 'parentId': 1,
              'relationName': 'Relation 2',
              'relationDescription': 'relation 2 description'}])

    def test_new_relation(self):
        relation_struct = {'name': 'Relation 3', 'slug': 'relation-3',
                           'description': 'Relation 3 description',
                           'parent_id': self.relations[0].pk}
        self.assertRaises(Fault, self.server.wp.newRelation,
                          1, 'contributor', 'password', relation_struct)
        self.assertEquals(Relation.objects.count(), 2)
        new_relation_id = self.server.wp.newRelation(
            1, 'webmaster', 'password', relation_struct)
        self.assertEquals(Relation.objects.count(), 3)
        relation = Relation.objects.get(pk=new_relation_id)
        self.assertEquals(relation.title, 'Relation 3')
        self.assertEquals(relation.description, 'Relation 3 description')
        self.assertEquals(relation.slug, 'relation-3')
        self.assertEquals(relation.parent.pk, 1)

    def test_get_recent_posts(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRecentPosts,
                          1, 'contributor', 'password', 10)
        self.assertEquals(len(self.server.metaWeblog.getRecentPosts(
            1, 'webmaster', 'password', 10)), 2)

    def test_delete_post(self):
        self.assertRaises(Fault, self.server.blogger.deletePost,
                          'apikey', 1, 'contributor', 'password', 'publish')
        self.assertEquals(Relationtype.objects.count(), 2)
        self.assertTrue(
            self.server.blogger.deletePost(
            'apikey', self.relationtype_1.pk, 'webmaster', 'password', 'publish'))
        self.assertEquals(Relationtype.objects.count(), 1)

    def test_get_post(self):
        self.assertRaises(Fault, self.server.metaWeblog.getPost,
                          1, 'contributor', 'password')
        post = self.server.metaWeblog.getPost(
            self.relationtype_1.pk, 'webmaster', 'password')
        self.assertEquals(post['title'], self.relationtype_1.title)
        self.assertEquals(post['description'], '<p>My content 1</p>')
        self.assertEquals(post['relations'], ['Relation 1', 'Relation 2'])
        self.assertEquals(post['dateCreated'].value, '2010-01-01T00:00:00')
        self.assertEquals(post['link'],
                          'http://example.com/2010/01/01/my-relationtype-1/')
        self.assertEquals(post['permaLink'],
                          'http://example.com/2010/01/01/my-relationtype-1/')
        self.assertEquals(post['postid'], self.relationtype_1.pk)
        self.assertEquals(post['userid'], 'webmaster')
        self.assertEquals(post['mt_excerpt'], '')
        self.assertEquals(post['mt_allow_comments'], 1)
        self.assertEquals(post['mt_allow_pings'], 1)
        self.assertEquals(post['mt_keywords'], self.relationtype_1.tags)
        self.assertEquals(post['wp_author'], 'webmaster')
        self.assertEquals(post['wp_author_id'], self.webmaster.pk)
        self.assertEquals(post['wp_author_display_name'], 'webmaster')
        self.assertEquals(post['wp_password'], '')
        self.assertEquals(post['wp_slug'], self.relationtype_1.slug)

    def test_new_post(self):
        post = post_structure(self.relationtype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.newPost,
                          1, 'contributor', 'password', post, 1)
        self.assertEquals(Relationtype.objects.count(), 2)
        self.assertEquals(Relationtype.published.count(), 1)
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 1)
        self.assertEquals(Relationtype.objects.count(), 3)
        self.assertEquals(Relationtype.published.count(), 2)
        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk
        self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)
        self.assertEquals(Relationtype.objects.count(), 4)
        self.assertEquals(Relationtype.published.count(), 2)

    def test_edit_post(self):
        post = post_structure(self.relationtype_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.editPost,
                          1, 'contributor', 'password', post, 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)

        relationtype = Relationtype.objects.get(pk=new_post_id)
        self.assertEquals(relationtype.title, self.relationtype_2.title)
        self.assertEquals(relationtype.content, self.relationtype_2.html_content)
        self.assertEquals(relationtype.excerpt, self.relationtype_2.excerpt)
        self.assertEquals(relationtype.slug, self.relationtype_2.slug)
        self.assertEquals(relationtype.status, DRAFT)
        self.assertEquals(relationtype.password, self.relationtype_2.password)
        self.assertEquals(relationtype.comment_enabled, True)
        self.assertEquals(relationtype.pingback_enabled, True)
        self.assertEquals(relationtype.relations.count(), 1)
        self.assertEquals(relationtype.authors.count(), 1)
        self.assertEquals(relationtype.authors.all()[0], self.webmaster)
        self.assertEquals(relationtype.creation_date, self.relationtype_2.creation_date)

        relationtype.title = 'Title edited'
        relationtype.creation_date = datetime(2000, 1, 1)
        post = post_structure(relationtype, self.site)
        post['relations'] = ''
        post['description'] = 'Content edited'
        post['mt_excerpt'] = 'Content edited'
        post['wp_slug'] = 'slug-edited'
        post['wp_password'] = 'password'
        post['mt_allow_comments'] = 2
        post['mt_allow_pings'] = 0

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        self.assertEquals(response, True)
        relationtype = Relationtype.objects.get(pk=new_post_id)
        self.assertEquals(relationtype.title, post['title'])
        self.assertEquals(relationtype.content, post['description'])
        self.assertEquals(relationtype.excerpt, post['mt_excerpt'])
        self.assertEquals(relationtype.slug, 'slug-edited')
        self.assertEquals(relationtype.status, PUBLISHED)
        self.assertEquals(relationtype.password, 'password')
        self.assertEquals(relationtype.comment_enabled, False)
        self.assertEquals(relationtype.pingback_enabled, False)
        self.assertEquals(relationtype.relations.count(), 0)
        self.assertEquals(relationtype.creation_date, datetime(2000, 1, 1))

        del post['dateCreated']
        post['wp_author_id'] = self.contributor.pk

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        relationtype = Relationtype.objects.get(pk=new_post_id)
        self.assertEquals(relationtype.authors.count(), 1)
        self.assertEquals(relationtype.authors.all()[0], self.contributor)
        self.assertEquals(relationtype.creation_date, datetime(2000, 1, 1))

    def test_new_media_object(self):
        file_ = TemporaryFile()
        file_.write('My test content')
        file_.seek(0)
        media = {'name': 'relationapp_test_file.txt',
                 'type': 'text/plain',
                 'bits': Binary(file_.read())}
        file_.close()

        self.assertRaises(Fault, self.server.metaWeblog.newMediaObject,
                          1, 'contributor', 'password', media)
        new_media = self.server.metaWeblog.newMediaObject(
            1, 'webmaster', 'password', media)
        self.assertTrue('/relationapp_test_file' in new_media['url'])
        default_storage.delete('/'.join([
            UPLOAD_TO, new_media['url'].split('/')[-1]]))
