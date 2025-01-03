# 基于模板的QA系统

## 基本介绍

### 系统架构

基本架构如下:

<img src="./img/README/base_design_build.svg" alt="base_design_build" style="width:67%;" />

不过这是最初的实现方式，因为最开始使用的是`ollama`的`nomic-embed-text`嵌入模型来根据模板比较语义，进而确定用户意图；使用`spacy`的`zh_core_web_sm`命名实体识别模型来NER，然后自定义一个命名实体识别器，来提取现在知识库中的人名、电影名等。

但是效果太差了，好在我遇到了`JointBert`模型，用它来提取用户输入的意图与其中的相关实体，替换了原先分离的两个部分（这两个部分还在代码中，只是被注释掉了）。

~~没遇到的话估计就去研究AC自动机了。~~

模型的代码仓库: [Linear95/bert-intent-slot-detector: BERT-based intent and slots detector for chatbots.](https://github.com/Linear95/bert-intent-slot-detector)

现在的基本架构如下：

<img src="./img/README/design_work.svg" alt="design_work" style="width:67%;" />

具体的思路如下：

<img src="./img/README/design_build.svg" alt="design_build" style="width:67%;" />

### 数据集

使用的数据集为 自行收集的公开数据：豆瓣电影 Top250，包含

`title`, `nickname`, `rank`, `year`, `region`, `type`, `url`, `short_comment`, `rating_cnt`, `rating_num`, `director`, `screenwriter`, `screenwriter_url`, `actor`, `actor_url`, `summary`, `award`

具体指：

      1. 电影名
      2. 电影别名
      3. Top250排名
      4. 上映年
      5. 生产地区
      6. 类型
      7. 豆瓣对应链接
      8. 短评
      9. 评分人数
      10. 评分
      11. 导演
      12. 编剧
      13. 编剧的豆瓣url
      14. 演员
      15. 演员的豆瓣url
      16. 简介
      17. 获奖情况

其中获奖情况指的是`电影/awards`页面相关数据，包含电影获奖与演员获奖。

### 问题模板范围

能够识别的问题包含以下范围：

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

数据库构方式建见`src\data\build_db.py`

数据库中存在的关系如下：

| StartNode |  Relationship  |    EndNode    |
| :-------: | :------------: | :-----------: |
|   movie   |   win_award    |     award     |
|   movie   |    nickname    |   nickname    |
|   movie   |      rank      |     rank      |
|   movie   |      year      |     year      |
|   movie   |      url       |      url      |
|   movie   | short_comment  | short_comment |
|   movie   |   rating_cnt   |  rating_cnt   |
|   movie   |   rating_num   |  rating_num   |
|   movie   |    director    |   director    |
|   movie   |  screenwriter  | screenwriter  |
|   movie   |     actor      |     actor     |
|   movie   |    summary     |    summary    |
|   movie   | product_region |    region     |
|   movie   |    is_type     |     type      |
|  person   |    directed    |     movie     |
|  person   |     wrote      |     movie     |
|  person   |   be_awarded   |     award     |
|  person   |    acted_in    |     movie     |

## 部署

python环境见`pyproject.toml`配置。

neo4j使用最新版即可。

**注：**如果有遇到neo4j无法启动的情况，可以尝试禁止neo4j联网，打开后如果是白屏，使用`ctrl+r`来刷新即可。

建议使用项目管理工具[rye](https://github.com/astral-sh/rye)，使用conda不保证可行。

所有脚本都**必须在项目根目录**，使用`python`命令执行。

### 环境初始化

执行以下命令，即可完成虚拟环境创建。
```cmd
rye sync
```

### 训练自己的JointBert模型

数据准备、训练、测试等见`src\NLP\bert_intent_slot`中的readme，或参考原仓库[Linear95/bert-intent-slot-detector: BERT-based intent and slots detector for chatbots.](https://github.com/Linear95/bert-intent-slot-detector)

本项目对该项目中的一些导入、默认参数等略作修改。

训练数据通过`src\data\build_dataset.py`根据`豆瓣电影Top 250相关数据`与`问题模板`，以及`无关问题意图模板`生成。

基础模型请下载并存放至`src\NLP\bert_intent_slot`或其他目录，注意修改train.py中的相关路径即可。

基本流程可以参考修改`src\utils\bert_pipeline.py`中的相关导入。

不想研究可以直接**在项目根目录**执行这行命令：

```cmd
python src\utils\bert_pipeline.py
```

即可开始训练数据生成、训练数据处理、训练。

### 运行

执行下述命令执行主程序：

```
python src\main.py
```

**注：**如果neo4j数据库auth不是默认的(‘neo4j’, ‘12345678’)，注意在`src\final\graph.py`中修改。

## 效果展示

```
python src\main.py
```

以下是执行了上述命令后交互的效果，其中任何**加粗**、`...`都为手动添加，以提取重点
  
initing GraphDatabase  
initing Classifier  
initing Answer  
            你好，我是豆瓣Top 250电影助手，有什么问题可以问我哦！  
            你可以问我关于豆瓣Top 250电影的问题，比如：  
                        主要内容是什么  
                        导演是谁  
                        是谁主演的  
                        什么时候播出的  
                        是那个国家/地区的  
                        类型是什么  
                        豆瓣评分是多少  
                        豆瓣评价人数是多少  
                        同类型/主演/导演/国家/地区电影推荐  
                        电影获奖  
                        ...  
            输入/quit或/bye或/exit退出.  

你:你是什么？  
Bot: 暂不支持该问题的回答。  
你:我想知道你住哪？  
Bot: 暂不支持该问题的回答。  
你:活着是什么时候的？  
Bot: 电影《活着》是1994年上映的。  
你:霸王别姬**是什么电影**？  
Bot: 电影《霸王别姬》的类型是剧情、爱情、同性。  
你:霸王别姬**怎么样**？  
Bot: 电影《霸王别姬》的类型是剧情、爱情、同性。  
你:霸王别姬讲了什么？  
Bot: 以下是电影《霸王别姬》的简介：  
段小楼（张丰毅）与程蝶衣（张国荣）是`...`  
你:一个叫欧**伟**的男人决定去死有什么别名？  
Bot: 没有找到一个叫欧伟的男人决定去死的别名信息。  
你:一个叫欧**维**的男人决定去死有什么别名？  
Bot: 电影《一个叫欧维的男人决定去死》的别名有**Toy Story 3**、反斗奇兵3(港)、**玩具的故事3**。  
你:**Toy Story 3**有什么别名？  
Bot: 没有找到**to##ystory3**的别名信息。  
你:**玩具的故事3**讲了什么？  
Bot: 以下是电影《玩具的故事3》的简介：  
欧维（罗夫·拉斯加德 Rolf Lassgård 饰）是一个刻`...`  

你:肖申克的救赎拿过哪些奖？        
Bot: 《肖申克的救赎》获得了如下奖项：  
        第67届奥斯卡金像奖      最佳剪辑(提名)   (1995  
        第52届金球奖    电影类 最佳编剧  (1995  
        第19届日本电影学院奖    最佳新人         (1996  
        第20届报知映画赏        最佳男配角       (1995  
你:肖申克的救赎谁演的？  
Bot: 电影《肖申克的救赎》的主演如下：蒂姆·罗宾斯、摩根·弗里曼、鲍勃·冈顿、威`...`  
你:保罗·麦克兰尼拿过什么奖？  
Bot: 保罗·麦克兰尼获得了如下奖项：  

你:肖申克的救赎导演是谁？  
Bot: 电影《肖申克的救赎》的导演是弗兰克·德拉邦特。  
你:弗兰克·德拉邦特拿过什么奖？  
Bot: 弗兰克·德拉邦特获得了如下奖项：  
        第67届奥斯卡金像奖      最佳剪辑(提名)   (1995  
        第52届金球奖    电影类 最佳编剧  (1995  
        第20届报知映画赏        最佳男配角       (1995  
        第72届奥斯卡金像奖      最佳音响(提名)   (2000  
你:肖申克的救赎是哪的？  
Bot: 电影《肖申克的救赎》是美国的。  
你:肖申克的救赎编剧是谁？  
Bot: 电影《肖申克的救赎》的编剧有：弗兰克·德拉邦特、斯蒂芬·金  
你:简单介绍一下肖申克的救赎  
Bot: 电影《肖申克的救赎》的别名有The Shawshank Redemption、月黑高飞(港)、刺激1995(台)。  
你:肖申克的救赎短评  
Bot: 电影《肖申克的救赎》的短评是：  
        希望让人自由。  

你:肖申克的救赎同类型的电影有哪些？    
Bot: 犯罪电影较多，推荐其中随机10部如下：  
        《看不见的客人》、《恐怖直播》、《教父2》、《可可西里》、《上帝之城》  
        《杀人回忆》、《猫鼠游戏》、《荒蛮故事》、《罗生门》、《七宗罪》  
剧情电影较多，推荐其中随机10部如下：  
        《狩猎》、《被嫌弃的松子的一生》、《穿条纹睡衣的男孩》、《星际穿越》、《卢旺达饭店》  
        《7号房的礼物》、《大佛普拉斯》、《拯救大兵瑞恩》、《恐怖游轮》、《让子弹飞》  

## 总结

对于定义了的几个问题模板能够较好的识别，能够即时`对话`，用户角度是几乎无延迟的。

但是该项目使用的方法本质还算是基于模板的，只是通过bert模型让相关实现相对简单，但是对模板的依赖仍然较强。

本项目的实现有英文支持较差（可能是模型问题）、且不支持模糊查询（可以优化），不支持多目标（可能可以训练优化），不支持复合意图（修改模型架构可能可以优化）等问题。

~~为什么里面有个轮子的名称叫final？单纯因为这是期末作业~~