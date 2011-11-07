"""XML-RPC methods for Gstudio"""


GSTUDIO_XMLRPC_PINGBACK = [
    ('gstudio.xmlrpc.pingback.pingback_ping',
     'pingback.ping'),
    ('gstudio.xmlrpc.pingback.pingback_extensions_get_pingbacks',
     'pingback.extensions.getPingbacks')]

GSTUDIO_XMLRPC_METAWEBLOG = [
    ('gstudio.xmlrpc.metaweblog.get_users_blogs',
     'blogger.getUsersBlogs'),
    ('gstudio.xmlrpc.metaweblog.get_user_info',
     'blogger.getUserInfo'),
    ('gstudio.xmlrpc.metaweblog.delete_post',
     'blogger.deletePost'),
    ('gstudio.xmlrpc.metaweblog.get_authors',
     'wp.getAuthors'),
    ('gstudio.xmlrpc.metaweblog.get_metatypes',
     'metaWeblog.getMetatypes'),
    ('gstudio.xmlrpc.metaweblog.new_metatype',
     'wp.newMetatype'),
    ('gstudio.xmlrpc.metaweblog.get_recent_posts',
     'metaWeblog.getRecentPosts'),
    ('gstudio.xmlrpc.metaweblog.get_post',
     'metaWeblog.getPost'),
    ('gstudio.xmlrpc.metaweblog.new_post',
     'metaWeblog.newPost'),
    ('gstudio.xmlrpc.metaweblog.edit_post',
     'metaWeblog.editPost'),
    ('gstudio.xmlrpc.metaweblog.new_media_object',
     'metaWeblog.newMediaObject')]

GSTUDIO_XMLRPC_METHODS = GSTUDIO_XMLRPC_PINGBACK + GSTUDIO_XMLRPC_METAWEBLOG
