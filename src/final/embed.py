# from ollama import embeddings
# import numpy as np


# class Embed:
# """
# 借助 ollama后端嵌入式模型处理
# """
#     def __init__(self, model='nomic-embed-text'):
#         self.model = model
    
#     def embed(self, text):
#         res = embeddings(model=self.model, prompt=text)
#         return np.array(res.embedding)
    
#     def __call__(self, text):
#         return self.embed(text)
    

# def cosine_similarity(vec1, vec2):
#     cos_sim = vec1.dot(vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
#     return cos_sim


# if __name__ == "__main__":
#     embed = Embed()

#     # embed1 = embed("这个杀手不太冷的导演是谁")

#     # a = embed("盗梦空间")
#     # b = embed("这个杀手不太冷")

#     # em2 = embed("的导演是谁")

#     # print(cosine_similarity(embed1, a + em2))
#     # print(cosine_similarity(embed1, b + em2))

#     a = embed("是哪个地区的？")
#     b = embed("是哪个国家的？")
#     c = embed("谁主演的？")
#     d = embed("是哪个国家/地区的？")
#     print(f"{cosine_similarity(a, b)=}")
#     print(f"{cosine_similarity(a, c)=}")
#     print(f"{cosine_similarity(a, d)=}")
#     print(f"{cosine_similarity(b, c)=}")
#     print(f"{cosine_similarity(b, d)=}")
#     print(f"{cosine_similarity(c, d)=}")
