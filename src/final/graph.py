import py2neo
# from spacy.tokens import Span
# from spacy.language import Language

def flatten_list(nested_list):
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_list(item)
        else:
            yield item


class GraphDatabase:
    """
    图数据库类
        用于统一图数据库通信方式
    """
    # 数据库账户
    neo4j_auth = ("neo4j", "12345678")

    # 特殊的关系名称，此外都与字段名相同
    relationship_name_dic = {
        "type": "is_type",
        "actor": "acted_in",
        "director": "directed",
        "screenwriter": "wrote",
        "region": "product_region"   
    }
    # 指向movie节点的关系，此外都是movie节点指出
    relationship_to_movie = ["acted_in", "wrote", "directed"]
    # person 类型节点
    person_type_nodes = ["actor", "director", "screenwriter"]

    def __init__(self, port=7687):
        print("initing", self.__class__.__name__)
        
        self.graph = ...
        self.init_graph(port)

    def init_graph(self, port):
        try:
            self.graph = py2neo.Graph(f"bolt://localhost:{port}", auth=GraphDatabase.neo4j_auth)
        except py2neo.errors.ConnectionUnavailable:
            # print("neo4j数据库连接失败，请检查数据库是否启动，或者端口是否正确")
            raise py2neo.errors.ConnectionUnavailable("neo4j数据库连接失败，请检查数据库是否启动，或者端口是否正确，或账户是否正确")

    def query(self, query):
        return self.graph.run(query).data()

    def get_relationship_name(self, filed_name):
        return self.relationship_name_dic.get(filed_name, filed_name)
    
    # def merge(self, node, label, key):
    #     return self.graph.merge(node, label, key)

    def get(self, label, key=None, value=None):
        """
        查找所有 label 的数据
        或
        查找 label类型数据的key字段的所有数据
        或
        检查 label类型数据是否有key字段为value的数据，若无返回值为空
        """
        if key is None:
            query = f"MATCH (n:{label}) RETURN n"
        elif key is not None and value is None:
            query = f"MATCH (n:{label}) RETURN n.{key}"
        else:
            query = f"MATCH (n:{label}) WHERE n.{key}='{value}' RETURN n"
        return [i['n'] for i in self.query(query)]
    
    def check_movie_nickname(self, movie_name):
        """
        检查一个movie_name是一部电影的别名还是原名，
            若是原名，则返回原名
            若是别名，则返回原名，
            若数据库中不存在，则返回None
        """
        name_query = f"MATCH (m:movie {{name: '{movie_name}'}}) RETURN m"
        res = self.query(name_query)
        # 是原名
        if res:
            return movie_name
        
        nickname_query = f"MATCH (m:movie) -[:nickname]-> (n:nickname {{name: '{movie_name}'}}) RETURN m.name"
        res = self.query(nickname_query)
        # 是别名
        if res:
            return res[0]['m.name']
        
        return None
           
    def get_movie_one_info(self, movie_name: str, filed: str):
        """
        获取电影信息
        
        特别地, type、region通过关系查询
        """
        movie_name = self.check_movie_nickname(movie_name=movie_name)
        if not movie_name:
            return []
        
        if filed in ["type", "region"]:
            realtion = self.get_relationship_name(filed)
            query = f"MATCH (m:movie {{name: '{movie_name}'}})-[:{realtion}]->(t:{filed}) RETURN t.name"
        else:
            query = f"MATCH (m:movie {{name: '{movie_name}'}}) RETURN m.{filed}"

        result = self.query(query)
        # print(result)
        if result:
            result = [list(res.values()) for res in result]
            result = list(flatten_list(result))
        return result

    def recommend_movie(self, by: str, movie_name: str):
        """
        根据实体推荐
        :param by: 推荐指标，如类型、演员、导演、编剧、国家/地区
        :param movie_name: 匹配的电影名
        返回值示例:
        {
            "类型1": ["电影1", "电影2", ...],
            "类型2": ["电影1", "电影2", ...],
            ...
        }
        """
        # print(by, movie_name)
        realtionship = self.get_relationship_name(by)
        # 演员、类型等可能有多个
        values = self.get_movie_one_info(movie_name, by)
        values = flatten_list(values)
        result = []
        for value in values:
            if realtionship in GraphDatabase.relationship_to_movie:
                query = f"MATCH (m:movie)<-[:{realtionship}]-(:{by} {{name: '{value}'}}) RETURN m.name"
            else:
                query = f"MATCH (m:movie)-[:{realtionship}]->(:{by} {{name: '{value}'}}) RETURN m.name"
            # print(query)
            result.append({value: [i['m.name'] for i in self.query(query)]})
            
        return result
    
    def get_award_info(self, filed: str, _name: str):
        """
        获取电影的奖项信息
        """
        # 人物获奖
        if filed == "be_awarded":
            query = f"MATCH (p:person {{name: '{_name}'}})-[:be_awarded]->(a:award) RETURN a"
        # 电影获奖
        elif filed == "win_award":
            query = f"MATCH (m:movie {{name: '{_name}'}})-[:win_award]->(a:award) RETURN a"
        result = self.query(query)
        if result:
            result = [i['a'] for i in result]
        return result
    
# class NER:
#     """
#     自定义命名实体识别器
#     用于Parser识别自定义的命名实体
#     """
#     def __init__(self, graph_db: GraphDatabase):
#         # self.graph_db = graph_db
#         self.custom_ner_dict = self.init_custom_ner_dict(graph_db)

#     @staticmethod
#     def init_custom_ner_dict(graph_db):
#         custom_ner_dict = {
#             "movie": [record["name"] for record in graph_db.query("MATCH (m:movie) RETURN m.name AS name")],
#             "actor": [record["name"] for record in graph_db.query("MATCH (p:person) RETURN p.name AS name")],
#             "director": [record["name"] for record in graph_db.query("MATCH (p:person) RETURN p.name AS name")],
#             "screenwriter": [record["name"] for record in graph_db.query("MATCH (p:person) RETURN p.name AS name")],
#             "award": [record["name"] for record in graph_db.query("MATCH (a:award) RETURN a.name AS name")],
#             "type": [record["name"] for record in graph_db.query("MATCH (t:type) RETURN t.name AS name")],
#             "region": [record["name"] for record in graph_db.query("MATCH (r:region) RETURN r.name AS name")],
#         }
#         return custom_ner_dict

#     # 自定义命名实体识别器
#     def custom_ner(self, doc):

#         entities = []
#         for token in doc:
#             if token.text in self.custom_ner_dict['movie']:
#                 entities.append(Span(doc, token.i, token.i+1, label="MOVIE"))
#             elif token.text in self.custom_ner_dict['actor']:
#                 entities.append(Span(doc, token.i, token.i+1, label="ACTOR"))
#             elif token.text in self.custom_ner_dict['director']:
#                 entities.append(Span(doc, token.i, token.i+1, label="DIRECTOR"))
#             elif token.text in self.custom_ner_dict['award']:
#                 entities.append(Span(doc, token.i, token.i+1, label="AWARD"))
#             elif token.text in self.custom_ner_dict['type']:
#                 entities.append(Span(doc, token.i, token.i+1, label="TYPE"))
#             elif token.text in self.custom_ner_dict['region']:
#                 entities.append(Span(doc, token.i, token.i+1, label="REGION"))

#         doc.ents = entities
#         return doc
    
#     def __call__(self, doc):
#         return self.custom_ner(doc)
    
# @Language.factory("custom_ner")
# def get_custom_ner(nlp, name):
#     return NER(GraphDatabase(7689)).custom_ner