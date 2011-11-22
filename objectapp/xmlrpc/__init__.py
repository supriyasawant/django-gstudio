"""XML-RPC methods for Objectapp"""


OBJECTAPP_XMLRPC_PINGBACK = [
    ('objectapp.xmlrpc.pingback.pingback_ping',
     'pingback.ping'),
    ('objectapp.xmlrpc.pingback.pingback_extensions_get_pingbacks',
     'pingback.extensions.getPingbacks')]

OBJECTAPP_XMLRPC_METAWEBLOG = [
    ('objectapp.xmlrpc.metaweblog.get_users_blogs',
     'blogger.getUsersBlogs'),
    ('objectapp.xmlrpc.metaweblog.get_user_info',
     'blogger.getUserInfo'),
    ('objectapp.xmlrpc.metaweblog.delete_post',
     'blogger.deletePost'),
    ('objectapp.xmlrpc.metaweblog.get_authors',
     'wp.getAuthors'),
    ('objectapp.xmlrpc.metaweblog.get_objecttypes',
     'metaWeblog.getObjecttypes'),
    ('objectapp.xmlrpc.metaweblog.new_Objecttype',
     'wp.newObjecttype'),
    ('objectapp.xmlrpc.metaweblog.get_recent_posts',
     'metaWeblog.getRecentPosts'),
    ('objectapp.xmlrpc.metaweblog.get_post',
     'metaWeblog.getPost'),
    ('objectapp.xmlrpc.metaweblog.new_post',
     'metaWeblog.newPost'),
    ('objectapp.xmlrpc.metaweblog.edit_post',
     'metaWeblog.editPost'),
    ('objectapp.xmlrpc.metaweblog.new_media_object',
     'metaWeblog.newMediaObject')]

OBJECTAPP_XMLRPC_METHODS = OBJECTAPP_XMLRPC_PINGBACK + OBJECTAPP_XMLRPC_METAWEBLOG
