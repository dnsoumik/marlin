#!/usr/bin/env
# coding: utf-8
from abc import ABCMeta

import tornado.ioloop
import tornado.web
import tornado

from build_config import WEB_SERVER_PORT
from handler.authorization.sign_in import SignInHandler
from handler.authorization.sign_up import SignUpHandler
from handler.element.country import CountryHandler
from handler.resource.profile import ProfileHandler
from util.conn_util import MongoMixin
from util.file_util import FileUtil
from util.log_util import Log


class IndexHandler(tornado.web.RequestHandler, metaclass=ABCMeta):
    fu = FileUtil()

    async def prepare(self):
        self.set_status(404)
        error_page_raw = open('./lib/http_error/404.html', 'r')
        error_page = error_page_raw.read()
        error_page_raw.close()
        self.write(
            error_page.format(self.fu.serverUrl)
        )
        await self.finish()
        return


class App(tornado.web.Application, MongoMixin):
    def __init__(self):
        settings = {
            'debug': False
        }
        super(App, self).__init__(
            handlers=[
                # (r'/', IndexHandler),
                # (r'/web/async', AsyncHttpHandler),
                # (r'/gen', GenHttpHandler),
                # (r'/sync', SyncHttpHandler),
                # (r'/sleep', SleepHandler),
                (r'/api/country', CountryHandler),
                (r'/api/resource/profile', ProfileHandler),
                (r'/api/auth/sign_in', SignInHandler),
                (r'/api/auth/sign_up', SignUpHandler),
                # (r'/web/api/authorization/sign_out', SignOutHandler),
                # (r'/web/api/forms', FormsHandler),
                # (r'/web/api/forms_data', FormsDataHandler),
            ],
            **settings,
            default_handler_class=IndexHandler
        )
        Log.i('APP', 'Running Tornado Application Port - [ {} ]'.format(WEB_SERVER_PORT))


if __name__ == "__main__":
    app = App()
    app.listen(WEB_SERVER_PORT)
    tornado.ioloop.IOLoop.current().start()
