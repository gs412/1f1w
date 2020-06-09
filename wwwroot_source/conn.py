#!/usr/bin/python
# -*- coding: UTF-8 -*-

import bsddb
import os
import web
import conf

db = web.database(dbn=conf.dbn, db=conf.dbname)

    
class Bdb:
    def decorator():
        def newdeco(func):
            def function(*args):
                args = map(lambda x: str(x) if isinstance(x, (int, float)) else x, args)
                self = args[0]
                self.dbenv = bsddb.db.DBEnv()
                self.dbenv.open(os.path.join(self.siteroot,'sitedata/bsddb/'), bsddb.db.DB_CREATE | bsddb.db.DB_INIT_MPOOL)
                self.db = bsddb.db.DB(self.dbenv)
                self.db.open('%s.bdb'%self.table, bsddb.db.DB_HASH, bsddb.db.DB_CREATE, 0666)
                f = func(*args)
                self.db.close()
                self.dbenv.close()
                return f
            return function
        return newdeco
    
    def __init__(self, table):
        self.siteroot = conf.SITE_ROOT
        self.table = table
        
    @decorator()
    def update(self, key):
        value = self.db.get(key, default='0')
        self.db.put(key, str(int(value)+1))
        return value
    
    @decorator()
    def set(self, key, value):
        self.db.put(key, value)
    
    @decorator()
    def get(self, key):
        return self.db.get(key, default='0')
    
    @decorator()
    def has_key(self, key):
        return self.db.has_key(key)
    
    @decorator()
    def delete(self, key):
        self.db.delete(key)
        
    @decorator()
    def getdict(self, keylist):
        keylist = map(str, keylist)
        D = {}
        for key in keylist:
            value = self.db.get(key, default='0')
            D.setdefault(int(key), int(value))
        return D
    
    @decorator()
    def getall(self):
        return self.db.items()