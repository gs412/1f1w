#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import web
from web.contrib.template import render_mako

web.config.debug = True
web.config.session_parameters['timeout'] = 2400
web.config.session_parameters['secret_key'] = 'adjvweotuah2934723thghfgewr'

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
cookies_secret_key = 'kaldsfhweyofusdhkj39fsdhfewh509345'

dbn = 'sqlite'
dbname = os.path.join(SITE_ROOT, 'sitedata/db.db')

version = '2011.3.3'
charset = 'utf-8'

render = render_mako(
    directories=[os.path.join(SITE_ROOT, 'templates/default')],
    module_directory=os.path.join(SITE_ROOT, 'sitedata/cache/templates'),
    input_encoding=charset,
    output_encoding=charset,
)