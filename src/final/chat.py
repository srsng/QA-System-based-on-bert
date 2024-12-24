from final.question import Classifier
from final.answer import Answer
from final.graph import GraphDatabase
import os
import signal


class ChatBot:
    def __init__(self, database_port=7687):
        self.cmd_start = '/'
        self.cmd_quit_ls = ['exit', 'quit', 'bye']

        self.graph_db = GraphDatabase(database_port)

        self.parser_classifier = Classifier()
        # self.parser = Parser()
        self.answer = Answer(self.graph_db)

    def _quit(self):
        os.kill(os.getpid(), signal.SIGINT)

    def check_cmd(self, sent):
        return sent.startswith(self.cmd_start)
        
    def parse_cmd(self, sent):
        if not self.check_cmd(sent):
            return False
        
        sent = sent.lstrip(self.cmd_start)

        if sent in self.cmd_quit_ls:
            return self._quit()
        else:
            return f'"{self.cmd_start}{sent}" 有误，退出请尝试: {self.cmd_start+self.cmd_quit_ls[0]}'
        

    def chat(self, sent):
        # 解析指令
        parse_cmd_res = self.parse_cmd(sent)
        if parse_cmd_res:
            return parse_cmd_res
        
        # 解析QA
        # entities = self.parser.parse(sent)
        # intension = self.classifier.classify(sent)
        intension, entities = self.parser_classifier.parse_classify(text=sent)
        # print(intension, entities)
        answer = self.answer.answer(intension, entities)
        return answer

    def self_intro(self):
        return '\
            你好，我是豆瓣Top 250电影助手，有什么问题可以问我哦！\n\
            你可以问我关于豆瓣Top 250电影的问题，比如：\n\t\
                主要内容是什么\n\t\
                导演是谁\n\t\
                是谁主演的\n\t\
                什么时候播出的\n\t\
                是那个国家/地区的\n\t\
                类型是什么\n\t\
                豆瓣评分是多少\n\t\
                豆瓣评价人数是多少\n\t\
                同类型/主演/导演/国家/地区电影推荐\n\t\
                电影获奖\n\t\
                ...\n\
            输入/quit或/bye或/exit退出.\n\
            '