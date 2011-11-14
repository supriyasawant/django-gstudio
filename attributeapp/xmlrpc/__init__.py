"""XML-RPC methods for Attributeapp"""


ATTRIBUTEAPP_XMLRPC_PINGBACK = [
    ('attributeapp.xmlrpc.pingback.pingback_ping',
     'pingback.ping'),
    ('attributeapp.xmlrpc.pingback.pingback_extensions_get_pingbacks',
     'pingback.extensions.getPingbacks')]

ATTRIBUTEAPP_XMLRPC_METAWEBLOG = [
    ('attributeapp.xmlrpc.metaweblog.get_users_blogs',
     'blogger.getUsersBlogs'),
    ('attributeapp.xmlrpc.metaweblog.get_user_info',
     'blogger.getUserInfo'),
    ('attributeapp.xmlrpc.metaweblog.delete_post',
     'blogger.deletePost'),
    ('attributeapp.xmlrpc.metaweblog.get_authors',
     'wp.getAuthors'),
    ('attributeapp.xmlrpc.metaweblog.get_attributes',
     'metaWeblog.getAttributes'),
    ('attributeapp.xmlrpc.metaweblog.new_attribute',
     'wp.newAttribute'),
    ('attributeapp.xmlrpc.metaweblog.get_recent_posts',
     'metaWeblog.getRecentPosts'),
    ('attributeapp.xmlrpc.metaweblog.get_post',
     'metaWeblog.getPost'),
    ('attributeapp.xmlrpc.metaweblog.new_post',
     'metaWeblog.newPost'),
    ('attributeapp.xmlrpc.metaweblog.edit_post',
     'metaWeblog.editPost'),
    ('attributeapp.xmlrpc.metaweblog.new_media_object',
     'metaWeblog.newMediaObject')]

ATTRIBUTEAPP_XMLRPC_METHODS = ATTRIBUTEAPP_XMLRPC_PINGBACK + ATTRIBUTEAPP_XMLRPC_METAWEBLOG
