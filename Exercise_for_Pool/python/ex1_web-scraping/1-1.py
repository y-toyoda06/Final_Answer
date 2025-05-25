import random
from bs4 import BeautifulSoup
import requests
import time
import re
import pandas as pd

#ユーザーエージェントの設定
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
]
random_user_agent = random.choice(user_agents)
headers = {
    'user-agent': random_user_agent
}

SLEEP_TIME = 3
MAX_RECORDS = 50


#指定URLから1ページ分のリンクを取得
def get_url(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    elems = soup.find_all("a", class_="style_titleLink___TtTO")
    links = [elem.attrs['href'] for elem in elems if '?' not in elem.attrs['href']]
    return links

#ページをまたいで50件リンクを収集
def collect_urls(base_url, max_records):
    page = 1
    urls = []

    while len(urls) < max_records:
        url = base_url if page == 1 else f"{base_url}?p={page}"
        print(f"ページ {page} を取得中")
        links = get_url(url)

        if not links:
            print("これ以上リンクが見つかりません．")
            break

        urls.extend(links)
        page += 1
        time.sleep(SLEEP_TIME)

    return urls[:max_records]



def get_store_info(url):
    time.sleep(SLEEP_TIME)
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")
    
    #店舗名
    name_tag = soup.find("p", id="info-name")
    name = name_tag.get_text(strip=True) if name_tag else ""
    
    #電話番号
    number_tag = soup.find("span", class_="number")
    number = number_tag.get_text(strip=True) if number_tag else ""
    
    #メールアドレス(見つけられず)
    #email_tag = soup.find()
    #email = email_tag.get_text(strip=True) if number_tag else ""
    email = ""
    
    #住所
    address_tag = soup.find("span", class_="region" )
    address = address_tag.get_text(strip=True) if address_tag else ""
    
    building_tag = soup.find("span", class_="locality" )
    building = building_tag.get_text(strip=True) if building_tag else ""
    
    #住所分割
    pref, city, addr = split_address(address)
    
    #ulrは空白でsslはfalse(仕様)
    url = ""
    ssl = False    
    
    return{
        "店舗名": name,
        "電話番号": number,
        "メールアドレス": email,
        "都道府県": pref,
        "市区町村": city,
        "番地": addr,
        "建物名": building,
        "URL": url,
        "SSL": ssl
    }
    
# 住所を分割
def split_address(address):
    pattern = r"^(東京都|北海道|(?:京都|大阪)府|.{2,3}県)([^0-9]+)([\d\-]+)"
    match = re.match(pattern, address)
    if match:
        return match.group(1), match.group(2), match.group(3) or ""
    else:
        return "", "", ""
    
    

def main():
    base_url = "https://r.gnavi.co.jp/area/tokyo/izakaya/rs/"
    urls = collect_urls(base_url, MAX_RECORDS)
    store_info = []

    for url in urls:
        store_info.append(get_store_info(url))
        print(f"done: {url}")
        
        
    df = pd.DataFrame(store_info,columns=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"])
    df.to_csv("1-1.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()