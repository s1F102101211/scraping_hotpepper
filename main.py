import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import datetime as dt


class HotPepper:
    def __init__(self, mode):
        self.areas = [
            {'name': "0北海道", 'url': "svcSD"},
            {'name': "1東北", 'url': "svcSE"},
            {'name': "2北信越", 'url': "svcSH"},
            {'name': "3関東", 'url': "svcSA"},
            {'name': "4東海", 'url': "svcSC"},
            {'name': "5中国", 'url': "svcSF"},
            {'name': "6関西", 'url': "svcSB"},
            {'name': "7四国", 'url': "svcSI"},
            {'name': "8九州沖縄", 'url': "svcSG"},
        ]

        self.categories = {
            'beauty':{'url1': "https://beauty.hotpepper.jp", 'url2': 'spkSP13_spdL035', 'url_length': 41},
            'relax': {'url1': "https://beauty.hotpepper.jp/relax", 'url2': 'grcGR01_spdL001', 'url_length': 44},
            'face':{ 'url1': "https://beauty.hotpepper.jp/esthe", 'url2': 'grcGR06_spdL040', 'url_length': 44},
            'body':{'url1': "https://beauty.hotpepper.jp/esthe", 'url2': 'grcGR06_spdL211', 'url_length': 44},
            'hair-loss':{'url1': "https://beauty.hotpepper.jp/esthe", 'url2': 'grcGR06_spdL116', 'url_length': 44},
        }
        self.category=self.categories[mode]
        self.mode = mode
        self.stores = []
        self.store_count = 1
        self.now = dt.datetime.now()
        self.now = self.now.strftime('%Y_%m_%d')
        os.makedirs(os.path.join('.', 'result_csv'), exist_ok=True)
        
    def count_pages_num(self, soup):
        row_text = soup.find(text=re.compile('\d+ページ')) 
        regex = re.compile('\d+')
        current_page_num, all_pages_num = regex.findall(row_text)
        return int(all_pages_num)
    
    def scrape_one_store(self, h3_tag, shop_area):
        a_tag = h3_tag.find("a")
        store_name = a_tag.text
        shop_url = a_tag.get('href').split('?')[0]
        html = requests.get(shop_url + 'tel')
        soup = BeautifulSoup(html.content, "html.parser")
        row_text = soup.find("td")
        tel = row_text.text.replace(u'\xa0', u'')
        store = {"area": shop_area, "name": store_name, "url": shop_url, "tel": tel}
        self.stores.append(store)
        
                
    def scrape_one_page(self, url):
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")
        h3_tags = soup.find_all("h3")
        titles = soup.find("title").text
        shop_area = titles.split('｜')[0]
        if len(shop_area) >= 5:
            for xs in ["北海道", "東北", "北信越", "関東", "東海", "中国", "関西", "四国", "九州・沖縄"]:
                if xs in shop_area:
                    shop_area = xs
        for i, h3_tag in enumerate(h3_tags):
            try:
                first_class_name = h3_tag.get("class").pop(0)
            except AttributeError:
                continue
            if first_class_name in ("slnName", "slcHead"):
                print('this is including store data!!', shop_area, self.store_count)
                self.scrape_one_store(h3_tag, shop_area)
                self.store_count += 1


    def main(self):
        for area in self.areas:
            base_url = f"{self.category['url1']}/{area['url']}/{self.category['url2']}"
            html = requests.get(base_url)
            soup = BeautifulSoup(html.content, "html.parser")
            pages_num = self.count_pages_num(soup)
            for page_num in range(1, pages_num+1):
                url = f"{base_url}/PN{page_num}.html?searchGender=ALL"
                self.scrape_one_page(url)
            df = pd.DataFrame(self.stores)
            df.to_csv(f"result_csv/HOTPEPPER_{self.mode}_{self.now}_{area['name']}.csv",encoding="utf-8-sig")
            self.stores = []


if __name__ == '__main__':
    hot_pepper_beauty = HotPepper('hair-loss')
    hot_pepper_beauty.main()
