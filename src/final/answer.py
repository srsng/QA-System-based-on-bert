from typing import List
from final.question import Classifier
from final.graph import GraphDatabase
import random

class Answer:
    """
    回答生成器
        用于生成回答
    """
    answer_fileds = list(Classifier.intension.keys())

    answer_template = {
        # 简单查找电影信息型
        "director": "电影《{}》的导演是{}。",
        "actor": "电影《{}》的主演如下：{}",
        "screenwriter": "电影《{}》的编剧有：{}",
        "year": "电影《{}》是{}年上映的。",
        "region": "电影《{}》是{}的。",
        "type": "电影《{}》的类型是{}。",
        "rating_num": "电影《{}》的豆瓣评分是{}分。",
        "rating_cnt": "电影《{}》的豆瓣评价人数是{}人。",
        "summary": "以下是电影《{}》的简介：\n{}。",
        "short_comment": "电影《{}》的短评是：\n\t{}",
        "nickname": "电影《{}》的别名有{}。",
        "rank": "电影《{}》在豆瓣Top 250的排名是第{}名。",
        # 一次关联查找型
        "recommend_type": "与{}同一个类型的电影推荐如下：\n{}",
        "recommend_actor": "与{}同一个演员的电影推荐如下：\n{}",
        "recommend_director": "与{}同一个导演的电影推荐如下：\n{}",
        "recommend_screenwriter": "与{}同一个编剧的电影推荐如下：\n{}",
        "recommend_region": "与{}同一个国家/地区的电影推荐如下：\n{}",
        # 复杂查找型
        "win_award": "{}获得了如下奖项：\n{}",
        "be_awarded": "{}获得了如下奖项：\n{}",
    }

    # 一些中文
    to_cn = {
        "director": "导演",
        "actor":"演员",
        "screenwriter": "编剧",
        "year": "年份",
        "region": "国家/地区",
        "type": "类型",
        "rating_num": "豆瓣评分",
        "rating_cnt": "豆瓣评分人数",
        "summary": "总结",
        "short_comment": "短评",
        "nickname": "别名",
        "rank": "豆瓣电影Top250排名",
        "recommend_type": "",
        "recommend_actor": "",
        "recommend_director": "",
        "recommend_screenwriter": "",
        "recommend_region": "",
        # 复杂查找型
        "win_award": "",
        "be_awarded": "",
    }

    info_types = ["director", "actor","screenwriter","year","region","type","rating_num","rating_cnt","summary","short_comment","nickname","rank",]
    recommend_types = ["recommend_type", "recommend_actor", "recommend_director", "recommend_screenwriter","recommend_region"]
    award_types = ["win_award", "be_awarded"]

    recommend_max = 10

    def __init__(self, graph_db: GraphDatabase):
        print("initing", self.__class__.__name__)
        # assert set(self.answer_filed) == set(self.answer_template.keys())
        self.graph_db = graph_db

    def answer(self, answer_field: str, entities: List[str]) -> str:
        """
        根据实体和意图生成回答
        :param answer_field: 意图
        :param entities: 实体
        :return: 回答
        """
        # 过滤无效问题
        if answer_field == "None" or answer_field not in Answer.answer_fileds:
            return "暂不支持该问题的回答。"

        res = self.prepare_answers(answer_field, entities)
        # 现在的版本只有一个实体
        res = res[0]
        res_str = self.format_answers(res, answer_field, entities)
        return res_str

    def prepare_answers(self, answer_field: str, entities: List[str]):
        res = []

        # 查找信息型
        if answer_field in Answer.info_types:
            for entity in entities:
                res += [self.graph_db.get_movie_one_info(entity, answer_field)]

        # 推荐型
        elif answer_field in Answer.recommend_types:
            by = answer_field.split("_")[1]
            res += [self.graph_db.recommend_movie(by, entity) for entity in entities]

        # 获奖型
        elif answer_field in Answer.award_types:
            res += [self.graph_db.get_award_info(answer_field, entity) for entity in entities]

        return res

    def format_answers(self, data: list, answer_field: str, entities: List[str]):
        res = ""
        if answer_field in Answer.info_types:
            res = self.format_info(data, answer_field, entities)
        elif answer_field in Answer.recommend_types:
            res = self.format_recommend(data, answer_field, entities)
        elif answer_field in Answer.award_types:
            res = self.format_award(data, answer_field, entities)

        return res

    def format_info(self, info_data: list, answer_field: str, entities: List[str]):
        # print(info_data)
        # print(entities)
        output = []
        # print(info_data)
        for entity in entities:
            if answer_field in ["rating_num", "rating_cnt", "rank"]:
                info_data = [str(i) for i in info_data]
            if len(info_data) == 0:
                output.append(f"没有找到{entity}的{Answer.to_cn[answer_field]}信息。")
            else:
                output.append(Answer.answer_template[answer_field].format(entity, '、'.join(info_data)))
        return '\n'.join(output)

    def format_recommend(self, recommend_data: list, answer_field: str, entities: List[str]):
        # print(recommend_data, answer_field, entities)
        if len(recommend_data) == 0:
            return f"没有找到有关{"、".join([entity.join(["《", "》"]) for entity in entities])}的信息，请询问有关豆瓣电影Top 250的内容。"

        output = []
        recommend_type = answer_field.split("_")[1]
        recommend_type_cn = Answer.to_cn[recommend_type]
        # print(recommend_data)
        # 没有统一类型的
        null_key = []
        for i, entity in enumerate(entities):
            lines = []
            for j in range(len(recommend_data)):
                for key, recommend in recommend_data[j].items():
                    line = ""
                    if len(recommend) == 0:
                        # line = f"没有与{key}同一{recommend_type_cn}的电影."
                        null_key.append(key)
                    else:
                        if len(recommend) > Answer.recommend_max:
                            recommend = random.sample(recommend, Answer.recommend_max)
                            line = f"{key}电影较多，推荐其中随机{Answer.recommend_max}部如下："
                        else:
                            line = f"{key}电影如下："
                        line += "\n\t" + "、".join([rec_item.join(["《", "》"]) for rec_item in recommend[:5]])
                        if len(recommend) > 5:
                            line += "\n\t" + "、".join([rec_item.join(["《", "》"]) for rec_item in recommend[5:]])

                    if line:
                        lines.append(line)
            if null_key:
                null_key_str = ""
                if len(null_key) > 3:
                    null_key = null_key[:3]
                    null_key_str =  f"等{len(null_key)}人"
                null_key_str = "、".join(null_key) + null_key_str

                line = f"没有与{null_key_str}同一{recommend_type_cn}的电影."
                lines.append(line)

            content = '\n'.join(lines)

            # res = Answer.answer_template[answer_field].format(entity, content)
            res = content
            output.append(res)

        return '\n'.join(output)

    def format_award(self, award_data: list, answer_field: str, entities: List[str]):
        """
        格式化获奖信息, 包括title, name, year
        """
        output = []
        entity = entities[0]
        # print(award_data)
        # for i, entity in enumerate(entities):
        lines = []
        # for award in award_data[i]:
        for award in award_data:
            line = f"{award['title']}\t{award['name']}\t{award['year']}"
            lines.append(line)
        content = '\t' + '\n\t'.join(lines)

        if answer_field == "win_award":
            entity = f"《{entity}》"
        res = Answer.answer_template[answer_field].format(entity, content)
        output.append(res)

        return '\n'.join(output)