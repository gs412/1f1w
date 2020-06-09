#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import web
import conf
from libs import utils

web.config.debug = False

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

render = conf.render_mako(
    directories=[utils.realpath('templates/default/admin')],
    module_directory=utils.realpath('sitedata/cache/templates/admin'),
    input_encoding=conf.charset,
    output_encoding=conf.charset,
)
