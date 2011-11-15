"""XML-RPC methods of Attributeapp metaWeblog API"""
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

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.settings import PROTOCOL
from attributeapp.settings import UPLOAD_TO
from attributeapp.managers import DRAFT, PUBLISHED
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
        PROTOCOL, site.domain, reverse('attributeapp_attributetype_archive_index')),
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
                reverse('attributeapp_author_detail', args=[user.username]))}


def author_structure(user):
    """An author structure"""
    return {'user_id': user.pk,
            'user_login': user.username,
            'display_name': user.username,
            'user_email': user.email}


def attribute_structure(attribute, site):
    """A attribute structure"""
    return {'description': attribute.title,
            'htmlUrl': '%s://%s%s' % (
                PROTOCOL, site.domain,
                attribute.get_absolute_url()),
            'rssUrl': '%s://%s%s' % (
                PROTOCOL, site.domain,
                reverse('attributeapp_attribute_feed', args=[attribute.tree_path])),
            # Useful Wordpress Extensions
            'attributeId': attribute.pk,
            'parentId': attribute.parent and attribute.parent.pk or 0,
            'attributeDescription': attribute.description,
            'attributeName': attribute.title}


def post_structure(attributetype, site):
    """A post structure with extensions"""
    author = attributetype.authors.all()[0]
    return {'title': attributetype.title,
            'description': unicode(attributetype.html_content),
            'link': '%s://%s%s' % (PROTOCOL, site.domain,
                                   attributetype.get_absolute_url()),
            # Basic Extensions
            'permaLink': '%s://%s%s' % (PROTOCOL, site.domain,
                                        attributetype.get_absolute_url()),
            'attributes': [cat.title for cat in attributetype.attributes.all()],
            'dateCreated': DateTime(attributetype.creation_date.isoformat()),
            'postid': attributetype.pk,
            'userid': author.username,
            # Useful Movable Type Extensions
            'mt_excerpt': attributetype.excerpt,
            'mt_allow_comments': int(attributetype.comment_enabled),
            'mt_allow_pings': int(attributetype.pingback_enabled),
            'mt_keywords': attributetype.tags,
            # Useful Wordpress Extensions
            'wp_author': author.username,
            'wp_author_id': author.pk,
            'wp_author_display_name': author.username,
            'wp_password': attributetype.password,
            'wp_slug': attributetype.slug,
            'sticky': attributetype.featured}


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
    user = authenticate(username, password, 'attributeapp.delete_attributetype')
    attributetype = Attributetype.objects.get(id=post_id, authors=user)
    attributetype.delete()
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string'])
def get_post(post_id, username, password):
    """metaWeblog.getPost(post_id, username, password)
    => post structure"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return post_structure(Attributetype.objects.get(id=post_id, authors=user), site)


@xmlrpc_func(returns='struct[]',
             args=['string', 'string', 'string', 'integer'])
def get_recent_posts(blog_id, username, password, number):
    """metaWeblog.getRecentPosts(blog_id, username, password, number)
    => post structure[]"""
    user = authenticate(username, password)
    site = Site.objects.get_current()
    return [post_structure(attributetype, site) \
            for attributetype in Attributetype.objects.filter(authors=user)[:number]]


@xmlrpc_func(returns='struct[]', args=['string', 'string', 'string'])
def get_attributes(blog_id, username, password):
    """metaWeblog.getAttributes(blog_id, username, password)
    => attribute structure[]"""
    authenticate(username, password)
    site = Site.objects.get_current()
    return [attribute_structure(attribute, site) \
            for attribute in Attribute.objects.all()]


@xmlrpc_func(returns='string', args=['string', 'string', 'string', 'struct'])
def new_attribute(blog_id, username, password, attribute_struct):
    """wp.newAttribute(blog_id, username, password, attribute)
    => attribute_id"""
    authenticate(username, password, 'attributeapp.add_attribute')
    attribute_dict = {'title': attribute_struct['name'],
                     'description': attribute_struct['description'],
                     'slug': attribute_struct['slug']}
    if int(attribute_struct['parent_id']):
        attribute_dict['parent'] = Attribute.objects.get(
            pk=attribute_struct['parent_id'])
    attribute = Attribute.objects.create(**attribute_dict)

    return attribute.pk


@xmlrpc_func(returns='string', args=['string', 'string', 'string',
                                     'struct', 'boolean'])
def new_post(blog_id, username, password, post, publish):
    """metaWeblog.newPost(blog_id, username, password, post, publish)
    => post_id"""
    user = authenticate(username, password, 'attributeapp.add_attributetype')
    if post.get('dateCreated'):
        creation_date = datetime.strptime(
            post['dateCreated'].value.replace('Z', '').replace('-', ''),
            '%Y%m%dT%H:%M:%S')
    else:
        creation_date = datetime.now()

    attributetype_dict = {'title': post['title'],
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
    attributetype = Attributetype.objects.create(**attributetype_dict)

    author = user
    if 'wp_author_id' in post and user.has_perm('attributeapp.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = User.objects.get(pk=post['wp_author_id'])
    attributetype.authors.add(author)

    attributetype.sites.add(Site.objects.get_current())
    if 'attributes' in post:
        attributetype.attributes.add(*[Attribute.objects.get_or_create(
            title=cat, slug=slugify(cat))[0]
                               for cat in post['attributes']])

    return attributetype.pk


@xmlrpc_func(returns='boolean', args=['string', 'string', 'string',
                                      'struct', 'boolean'])
def edit_post(post_id, username, password, post, publish):
    """metaWeblog.editPost(post_id, username, password, post, publish)
    => boolean"""
    user = authenticate(username, password, 'attributeapp.change_attributetype')
    attributetype = Attributetype.objects.get(id=post_id, authors=user)
    if post.get('dateCreated'):
        creation_date = datetime.strptime(
            post['dateCreated'].value.replace('Z', '').replace('-', ''),
            '%Y%m%dT%H:%M:%S')
    else:
        creation_date = attributetype.creation_date

    attributetype.title = post['title']
    attributetype.content = post['description']
    attributetype.excerpt = post.get('mt_excerpt', truncate_words(
        strip_tags(post['description']), 50))
    attributetype.creation_date = creation_date
    attributetype.last_update = datetime.now()
    attributetype.comment_enabled = post.get('mt_allow_comments', 1) == 1
    attributetype.pingback_enabled = post.get('mt_allow_pings', 1) == 1
    attributetype.featured = post.get('sticky', 0) == 1
    attributetype.tags = 'mt_keywords' in post and post['mt_keywords'] or ''
    attributetype.slug = 'wp_slug' in post and post['wp_slug'] or slugify(
        post['title'])
    attributetype.status = publish and PUBLISHED or DRAFT
    attributetype.password = post.get('wp_password', '')
    attributetype.save()

    if 'wp_author_id' in post and user.has_perm('attributeapp.can_change_author'):
        if int(post['wp_author_id']) != user.pk:
            author = User.objects.get(pk=post['wp_author_id'])
            attributetype.authors.clear()
            attributetype.authors.add(author)

    if 'attributes' in post:
        attributetype.attributes.clear()
        attributetype.attributes.add(*[Attribute.objects.get_or_create(
            title=cat, slug=slugify(cat))[0]
                               for cat in post['attributes']])
    return True


@xmlrpc_func(returns='struct', args=['string', 'string', 'string', 'struct'])
def new_media_object(blog_id, username, password, media):
    """metaWeblog.newMediaObject(blog_id, username, password, media)
    => media structure"""
    authenticate(username, password)
    path = default_storage.save(os.path.join(UPLOAD_TO, media['name']),
                                ContentFile(media['bits'].data))
    return {'url': default_storage.url(path)}
