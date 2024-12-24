# -*- coding:utf-8 -*-
# @author: 木子川
# @Email:  m21z50c71@163.com
# @VX：fylaicai


import time
# from detector import JointIntentSlotDetector
from NLP.bert_intent_slot.detector import JointIntentSlotDetector


start1_time = time.perf_counter()
model = JointIntentSlotDetector.from_pretrained(
    model_path='./save_model/bert-base-chinese',
    tokenizer_path='./save_model/bert-base-chinese',
    intent_label_path=r'src\NLP\bert_intent_slot\data\DouBanTop250\intent_labels.txt',
    slot_label_path=r'src\NLP\bert_intent_slot\data\DouBanTop250\slot_labels.txt'
)
start2_time = time.perf_counter()
all_text = [
    # 与数据集直接相关的问题
    '巩俐得过什么奖？',
    "大红灯笼高高挂是什么类型的电影？",
    "大红灯笼高高挂这部电影的得分是多少分？",
    "爱在日落黄昏时得过什么奖？",
    "鬼子来了有什么别名？",
    "推荐一下跟鬼子来了一个类型的电影",
    # 数据集中没出现过的人名、电影名
    "苹果嘉儿出演过什么电影？",
    "小马宝莉的编剧是谁？",
    # 无关问题
    "刘德华多少岁了？",
    # 多目标测试
    "刘德华跟周星驰演过什么电影？",
    "大红灯笼高高挂与鬼子来了是什么类型的电影"
]
for i in all_text:
    print(i, '\n\t', model.detect(i))

end_time = time.perf_counter()
time1 = (end_time - start1_time) / 3600
time2 = (end_time - start2_time) / 3600
print("所有检测时间（包括加载模型）：", time1, "s", "除去模型加载时间：", time2, "s",
      "总预测数据量：", len(all_text), "平均预测一条的时间（除去加载模型）：", time2 / len(all_text), "s/条")
