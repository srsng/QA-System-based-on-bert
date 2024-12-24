import pandas as pd
from py2neo import Graph, Node, Relationship
# import numpy as np

# csv数据读取
df = pd.read_csv("data/movie.csv", encoding="utf-8")

df.fillna("", inplace=True)

df['award'] = df['award'].apply(eval)
df['actor'] = df['actor'].apply(eval)
df['screenwriter'] = df['screenwriter'].apply(eval)
df['actor_url'] = df['actor_url'].apply(eval)
df['screenwriter_url'] = df['screenwriter_url'].apply(eval)
df['nickname'] = df['nickname'].apply(eval)

df['type'] = df['type'].map(lambda x: x.split())
df['region'] = df['region'].map(lambda x: x.split())

to_drop = ['Unnamed: 0', 'index']
for col in to_drop:
    if col in df.columns:
        df.drop(columns=col, inplace=True)

# 连接图形库，配置neo4j
graph = Graph("bolt://localhost:7689", auth=("neo4j", "12345678"))

def add_node_and_rel(node_name, node_type, rel_name):
    _node = Node(node_type, name=node_name)
    graph.merge(_node, node_type, "name")
    rel = Relationship(movie_node, rel_name, _node)
    graph.merge(rel)



# 清空全部数据
graph.delete_all()
# 开启一个新的事务
graph.begin()

# 获取所有列标签
fileds = df.columns.tolist()
# 获取数据数量
num = len(df["title"])

# KnowledgeGraph知识图谱构建(以电影为主体构建的知识图谱)
for idx, row in df.iterrows():
    print(idx, row['title'])

    # 将row转化为字典
    row_dic = row.to_dict()

    title = row_dic.pop("title")
    awards = row_dic.pop("award")
    types = row_dic.pop("type")
    regions = row_dic.pop("region")
    nicknames = row_dic.get("nickname")

    actor_ls = row_dic.get("actor")
    actor_url_ls = row_dic.pop("actor_url")

    screenwriter_ls = row_dic.get("screenwriter")
    screenwriter_url_ls = row_dic.pop("screenwriter_url")

    # 创建电影节点
    movie_node = Node("movie", name=title, **row_dic)
    graph.merge(movie_node, "movie", "name")

    # 创建类型节点和关系
    for type_ in types:
        add_node_and_rel(type_, "type", "is_type")
    
    # 创建别名节点和关系
    for nickname in nicknames:
        add_node_and_rel(nickname, "nickname", "nickname")

    # 创建地区节点和关系
    for region in regions:
        add_node_and_rel(region, "region", "product_region")

    # 创建导演节点和关系
    director_node = Node("person", name=row_dic['director'])
    graph.merge(director_node, "person", "name")
    rel = Relationship(director_node, "directed", movie_node)
    graph.merge(rel)

    # 创建演员节点和关系
    for idx2, actor in enumerate(actor_ls):
        actor_node = Node("person", name=actor, url=actor_url_ls[idx2])
        graph.merge(actor_node, "person", "name")
        rel = Relationship(actor_node, "acted_in", movie_node)
        graph.merge(rel)
    
    # 创建编剧节点和关系
    for idx2, screenwriter in enumerate(screenwriter_ls):
        screenwriter_node = Node("person", name=screenwriter, url=screenwriter_url_ls[idx2])
        graph.merge(screenwriter_node, "person", "name")
        rel = Relationship(screenwriter_node, "wrote", movie_node)
        graph.merge(rel)

    # 创建奖项节点和关系
    for award in awards:
        award_title = award['award_title']
        award_year = award['award_year'].lstrip('(')
        award_name = award['award_name']
        awardees = award['awardees']

        # 创建奖项节点
        award_node = Node("award", title=award_title, year=award_year, name=award_name)
        graph.merge(award_node, "award", "title")

        # 创建关系：电影获得了奖项
        rel = Relationship(movie_node, "win_award", award_node)
        graph.merge(rel)

        # 创建获奖者节点和关系
        for awardee in awardees:
            awardee_node = Node("person", name=awardee)
            graph.merge(awardee_node, "person", "name")

            # 创建关系：获奖者获得了奖项
            rel = Relationship(awardee_node, "be_awarded", award_node)
            graph.merge(rel)

    # 创建其他节点和关系
    for key, value in row_dic.items():
        ## 建立分结点
        node2 = Node(key, name=value)
        graph.merge(node2, key, "name")
        ## 创建关系
        rel = Relationship(movie_node, key, node2)
        # print(rel)
        graph.merge(rel)