#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
import yaml
import json
import time
import base64
import random
import hashlib
import asyncio
import requests
import markdown
import threading
import subprocess
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
# from tools import make_json, solr_tools
from system.config import Config
import logging
import logging.config
import pygame
from utils import *

logger = logging.getLogger('server')

uiManager = None
server_ioloop = None
# http_server = None

class BaseHandler(tornado.web.RequestHandler):
    logger = None

    def getLogger(self):
        if self.logger is None:
            self.logger = logging.getLogger('server.{}'.format(self.__class__.__name__))
        return self.logger

    def initialize(self):
        self.getLogger()
        pass

    def prepare(self):
        # self.request.method,
        # self.request.uri,
        # self.request.remote_ip,
        # self.getLogger().debug('request: {}'.format(self._request_summary()))
        self._request_summary()
        pass
    def isValidated(self):
        if not self.get_secure_cookie('validation'):
            return False
        return str(self.get_secure_cookie("validation"), encoding='utf-8') == Config().get('server.validate', '')
    def validate(self, validation):
        if validation is not None and '"' in validation:
            validation = validation.replace('"', '')
        return validation == Config().get('server.validate', '') or validation == str(self.get_cookie('validation'))


class MainHandler(BaseHandler):
    def get(self):
        if not self.isValidated():
            self.redirect("/login")
            return
        self.render('index.html', update_info='', suggestion=[], notices=[])

class RobotEventHandler(BaseHandler):
    def post(self):
        global uiManager
        if not self.validate(self.get_argument('validate', default=None)):
            res = {'code': 1, 'message': 'illegal visit'}
            self.write(json.dumps(res))
        else:
            res = {'code': 0, 'message': 'ok'}
            eventName = self.get_argument('name')
            eventArgs = self.get_argument('args')
            uiManager.robotEvent(eventName, eventArgs)
            self.write(json.dumps(res))
        self.finish()

class RobotMessageHandler(BaseHandler):

    def post(self):
        global uiManager
        if not self.validate(self.get_argument('validate', default=None)):
            res = {'code': 1, 'message': 'illegal visit'}
            self.write(json.dumps(res))
        else:
            res = {'code': 0, 'message': 'ok'}
            robotMsgStr = self.get_argument('robot_msg')
            uiManager.robotMessage(robotMsgStr)
            self.write(json.dumps(res))
        self.finish()

class RobotWakeUpHandler(BaseHandler):

    def post(self):
        global uiManager
        if not self.validate(self.get_argument('validate', default=None)):
            res = {'code': 1, 'message': 'illegal visit'}
            self.write(json.dumps(res))
        else:
            res = {'code': 0, 'message': 'ok'}
            if uiManager is None:
                logger.warn('uiManager is none')
            uiManager.robotWakeUp()
            self.write(json.dumps(res))
        self.finish()

class RobotSleepHandler(BaseHandler):

    def post(self):
        global uiManager
        if not self.validate(self.get_argument('validate', default=None)):
            res = {'code': 1, 'message': 'illegal visit'}
            self.write(json.dumps(res))
        else:
            res = {'code': 0, 'message': 'ok'}
            uiManager.robotSleep()
            self.write(json.dumps(res))
        self.finish()

class LoginHandler(BaseHandler):
    def get(self):
        if self.isValidated():
            self.redirect('/')
        else:
            self.render('login.html', error=None)
    def post(self):
        if self.get_argument('username') == Config().get('server.username') and \
           hashlib.md5(self.get_argument('password').encode('utf-8')).hexdigest() \
           == Config().get('server.validate'):
            self.getLogger().debug('success')
            self.set_secure_cookie("validation", Config().get('server.validate'))
            self.redirect("/")
        else:
            self.render('login.html', error="登录失败")


class LogoutHandler(BaseHandler):
    
    def get(self):
        if self.isValidated():
            self.set_secure_cookie("validation", '')
        self.redirect("/login")

settings = {
    "cookie_secret": Config().get('server.cookie_secret', "__GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
    "template_path": os.path.join(sys.path[0], "server/templates"),
    "static_path": os.path.join(sys.path[0], "server/static"),
    "login_url": "/login",
    "debug": True
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    # (r"/gethistory", GetHistoryHandler),
    # (r"/chat", ChatHandler),
    # (r"/chat/updates", MessageUpdatesHandler),
    # (r"/config", ConfigHandler),
    # (r"/getconfig", GetConfigHandler),
    # (r"/operate", OperateHandler),
    # (r"/getlog", GetLogHandler),
    # (r"/log", LogHandler),
    (r"/logout", LogoutHandler),
    (r"/robot/wakeUp", RobotWakeUpHandler),
    (r"/robot/sleep", RobotSleepHandler),
    (r"/robot/message", RobotMessageHandler),
    (r"/robot/event", RobotEventHandler),
    # (r"/api", APIHandler),
    # (r"/qa", QAHandler),
    (r"/launchers/(.+\.(?:png|jpg|jpeg|bmp|gif|JPG|PNG|JPEG|BMP|GIF))", tornado.web.StaticFileHandler, {'path': 'images/launcher'}),
    (r"/photo/(.+\.(?:png|jpg|jpeg|bmp|gif|JPG|PNG|JPEG|BMP|GIF))", tornado.web.StaticFileHandler, {'path': Config().get('camera.dest_path', 'server/static')}),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'server/static'})
], **settings)


def start_server(mgr, start_callback):
    global uiManager, http_server
    uiManager = mgr
    if Config().get('server.enable', False):
        logger.info('''
            Web管理端：http://{}:{}
'''.format(Config().get('server.host', '0.0.0.0'), Config().get('server.port', '4096')))

        port = Config().get('server.port', '4096')
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            application.listen(int(port))
            io_loop = tornado.ioloop.IOLoop.current()
            # io_loop.make_current()
            if start_callback is not None:
                start_callback(io_loop)
            # print('start_server: io_loop', io_loop)
            # dumpThreads('io_loop before start')
            io_loop.start()
            # dumpThreads('io_loop end')
        except Exception as e:
            logger.critical('服务器启动失败: {}'.format(e))
        
def _server_started(ioloop):
    global server_ioloop
    # logger.debug('server started, ioloop %s', ioloop)
    server_ioloop = ioloop

def stop_server():
    global server_ioloop
    # logger.debug('stop server, server_ioloop: %d', server_ioloop)
    # dumpThreads('stop server')
    if server_ioloop is not None:
        # logger.debug('stop io_loop')
        server_ioloop.add_callback(lambda: server_ioloop.stop())
    # dumpThreads('stopped server')
    logger.info('server stopped')

def run(uiManager):
    # pygame.register_quit(lambda: stop_server())
    t = threading.Thread(target=lambda: start_server(uiManager, _server_started), name='ServerThread')
    t.start()
