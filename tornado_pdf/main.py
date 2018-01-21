import os

import tornado.web
import sqlite3


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listen(kwargs.get('settings', {}).get('debug_port', 8888))
        self.conn = sqlite3.connect(kwargs.get('settings', {}).get('db_connection', '../main.db'))


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("session")


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("templates/add_pdf.html")


class AddHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        print(self.request.files)
        file_body = self.request.files['file'][0]['body']
        name = self.get_argument('name')
        user = self.current_user
        print(name, user)


class LoginHandler(BaseHandler):
    def get(self):
        self.render("templates/login.html", user = self.current_user)

    def post(self):
        # let's pretend there is real authentication
        conn = self.application.conn
        cursor = conn.cursor()
        login = self.get_argument("login")
        password = self.get_argument("password")
        cursor.execute('''select * from users where login=? and password=?''',
                       (login, password))
        user = cursor.fetchone()
        print(user)
        if user:
            self.set_secure_cookie('session', login)
            self.redirect("/", False)
        else:
            self.redirect("/login", False) # надо бы показать сообщение об ошибке

if __name__ == "__main__":
    static_path = os.path.join(os.path.dirname(__file__), '..', 'usercontent')
    settings = {
        "cookie_secret": "serious bananas though request abyr secret 1 45 11",
        "login_url": "/login",
        "debug": "True"
    }
    application = Application([
        (r"/add", AddHandler),
        (r"/login", LoginHandler),
        (r"/", MainHandler),
        (r"/file/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    ], **settings)

    tornado.ioloop.IOLoop.current().start()
