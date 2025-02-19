from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
from urllib.parse import quote


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 탐지를 방지

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 검색어 및 링크
query = "RTX5090"
encoded_query = quote(query)  # 한글 URL 인코딩
url = f"https://search.shopping.naver.com/ns/search?query={encoded_query}"

print(f"검색 URL: {url}")
driver.get(url)

for _ in range(3):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(2)

# 데드락이나 무한 로딩에 빠지지않게
try:
    (WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.basicProductCard_link__urzND, a.miniProductCard_link__1X65D"))
    ))
except:
    print("⏳ 상품이 로드되지 않음. 크롤링 중단.")
    driver.quit()
    exit()

products = driver.find_elements(By.CSS_SELECTOR, "a.basicProductCard_link__urzND, a.miniProductCard_link__1X65D")
product_list = []

for product in products[:10]:  # 검색할 프러덕트 갯수
    try:
        # 광고 제거
        if "adcr.naver.com" in product.get_attribute("href"):
            print("광고 상품 스킵!!!!")
            continue

        # 제품 페이지 URL 긁어옴
        data_shp_contents_dtl = product.get_attribute("data-shp-contents-dtl")
        data_json = json.loads(data_shp_contents_dtl)

        name = next((item["value"] for item in data_json if item["key"] == "prod_nm"), "상품명 없음")
        price = next((item["value"] for item in data_json if item["key"] == "price"), "0")
        link = next((item["value"] for item in data_json if item["key"] == "click_url"), product.get_attribute("href"))  # 올바른 제품 링크 가져오기

        price = int(price.replace(",", ""))  # 가격을 정수로 변환

        # "렌탈"이 포함된 단어 제외
        if "렌탈" in name:
            print(f" '{name}' (렌탈 상품 제외됨!)")
            continue

        print(f"상품명: {name}")
        print(f"가격: {price:,}원")
        print(f"링크: {link}")
        print("-" * 50)

        product_list.append({"name": name, "price": price, "link": link})

    except Exception as e:
        continue

driver.quit()

# 최저가 상품 찾기
if product_list:
    lowest_product = sorted(product_list, key=lambda x: x["price"])[0]

    print("\n 최저가 상품 (렌탈 상품 제외)")
    print(f"상품명: {lowest_product['name']}")
    print(f"가격: {lowest_product['price']:,}원")
    print(f"구매 링크: {lowest_product['link']}")
else:
    print(" 검색 결과가 없습니다.")
