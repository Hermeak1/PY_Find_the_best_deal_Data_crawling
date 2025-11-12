import requests
import re
from bs4 import BeautifulSoup

def parse_price(s):
    """가격 문자열에서 숫자만 추출"""
    n = re.sub(r"[^\d]", "", s or "")
    return int(n) if n else None

def crawl_danawa_gpu(keyword, limit=20):
    """다나와 그래픽카드(VGA) 카테고리 내에서 키워드 검색"""
    base_url = "https://search.danawa.com/dsearch.php"
    params = {
        "query": keyword,
        "tab": "main",
        "cate": "112753",  # 그래픽카드 카테고리 고정 (VGA)
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Referer": "https://search.danawa.com/",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    print(f"\n'{keyword}' 검색 중...\n")

    r = requests.get(base_url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for li in soup.select("div.main_prodlist ul.product_list > li"):
        # 광고/렌탈/악세사리 제외
        if li.select_one(".ad_header, .ad_info"):
            continue

        a = li.select_one("p.prod_name a, a.click_log_product_standard_title_")
        price_el = li.select_one(".price_sect strong, .price_real, .price_sect .num")

        if not a or not price_el:
            continue

        name = a.get_text(strip=True)
        price = parse_price(price_el.get_text(" ", strip=True))
        link = a.get("href") or ""

        if not price:
            continue
        if any(bad in name for bad in ["렌탈", "지지대", "브라켓", "쿨러", "워터", "케이스"]):
            continue

        items.append({"name": name, "price": price, "link": link})
        if len(items) >= limit:
            break

    if not items:
        print("검색 결과 없음 또는 구조 변경")
        return None, []

    items.sort(key=lambda x: x["price"])
    return items[0], items


if __name__ == "__main__":
    keyword = input("검색할 그래픽카드 모델명을 입력하세요 (예: RTX5090): ").strip()
    if not keyword:
        keyword = "RTX5090"

    best, items = crawl_danawa_gpu(keyword, limit=20)

    if best:
        print("최저가 (렌탈 제외)")
        print(f"상품명 : {best['name']}")
        print(f"가격   : {best['price']:,}원")
        print(f"링크   : {best['link']}")
        print("-" * 60)
        print("상위 5개 결과:")

        for i, it in enumerate(items[:5], start=1):
            print(f"{i}. {it['name']} - {it['price']:,}원")

        try:
            choice = int(input("\n열람할 상품 번호를 선택하세요 (1~5): "))
            if 1 <= choice <= min(5, len(items)):
                selected = items[choice - 1]
                print("\n선택한 상품 링크:")
                print(selected["link"])
            else:
                print("올바른 번호를 입력해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")
    else:
        print("검색 결과가 없습니다.")
