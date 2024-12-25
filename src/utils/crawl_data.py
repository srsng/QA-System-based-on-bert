import requests
from lxml import etree
import pandas as pd
import time
import random

# cookies = 'll="118172"; bid=GRQ0a4CQ2yo; _pk_id.100001.4cf6=643c438a7c20489f.1718536235.; __utma=223695111.1076308420.1718536235.1718536235.1718536235.1; _vwo_uuid_v2=D10CD881617BEEF39E7241A617A605074|a00d7bdb8f856d71eac7ef91d30bb3df; __utma=30149280.193522773.1718536235.1718536235.1718785826.2; douban-fav-remind=1; viewed="30584432_35066598_26295448_1437504_36937097_37000613_35501207_34882208_1159821_1135952"; dbcl2="285485265:LMcGWNiqVNQ"; ck=IQyR; push_noty_num=0; push_doumail_num=0; frodotk_db="246b628cd78566e06d4227a6869034a0"'
cookies = None

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

if cookies:
    headers['cookie'] = cookies

page_url = 'https://movie.douban.com/top250'

params = {
    'start': 0,
    'filter':'',
}

data_fileds = [
    'title', 'nickname', 'rank', 'year', 'region', 'type', 'url', 'short_comment', 'rating_cnt', 'rating_num', 
    'director', 'screenwriter', 'screenwriter_url', 'actor', 'actor_url',
    'summary', 'award', 
    # 'language'
]
data_ls = []
# df = pd.DataFrame(columns=data_fileds)
rank = 0
# 获取基本名单
for i in range(10):
    params['start'] = i * 25
    time.sleep(0.5+random.random())
    page_source = requests.get(page_url, headers=headers, params=params).text

    tree = etree.HTML(page_source)

    cards = tree.xpath('//*[@id="content"]/div/div[1]/ol/li')
    for card in cards:
        rank += 1
        print(rank)
        movie_names = card.xpath('./div/div[2]/div[1]/a/span/text()')
        title = movie_names[0].strip()
        temp_nickname = [i.strip().strip('/').strip() for i in movie_names[1:]]
        nickname = []
        for _nick in temp_nickname:
            nickname += [i for i in _nick.split("  /  ") if i]
            
        href = card.xpath('.//div[@class="hd"]/a/@href')[0]
        short_comment = card.xpath('.//span[@class="inq"]/text()')
        short_comment = short_comment[0] if short_comment else ''
        rating_cnt = card.xpath('.//div[@class="star"]/span[last()]/text()')[0]
        rating_num = card.xpath('.//span[@class="rating_num"]/text()')[0]
        
        *year, region, type_ = [i.strip() for i in card.xpath('.//div[2]/p[1]/text()[2]')[0].split('/')]
        year = '/'.join(year)
        data_ls.append([
            title,
            nickname,
            rank,
            year,
            region,
            type_,
            href,
            short_comment,
            rating_cnt.strip("人评价"),
            rating_num
        ])

error_ls = []
# 爬取影片数据
random.shuffle(data_ls)
for index, film in enumerate(data_ls):
    # 随机休眠3~15秒
    time.sleep(random.randint(3, 15)+random.random())

    url = film[6]
    print(film[0], url)
    try:
        page = requests.get(url=url, headers=headers).text

        tree = etree.HTML(page)

        # title = tree.xpath('//*[@id="content"]/h1/span[1]/text()')[0]
        # year = tree.xpath('//*[@id="content"]/h1/span[2]/text()')[0].strip('()')

        director = tree.xpath('//*[@id="info"]/span[1]/span[2]/a/text()')[0]

        screenwriter_a_ls = tree.xpath('//*[@id="info"]/span[2]/span[2]/a')
        screenwriter = [i.xpath('text()')[0] for i in screenwriter_a_ls]
        screenwriter_url = [i.xpath('@href')[0] for i in screenwriter_a_ls]

        actor_a_ls = tree.xpath('//*[@id="info"]/span[3]/span[2]//a')
        actor = [i.xpath('text()')[0] for i in actor_a_ls]
        actor_url = [i.xpath('@href')[0] for i in actor_a_ls]

        # info_text = tree.xpath('//*[@id="info"]/text()')
        # info_text = [i.strip() for i in info_text if i.strip()]
        # region = info_text[1]
        # language = info_text[2]
        # nickname = info_text[4]

        # type_list = []
        # for element in tree.xpath('//*[@id="info"]/span[4]/following-sibling::*'):
        #     if element.tag == 'br':
        #         break
        #     type_list.append(element.xpath('text()')[0])
        # type_ = '/'.join(type_list)

        summary_nodes = tree.xpath('//*[@id="link-report-intra"]/span')
        summary_node = summary_nodes[1] if len(summary_nodes) == 3 else summary_nodes[0]
        summary = '\n\n'.join([i.strip() for i in summary_node.xpath('./text()')])

        # 获奖信息
        award = []
        try:
            awards_page = requests.get(url=url+'awards/', headers=headers).text
            awards_tree = etree.HTML(awards_page)

            awards_sections = awards_tree.xpath('//div[@class="awards"]')

            for section in awards_sections:
                award_title = section.xpath('.//div[@class="hd"]/h2/a/text()')[0]
                award_year = section.xpath('.//div[@class="hd"]/h2/span[@class="year"]/text()')[0].strip('()')
                awards = section.xpath('.//ul[@class="award"]')
                
                for award_ in awards:
                    award_name = award_.xpath('.//li[1]/text()')[0]
                    awardees = award_.xpath('.//li[2]//a/text()')
                    award.append({
                        'award_title': award_title,
                        'award_year': award_year,
                        'award_name': award_name,
                        'awardees': awardees
                    })

        except Exception as e:
            print('\t', e)
            
        cur_data = [
            director, screenwriter, screenwriter_url, actor, actor_url,
            summary, award
        ]
        data_ls[index].extend(cur_data)

    except Exception as e:
        print('\t', e)
        error_ls.append(data_ls[index])
        continue

df = pd.DataFrame(data_ls, columns=data_fileds)
df.to_csv("data/movie.csv")
