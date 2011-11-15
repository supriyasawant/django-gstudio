"""XML-RPC methods of Relationapp metaWeblog API"""
import os
from datetime import datetime
from xmlrpclib import Fault
from xmlrpclib import DateTime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.settings import PROTOCOL
from relationapp.settings import UPLOAD_TO
from relationapp.managers import DRAFT, PUBLISHED
from django_xmlrpc.decorators import xmlrpc_func

# http://docs.nucleuscms.org/blog/12#errorcodes
LOGIN_ERROR = 801
PERMISSION_DENIED = 803


def authenticate(username, password, permission=None):
    """Authenticate staff_user with permission"""
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        raise Fault(LOGIN_ERROR, _('Username is incorrect.'))
    if not user.check_password(password):
        raise Fault(LOGIN_ERROR, _('Password is invalid.'))
    if not user.is_staff or not user.is_active:
        raise Fault(PERMISSION_DENIED, _('User account unavailable.'))
    if permission:
        if not user.has_perm(permission):
            raise Fault(PERMISSION_DENIED, _('User cannot %s.') % permission)
    return user


def blog_structure(site):
    """A blog structure"""
    return {'url': '%s://%s%s' % (
        PROTOCOL, site.domain, reverse('relationapp_relationtype_archive_index')),
            'blogid': settings.SITE_ID,
            'blogName': site.name}


def user_structure(user, site):
    """An user structure"""
    return {'userid': user.pk,
            'email': user.email,
            'nickname': user.username,
            'lastname': user.last_name,
            'firstname': user.first_name,
            'url': '%s://%s%s' % (
                PROTOCOL, site.domain,
                reverse('relationapp_author_detail', args=[user.username]))}


def author_structure(user):
    """An author structure"""
    return {'user_id': user.pk,
            'user_login': user.username,
            'display_name': user.username,
            'user_email': user.email}


def relation_structure(relation, site):
    """A relation structure"""
    return {'description': relation.title,
            'htmlUrl': '%s://%s%s' % (
                PROTOCOL, site.domain,
                relation.get_absolute_url()),
            'rssUrl': '%s://%s%s' % (
                PROTOCOL, site.domain,
                reverse('relationapp_relation_feed', args=[relation.tree_path])),
            # Useful Wordpress Extensions
            'relationId': relation.pk,
            'parentId': relation.parent and relation.parent.pk or 0,
            'relationDescription': relation.description,
            'relationName': relation.title}


def post_structure(relationtype, site):
    """A post structure with extensions"""
    author = relationtype.authors.all()[0]
    return {'title': relationtype.title,
            'description': unicode(relationtype.html_content),
            'link': '%s://%s%s' % (PROTOCOL, site.domain,
                                   relationtype.get_absolute_url()),
            # Basic Extensions
            'permaLink': '%s://%s%s' % (PROTOCOL, site.domain,
                                        relationtype.get_absolute_url()),
            'relations': [cat.title for cat in relationtype.relations.all()],
            'dateCreated': DateTime(relationtype.creation_date.isoformat()),
            'postid': relationtype.pk,
            'userid': author.username,
            # Useful Movable Type Extensions
            'mt_excerpt': relationtype.excerpt,
            'mt_allow_comments': int(relationtype.comment_enabled),
            'mt_allow_pings': int(relationtype.pingback_enabled),
            'mt_keywords': relationtype.tags,
            # Useful Wordpress Extensions
            'wp_author': author.username,
            'wp_author_id': author.pk,
            'wp_author_display_name': author.username,
            'wp_password': relationtype.password,
            'wp_slug': relationtype.slug,
            'sticky': relationtype.featured}


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_users_blogs(apikey, username, password):
    """blogger.getUsersBlogs(api_key, username, password)
    => blog structure[]"""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [blog_structure(site)]


@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_user_info(apikey, username, password):
    """blogger.getUserInfo(api_key, username, password)
    => user structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return user_structure(user, site)


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_authors(apikey, username, password):
    """wp.getAuthors(api_key, username, password)
    => author structure[]"""
    authenticate(username, password)
    return [author_structure(author)
            for author in User.objects.filter(is_staff=True)]


@xmlrpc_func(returns='boolean', args=['string', 'string',
                                      'string', 'string', 'string'])
def delete_post(apikey, post_id, username, password, publish):
    """blogger.deletePost(api_key, post_id, username, password, 'publish')
    => boolean"""
    user = authenticate(username, password, 'relationapp.delete_relationtype')
    relationtype = Relationtype.objects.get(id=post_id, authors=user)
    relationtype.delete()
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_post(post_id, username, password):
    """metaWeblog.getPost(post_id, username, password)
    => post structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return post_structure(Relationtype.objects.get(id=post_id, authors=user), site)


@xmlrpc_func(returns='struct[]',
             args=['string', 'string', 'string', 'integer'])
