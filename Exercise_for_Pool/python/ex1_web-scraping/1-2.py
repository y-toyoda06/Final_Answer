from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

SLEEP_TIME = 3
MAX_RECORDS = 50

def get_store_urls(driver):
    #一覧ページから店舗リンク取得
    links = driver.find_elements(By.CSS_SELECTOR, "a.style_titleLink___TtTO")
    return [link.get_attribute("href") for link in links]

def parse_store_info(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)

    #店名
    try:
        name = driver.find_element(By.ID, "info-name").text
    except:
        name = ""
        
    #電話番号
    try:
        number = driver.find_element(By.CLASS_NAME, "number").text
    except:
        number = ""
    
    #住所
    try:
        address = driver.find_element(By.CLASS_NAME, "region").text
    except:
        address = ""
    
    
    #建物名
    try:
        building = driver.find_element(By.CLASS_NAME, "locality").text
    except:
        building = ""
        
    pref, city, addr = split_address(address)
    
        
    #お店のホームページをクリックしてURL取得
    #お店のホームページURLとSSL
    try:
        link = driver.find_element(By.CSS_SELECTOR, ".url.go-off")
        homepage = link.get_attribute("href")
        ssl = homepage.startswith("https://")
    except:
        homepage = ""
        ssl = "False"

        
    email =""
        
    return{
        "店舗名": name,
        "電話番号": number,
        "メールアドレス": email,
        "都道府県": pref,
        "市区町村": city,
        "番地": addr,
        "建物名": building,
        "URL": homepage,
        "SSL": ssl
    }
        
        
#住所を分割
def split_address(address):
    pattern = r"^(東京都|北海道|(?:京都|大阪)府|.{2,3}県)([^0-9]+)([\d\-]+)"
    match = re.match(pattern, address)
    if match:
        return match.group(1), match.group(2), match.group(3) or ""
    else:
        return "", "", ""

    
def main():
    base_url = "https://r.gnavi.co.jp/area/tokyo/izakaya/rs/"
    driver = webdriver.Chrome()
    driver.get(base_url)
    time.sleep(3)

    collected_data = []
    page_count = 1

    while len(collected_data) < MAX_RECORDS:
        print(f"\nページ {page_count} 開始 - URL: {driver.current_url}")

        # ストアURLの収集
        urls = get_store_urls(driver)
        print(f" 店舗URL取得：{len(urls)}件")


        for url in urls:
            if len(collected_data) >= MAX_RECORDS:
                break

            store_info = parse_store_info(driver, url)
            
            
            collected_data.append(store_info)
            print(f"done: {store_info['店舗名']}")
            
        if len(collected_data) >= MAX_RECORDS:
            break

        #「次へ」ボタン押す
        try:
            driver.get(base_url)
            time.sleep(SLEEP_TIME)
            next_btn = driver.find_element(By.XPATH, '//a[./img[contains(@alt, "次")]]')
            current_url = driver.current_url
            next_btn.click()
            time.sleep(SLEEP_TIME)
            base_url = driver.current_url
            
            if current_url == driver.current_url:
                print("ページ遷移失敗")
                break
            else:
                print(f"遷移：{current_url} → {base_url}")
                page_count += 1

        except:
            print("次のページが見つかりません")
            break

    print(f"総レコード数: {len(collected_data)} 件")
     #CSVに保存
    df = pd.DataFrame(collected_data,columns=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"])
    df.to_csv("1-2.csv", index=False, encoding="utf-8-sig")

    driver.quit()


if __name__ == "__main__":
    main()



