from final.graph import GraphDatabase
from final.question import Classifier
import json
import itertools
import random

def build_dataset():
    intension = Classifier.intension
    gdb = GraphDatabase(7689)


    # get all movie data
    movies = gdb.get("movie")
    movie_names = [movie["name"] for movie in movies]
    # 二维列表
    movie_nicknames = [movie["nickname"] for movie in movies]
    # 汇总到一个一维列表
    for nicknames in movie_nicknames:
        movie_names += nicknames

    def get(name="actor"):
        actors = gdb.get(name)
        actor_names = [actor["name"] for actor in actors]
        actor_names = set(itertools.chain.from_iterable(actor_names))
        return actor_names

    # actor
    actor_names = get("actor")
    screenwriter_names = get("screenwriter")
    director_names = get("director")


    """
    intnesion e.g.
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
            "awarded": awarded,
        }
    """


    key_words = ["这部电影", "这个演员", "这个导演", "这个编剧"]
    key_names = ["movie_name", "actor_name", "director_name", "screenwriter_name"]
    data_names = [movie_names, actor_names, director_names, screenwriter_names]

    data = []

    # 组合数据
    for intension, sentence_temps in intension.items():
        intent = intension
        for sentence in sentence_temps:
            # 判断 ["这部电影", "这个演员", "这个导演", "这个编剧"] 中的一个
            for key_index, key_word in enumerate(key_words):
                if key_word in sentence:
                    _names = data_names[key_index]
                    for _name in _names:
                        for _i in range(2):
                            # 40% 跳过 ， 同时排除空字符串，_name不知道哪来的空值导致数据集处理会卡住？？
                            # 虽然已经修复了现有的数据集的这个问题，但是留着这个判断吧
                            if random.random() < 0.4 and _name:
                                continue
                            data.append(                    
                                dict(
                                    intent=intent,
                                    domain="movie", 
                                    text=sentence.replace(
                                                key_word,
                                                _name + key_word if _i else _name
                                            ),
                                    slots={key_names[key_index]: _name}
                                )
                            )
                    break
            

    # 加入一些脏数据，用于非问答内容的 None 类型意图训练
    dirty_temp = [
        "这部电影的有多少个群演",
        "这个演员多少岁了",
        "这部电影血腥吗",
        "这部电影有续作吗",
        "这个演员的别名是什么",
        "这个演员的简介",
        "今天适合看什么电影",
        "电影的历史是什么",
        "今天吃什么好",
        "话说这个导演有什么小故事吗",
        "那这部电影有什么花絮吗",
        "你知道这个编剧的生平吗",
    ]

    intent = "None"
    for sentence in dirty_temp:
        # 判断 ["这部电影", "这个演员", "这个导演", "这个编剧"] 中的一个
        did = False
        for key_index, key_word in enumerate(key_words):
            if key_word in sentence:
                did = True
                _names = data_names[key_index]
                for _name in _names:
                    for _i in range(2):
                        # 30% 跳过
                        if random.random() < 0.3:
                            continue
                        data.append(                    
                            dict(
                                intent=intent,
                                domain="movie", 
                                text=sentence.replace(
                                            key_word,
                                            _name + key_word if _i else _name
                                        ),
                                slots={key_names[key_index]: _name}
                            )
                        )
                break
        if not did:
            data.append(                    
                dict(
                    intent=intent,
                    domain="movie", 
                    text=sentence,
                    slots={}
                )
            )

    with open(r"src\NLP\bert_intent_slot\data\DouBanTop250\data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("done")


if __name__ == '__main__':
    build_dataset()