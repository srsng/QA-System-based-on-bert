# from final.embed import Embed, cosine_similarity
# from graph import get_custom_ner
from NLP.bert_intent_slot.detector import JointIntentSlotDetector
from final.graph import flatten_list

# class Parser:
#     """
#     解析器
#         用于解析文本，提取命名实体
#     """
#     def __init__(self):
#         self.nlp = self.get_nlp()
#         # self.graph_db = graph_db
    
#     def get_nlp(self, custom_ner:str="custom_ner"):
#         nlp = spacy.load("zh_core_web_sm")
#         nlp.add_pipe(custom_ner, after="ner")
#         return nlp

#     def parse(self, text):
#         # 处理文本
#         doc = self.nlp(text)
#         # 提取命名实体
#         entities = [(ent.text, ent.label_) for ent in doc.ents]

#         return entities
    
#     def __call__(self, doc):
#         return self.parse(doc)
        

class Classifier:
    """
    问题分类器
        用于分类问题

    问题类别包括：
        1. 导演
        2. 演员
        3. 编剧
        4. 上映时间
        5. 国家/地区
        6. 类型
        7. 评分
        8. 评价人数
        9. 同类型推荐
        10. 同演员推荐
        11. 同导演推荐
        12. 同编剧推荐
        13. 同国家/地区推荐
        14. 电影获奖情况
        15. 演员获奖情况
        16. 简介
        17. 短评
        18. 别名
        19. 排名
    """
    director = ["这部电影的导演是谁", "这部电影是谁拍的"]
    actor = ["这部电影是谁主演的", "这部电影的主演都有谁", "这部电影的主角是谁"]
    screenwriter = ["这部电影的编剧是谁", "这部电影的剧本是谁写的"]
    year = ["这部电影是什么时候播出的", "这部电影是什么时候上映的", "这部电影是哪一年上映的"]
    region = ["这部电影是哪个国家/地区的", "这部电影是哪里的"]
    type_ = ["这部电影的类型是什么", "这部电影什么类型的电影"]
    rating_num = ["这部电影的评分是多少", "这部电影的评分怎么样", "这部电影的得分是多少分"]
    rating_cnt = ["这部电影的评价人数是多少", "这部电影有多少人评价过"]
    summary = ["这部电影的简介是什么", "这部电影的剧情简介是什么"]
    short_comment = ["这部电影的短评是什么", "这部电影的短评有哪些"]
    nickname = ["这部电影的别名是什么", "这部电影有什么别名"]
    rank = ["这部电影的排名是多少", "这部电影的排名怎么样"]

    recommend_type = ["与这部电影同一个类型的电影推荐", "给我推荐跟这部电影同一个类型的电影", "与这部电影同类型的电影的经典作品还有什么"]
    recommend_actor = ["与这部电影同一个演员的电影推荐", "给我推荐跟这部电影同一个演员的电影", "这个演员的代表作品还有哪些"]
    recommend_director = ["与这部电影同一个导演的电影推荐", "给我推荐跟这部电影同一个导演的电影", "这个导演的代表作品还有哪些"]
    recommend_screenwriter = ["与这部电影同一个编剧的电影推荐", "给我推荐跟这部电影同一个编剧的电影", "这个编剧的代表作品还有哪些"]
    recommend_region = ["与这部电影同一个国家/地区的电影推荐"]

    win_award = ["这部电影获得了哪些奖项"]
    be_awarded = ["这个演员获得了哪些奖项"]

    intension = {
            "director": director,
            "actor": actor,
            "screenwriter": screenwriter,
            "year": year,
            "region": region,
            "type": type_,
            "rating_num": rating_num,
            "rating_cnt": rating_cnt,
            "summary": summary,
            "short_comment": short_comment,
            "nickname": nickname,
            "rank": rank,
            "recommend_type": recommend_type,
            "recommend_actor": recommend_actor,
            "recommend_director": recommend_director,
            "recommend_screenwriter": recommend_screenwriter,
            "recommend_region": recommend_region,
            "win_award": win_award,
            "be_awarded": be_awarded,
    }

    def __init__(self):
        print("initing", self.__class__.__name__)
        self.intension = Classifier.intension
        # self.embed = Embed()
        # self.embed_intention()
        
        self.model = JointIntentSlotDetector.from_pretrained(
            model_path='./save_model/bert-base-chinese',
            tokenizer_path='./save_model/bert-base-chinese',
            intent_label_path=r'src\NLP\bert_intent_slot\data\DouBanTop250\intent_labels.txt',
            slot_label_path=r'src\NLP\bert_intent_slot\data\DouBanTop250\slot_labels.txt'
        )

    def parse_classify(self, text, ):
        """
        返回
            (intent, entities)
        intent: type
        entities: dict
        e.g.
            ('actor', {'movie_name': ['刘德华']})

            ('awarded', {'actor_name': ['巩俐']})
        """
        res = self.model.detect(text)
        intent = res['intent']
        entities = list(flatten_list(list(res['slots'].values())))
        return intent, entities

    # def embed_intention(self):
    #     for key, value_ls in self.intension.items():
    #         self.intension[key] = [self.embed(value) for value in value_ls]

    # def classify(self, text, threshold1=0.83, threshold2 = 0.75):
    #     text_vec = self.embed(text)
    #     max_sim = 0
    #     sec_sim = 0
    #     max_key = None
    #     # sec_key = None
    #     for key, value in self.intension.items():
    #         for v in value:
    #             sim = cosine_similarity(text_vec, v)
    #             if sim > max_sim:
    #                 sec_sim = max_sim
    #                 # sec_key = max_key
    #                 max_sim = sim
    #                 max_key = key

    #     print(max_key, max_sim)

    #     res = None
    #     # 如果最大相似度大于阈值1或者第二大相似度小于阈值2
    #     if max_sim > threshold1 or sec_sim < threshold2:
    #         res = max_key

    #     return res
    