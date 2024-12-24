import pytest

from final.answer import Answer
from final.graph import GraphDatabase


@pytest.fixture(scope="module")
def answer():
    gdb = GraphDatabase(7689)
    return Answer(gdb)

def test_answer_info(answer):
    temp = [
        ("director", ['肖申克的救赎']),
        ("director", ['Titanic']),
        ("actor", ['肖申克的救赎']),
        ("actor", ['Titanic']),
        ("screenwriter", ['肖申克的救赎']),
        ("screenwriter", ['Titanic']),
        ("year", ['肖申克的救赎']),
        ("year", ['Titanic']),
        ("region", ['肖申克的救赎']),
        ("region", ['Titanic']),
        ("type", ['肖申克的救赎']),
        ("type", ['Titanic']),
        ("rating_num", ['肖申克的救赎']),
        ("rating_num", ['Titanic']),
        ("rating_cnt", ['肖申克的救赎']),
        ("rating_cnt", ['Titanic']),
        ("summary", ['肖申克的救赎']),
        ("summary", ['Titanic']),
        ("short_comment", ['肖申克的救赎']),
        ("short_comment", ['Titanic']),
        ("nickname", ['肖申克的救赎']),
        ("nickname", ['Titanic']),
        ("rank", ['肖申克的救赎']),
        ("rank", ['Titanic']),
        ("nickname",["比八不"])
    ]
    for t in temp:
        result = answer.answer(t[0], t[1])
        print(t[0])
        print(result)
        print()

def test_answer_recommend(answer):
    movie_name = ['快乐的大脚']
    temp = [
        "recommend_type",
        "recommend_actor",
        "recommend_director",
        "recommend_screenwriter",
        "recommend_region"
    ]
    for t in temp:
        result = answer.answer(t, movie_name)
        print(t)
        print(result)
        print()

def test_answer_award(answer):
    temp = [
        ("be_awarded", ['古斯塔沃·桑多拉拉']),
        ("be_awarded", ['里卡多·达林']),
        ("win_award", ['肖申克的救赎']),
    ]
    for t in temp:
        result = answer.answer(t[0], t[1])
        print(t[0])
        print(result)
        print()

if __name__ == "__main__":
    gdb = GraphDatabase(7689)
    ans = Answer(gdb)
    # test_answer_award(ans)
    # test_answer_recommend(ans)
    test_answer_info(ans)