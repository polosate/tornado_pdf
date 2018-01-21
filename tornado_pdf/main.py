import tornado.web
import tornado.process
import sqlite3
import os
import shlex

user_content_path = os.path.join(os.path.dirname(__file__), '..', 'usercontent')


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listen(kwargs.get('settings', {}).get('debug_port', 8888))
        self.conn = sqlite3.connect(kwargs.get('settings', {}).get('db_connection', '../main.db'), isolation_level=None)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("session")


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        cursor = self.application.conn.cursor()
        cursor.execute('''select name from files where user=?''', (self.current_user.decode('utf-8'),))
        files = cursor.fetchall()
        self.render("templates/add_pdf.html", files=files)


class AddHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        file_body = self.request.files['file'][0]['body']
        name = self.request.files['file'][0]['filename']
        user = self.current_user.decode('utf-8')

        try:
            folder = os.path.join(user_content_path, user)
            os.mkdir(folder)
        except FileExistsError:
            pass

        cursor = self.application.conn.cursor()
        cursor.execute('''INSERT INTO files (user, name) values (?, ?) ''',
                       (user, name))
        with open(os.path.join(folder, name), 'wb') as file:
            file.write(file_body)
        self.application.conn.commit()
        self.redirect("/add?filename="+name)

    @tornado.web.authenticated
    def get(self):
        name = self.get_argument('filename')
        user = self.current_user.decode('utf-8')

        self.render("templates/done.html", filename="/".join(['file', user, name]))


class SinglePageHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, name=None, page_number=None):
        if not name:
            name = self.get_argument('name')
        if not page_number:
            page_number = self.get_argument('page_number')
        user = self.current_user.decode('utf-8')
        folder = os.path.join(user_content_path, user)
        command = 'pdftk "%s" cat %s output %s' % (os.path.join(folder, name), page_number, os.path.join(folder, 'result.pdf'))
        args = shlex.split(command)
        print(args)
        proc = tornado.process.Subprocess(args)
        await proc.wait_for_exit()
        # proc.wait_for_exit().add_callback(self.pdf_split_done)
        self.redirect("/"+("/".join(['file', user, 'result.pdf'])))

    # def pdf_split_done(self):
    #     self.redirect("/"+("/".join(['file', user, 'result.pdf'])))


class LoginHandler(BaseHandler):
    def get(self):
        self.render("templates/login.html", user = self.current_user)

    def post(self):
        conn = self.application.conn
        cursor = conn.cursor()
        login = self.get_argument("login")
        password = self.get_argument("password")
        cursor.execute('''select * from users where login=? and password=?''',
                       (login, password))
        user = cursor.fetchone()
        if user:
            self.set_secure_cookie('session', login)
            self.redirect("/", False)
        else:
            self.redirect("/login", False) # надо бы показать сообщение об ошибке

if __name__ == "__main__":
    static_path = user_content_path
    settings = settings = {
        "cookie_secret": "serious bananas though request abyr secret 1 45 11",
        "login_url": "/login",
        "debug": "True"
    }
    application = Application([
        (r"/add", AddHandler),
        (r"/login", LoginHandler),
        (r"/", MainHandler),
        (r"/page/(.*)/(.*)", SinglePageHandler),
        (r"/page", SinglePageHandler),
        (r"/file/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    ], **settings)

tornado.ioloop.IOLoop.current().start()