def get_recent_posts(blog_id, username, password, number):
    """metaWeblog.getRecentPosts(blog_id, username, password, number)
    => post structure[]"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return [post_structure(relationtype, site) \
            for relationtype in Relationtype.objects.filter(authors=user)[:number]]


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_relations(blog_id, username, password):
    """metaWeblog.getRelations(blog_id, username, password)
    => relation structure[]"""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [relation_structure(relation, site) \
            for relation in Relation.objects.all()]


@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'struct'])
def new_relation(blog_id, username, password, relation_struct):
    """wp.newRelation(blog_id, username, password, relation)
    => relation_id"""
    authenticate(username, password, 'relationapp.add_relation')
    relation_dict = {'title': relation_struct['name'],
                     'description': relation_struct['description'],
                     'slug': relation_struct['slug']}
    if int(relation_struct['parent_id']):
        relation_dict['parent'] = Relation.objects.get(
            pk=relation_struct['parent_id'])
    relation = Relation.objects.create(**relation_dict)

    return relation.pk


@xmlrpc_func(returns='string', args=['string', 'string', 'string',
                                     'struct', 'boolean'])
def new_post(blog_id, username, password, post, publish):
    """metaWeblog.newPost(blog_id, username, password, post, publish)
    => post_id"""
    user = authenticate(username, password, 'relationapp.add_relationtype')
    if post.get('dateCreated'):
        creation_date = datetime.strptime(
            post['dateCreated'].value.replace('Z', '').replace('-', ''),
            '%Y%m%dT%H:%M:%S')
    else:
        creation_date = datetime.now()

    relationtype_dict = {'title': post['title'],
                  'content': post['description'],
                  'excerpt': post.get('mt_excerpt', truncate_words(
                      strip_tags(post['description']), 50)),
                  'creation_date': creation_date,
                  'last_update': creation_date,
                  'comment_enabled': post.get('mt_allow_comments', 1) == 1,
                  'pingback_enabled': post.get('mt_allow_pings', 1) == 1,
                  'featured': post.get('sticky', 0) == 1,
                  'tags': 'mt_keywords' in post and post['mt_keywords'] or '',
                  'slug': 'wp_slug' in post and post['wp_slug'] or slugify(
                      post['title']),
                  'password': post.get('wp_password', ''),
                  'status': publish and PUBLISHED or DRAFT}
    relationtype = Relationtype.objects.create(**relationtype_dict)

    author = user
    if 'wp_author_id' in post and user.has_perm('relationapp.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = User.objects.get(pk=post['wp_author_id'])
    relationtype.authors.add(author)

    relationtype.sites.add(Site.objects.get_current())
    if 'relations' in post:
        relationtype.relations.add(*[Relation.objects.get_or_create(
            title=cat, slug=slugify(cat))[0]
                               for cat in post['relations']])

    return relationtype.pk


@xmlrpc_func(returns='boolean', args=['string', 'string', 'string',
                                      'struct', 'boolean'])
def edit_post(post_id, username, password, post, publish):
    """metaWeblog.editPost(post_id, username, password, post, publish)
    => boolean"""
    user = authenticate(username, password, 'relationapp.change_relationtype')
    relationtype = Relationtype.objects.get(id=post_id, authors=user)
    if post.get('dateCreated'):
        creation_date = datetime.strptime(
            post['dateCreated'].value.replace('Z', '').replace('-', ''),
            '%Y%m%dT%H:%M:%S')
    else:
        creation_date = relationtype.creation_date

    relationtype.title = post['title']
    relationtype.content = post['description']
    relationtype.excerpt = post.get('mt_excerpt', truncate_words(
        strip_tags(post['description']), 50))
    relationtype.creation_date = creation_date
    relationtype.last_update = datetime.now()
    relationtype.comment_enabled = post.get('mt_allow_comments', 1) == 1
    relationtype.pingback_enabled = post.get('mt_allow_pings', 1) == 1
    relationtype.featured = post.get('sticky', 0) == 1
    relationtype.tags = 'mt_keywords' in post and post['mt_keywords'] or ''
    relationtype.slug = 'wp_slug' in post and post['wp_slug'] or slugify(
        post['title'])
    relationtype.status = publish and PUBLISHED or DRAFT
    relationtype.password = post.get('wp_password', '')
    relationtype.save()

    if 'wp_author_id' in post and user.has_perm('relationapp.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = User.objects.get(pk=post['wp_author_id'])
            relationtype.authors.clear()
            relationtype.authors.add(author)

    if 'relations' in post:
        relationtype.relations.clear()
        relationtype.relations.add(*[Relation.objects.get_or_create(
            title=cat, slug=slugify(cat))[0]
                               for cat in post['relations']])
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'struct'])
def new_media_object(blog_id, username, password, media):
    """metaWeblog.newMediaObject(blog_id, username, password, media)
    => media structure"""
    authenticate(username, password)
    path = default_storage.save(os.path.join(UPLOAD_TO, media['name']),
                                ContentFile(media['bits'].data))
    return {'url': default_storage.url(path)}
