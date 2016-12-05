import tornado
import tornado.web
from tornado.options import options, define

import settings
from utils import read_content_from_file
from core import (WedPageWordCounter, WordFilter, SimpleEncryption, InvalidWebURL, RequestWebContentFailure)
from db_models import (save_word_list_to_db, read_word_counter_list, reset_word_counter)


define("port", default=8000, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(read_content_from_file("./static/index.html"))

    def post(self):
        self.set_header("Content-Type", "text/html")
        web_url = self.get_body_argument("web_url")
        try:
            top_word_counter = self.application.web_page_word_counter.start_scan(web_url)
            save_word_list_to_db(top_word_counter, self.application.encryptor)

            html_content = read_content_from_file("./static/results.html.tpl")
            render_lines = []
            for index, word in enumerate(top_word_counter):
                render_lines.append("<ui style=\"font-size: {}pt;\">{}, </ui>".format(105 - 2*index, word[0]))
            html_content = html_content.replace("__WORD_COUNTER_RESULT__", "".join(render_lines))
            self.write(html_content)
        except InvalidWebURL:
            self.write(read_content_from_file("./static/message.html.tpl").replace("__MESSAGE__", "Invalid input"))
        except RequestWebContentFailure:
            self.write(read_content_from_file("./static/message.html.tpl").replace("__MESSAGE__", "error"))
        except Exception:
            self.write(read_content_from_file("./static/message.html.tpl").replace("__MESSAGE__", "error"))


class AdminHanlder(tornado.web.RequestHandler):
    def get(self):
        word_list = read_word_counter_list(self.application.encryptor)
        html_content = read_content_from_file("./static/full_word_list.html.tpl")
        table_content_for_render = []
        for item in word_list:
            table_content_for_render.append("<tr>")
            table_content_for_render.append("<td>{}</td>".format(item['word']))
            table_content_for_render.append("<td>{}</td>".format(item['frequency']))
            table_content_for_render.append("</tr>")

        html_content = html_content.replace("__FULL_WORD_COUNTER_LIST__","\n".join(table_content_for_render))
        self.set_header("Content-Type", "text/html")
        self.write(html_content)


class AdminResetDBHanlder(tornado.web.RequestHandler):

    def get(self):
        reset_word_counter()
        self.write(read_content_from_file("./static/message.html.tpl").
                   replace("__MESSAGE__", "The data has been cleaned up!"))



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/index/", MainHandler),
            (r"/reset/", AdminResetDBHanlder),
            (r"/admin/", AdminHanlder),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "./static"}),
        ]
        self.word_filter = WordFilter("./static/resources/words_filter_dict.json")
        self.web_page_word_counter = WedPageWordCounter(self.word_filter)
        self.encryptor = SimpleEncryption(settings.KEY_STORE_LOCATION)
        tornado.web.Application.__init__(self, handlers)


def main():
    tornado.options.parse_command_line()
    io_loop = tornado.ioloop.IOLoop.instance()

    app = Application()
    app.listen(options.port)
    io_loop.start()


if __name__ == "__main__":
    main()