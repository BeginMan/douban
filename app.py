# coding=utf-8
__author__ = 'fang'
import os
import json
import tornado.web
import tornado.httpclient
import tornado.httpserver
import tornado.gen
import tornado.ioloop
import tornado.options
import tornado.ioloop


BASE_DIR = os.path.join(os.path.dirname(__file__))

from tornado.options import define, options
define('port', default=8090, help='run this port', type=int)

class DemoHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    #todo:add cache
    def get(self):
        """
        @api:https://developers.douban.com/wiki/?title=book_v2#get_user_collections
        @:arg
        @:returns
            想读：wish  在读：reading  读过：read
        """
        jsonpCallback = self.get_argument("jsonpCallback", None)
        self.set_header("Content-Type", "application/javascript")
        client = tornado.httpclient.AsyncHTTPClient()
        result = yield tornado.gen.Task(client.fetch, 'https://api.douban.com/v2/book/user/70526937/collections')
        data = json.loads(result.body)
        books  = data['collections']
        status = {'wish':[], 'reading':[], 'read':[]}
        for book in books:
            dic = {}
            if book['status'] in status:
                dic['tags'] = ','.join(book.get('tags', ''))
                dic['image'] = book['book']['image']
                dic['title'] = book['book']['title']
                dic['url'] = book['book']['alt']
                status.get(book['status']).append(dic)

        data = json.dumps(status)
        self.write("%s(%s)" % (jsonpCallback, data))
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.httpserver.HTTPServer(tornado.web.Application(
            handlers = [
                (r'/demo', DemoHandler),
            ],
            **{
                'autoreload':True,
                'static_path': os.path.join(BASE_DIR, 'static'),
            }
    ))
    app.listen(options.port)
    print 'run app with port:%s' % options.port
    tornado.ioloop.IOLoop.instance().start()
