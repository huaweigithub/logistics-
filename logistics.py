#coding=utf-8

import tornado.ioloop
import tornado.web
# import tornado.log
import logging

from bs4 import BeautifulSoup
import requests
import json
# from pprint import pprint

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# tornado.log.enable_pretty_logging(logger=logger)

# 获取单号详情页面

def get_code_html(code):
    url = "http://www.t-cat.com.tw/Inquire/TraceDetail.aspx?BillID=%s&ReturnUrl=Trace.aspx"%code
    d = requests.get(url)
    content = d.text
    return content
# result = get_code_html(620152014134)

# 提取网页内响应物流内容
def get_result(html_doc):
    soup = BeautifulSoup(html_doc, 'html5lib', from_encoding="utf-8")
    table_content = soup.find("table")
    return table_content


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/form.html", error="")

class ResultHandler(tornado.web.RequestHandler):
    def get(self):
        code = self.get_argument("code")  # 这里的code必须是（"templates/result.html"）表单的name
        try:
            code_html = get_code_html(code)
            table_result = get_result(code_html)
            all_span_text = []
            spans = table_result.find_all('span')
            for span in spans:
                # print(span)
                # print(span.text)
                all_span_text.append(span.text.strip())
            if len(all_span_text) == 0:
                return self.render("templates/form.html", error=u'订单号错误或暂时没有物流信息')
            order_num = all_span_text[0]
            infos = all_span_text[1:]
            # print((json.dumps(all_span_text, ensure_ascii=False, indent=2)))
        except BaseException as e:
            logger.error(e)
            # raise
            # 出错的情况
            self.render("templates/form.html", error = u'查询超时或订单号错误，请稍后重试')
        else:
            # 没有出错的情况
            # print('order num = %s' % order_num)
            # print('infos = %s' % json.dumps(infos, ensure_ascii=False, indent=2))
            rows = []
            for status, at_time, at_place in zip(infos[::3], infos[1::3], infos[2::3]):
                # print(status, at_time, at_place)
                row = {
                    'status': status,
                    'at_time': at_time,
                    'at_place': at_place
                }
                print(row)
                rows.append(row)
                print(rows)
            self.render("templates/result.html", order_num = order_num, rows = rows)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/result", ResultHandler),
    ], debug = True,static_path="static" )

if __name__ == "__main__":
    app = make_app()
    app.listen(7856)
    tornado.ioloop.IOLoop.instance().start()
