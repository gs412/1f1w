#!/usr/bin/python
# -*- coding: UTF-8 -*-

import web
from libs import utils

urls = (
    '', 'admin_global.Index',
    'invite/(\d*\/?)', 'admin_global.Invite',
    'invite/delete/(\d+)/', 'admin_global.Invitedelete',
    'post/', 'admin_post.Index',
    'chat/', 'admin_chat.Index',
    'user/(\d*\/?)', 'admin_global.Userlist',
    'user/delete/(\d*)/', 'admin_global.Userdelete',
    'group/', 'admin_global.Group',
    'deletedthread/(\d*\/?)', 'admin_post.Deletedthread',
    'thread/delete/(\d*)/', 'admin_post.Threaddelete',
    'deletedpost/(\d*\/?)', 'admin_post.Deletedpost',
    'post/delete/(\d*)/', 'admin_post.Postdelete',
)
urls = utils.handle_app_urls(__file__, urls)

app = web.application(urls, locals())