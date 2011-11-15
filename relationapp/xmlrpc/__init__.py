"""XML-RPC methods for Relationapp"""


RELATIONAPP_XMLRPC_PINGBACK = [
    ('relationapp.xmlrpc.pingback.pingback_ping',
     'pingback.ping'),
    ('relationapp.xmlrpc.pingback.pingback_extensions_get_pingbacks',
     'pingback.extensions.getPingbacks')]

RELATIONAPP_XMLRPC_METAWEBLOG = [
    ('relationapp.xmlrpc.metaweblog.get_users_blogs',
     'blogger.getUsersBlogs'),
    ('relationapp.xmlrpc.metaweblog.get_user_info',
     'blogger.getUserInfo'),
    ('relationapp.xmlrpc.metaweblog.delete_post',
     'blogger.deletePost'),
    ('relationapp.xmlrpc.metaweblog.get_authors',
     'wp.getAuthors'),
    ('relationapp.xmlrpc.metaweblog.get_relations',
     'metaWeblog.getRelations'),
    ('relationapp.xmlrpc.metaweblog.new_relation',
     'wp.newRelation'),
    ('relationapp.xmlrpc.metaweblog.get_recent_posts',
     'metaWeblog.getRecentPosts'),
    ('relationapp.xmlrpc.metaweblog.get_post',
     'metaWeblog.getPost'),
    ('relationapp.xmlrpc.metaweblog.new_post',
     'metaWeblog.newPost'),
    ('relationapp.xmlrpc.metaweblog.edit_post',
     'metaWeblog.editPost'),
    ('relationapp.xmlrpc.metaweblog.new_media_object',
     'metaWeblog.newMediaObject')]

RELATIONAPP_XMLRPC_METHODS = RELATIONAPP_XMLRPC_PINGBACK + RELATIONAPP_XMLRPC_METAWEBLOG
