import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from . import crud

def get_lotto_numbers(draw_no: int):
    """
    동행복권 웹사이트에서 특정 회차의 로또 당첨 번호를 가져옵니다.
    """
    url = f"https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={draw_no}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 요청 실패 시 예외 발생
    except requests.exceptions.RequestException as e:
        print(f"Error fetching draw {draw_no}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    win_result = soup.select_one("div.win_result")
    if not win_result:
        return None

    win_nums_div = win_result.select_one("div.num.win")
    if not win_nums_div:
        return None
    win_nums = [int(num.text) for num in win_nums_div.select("span")]

    bonus_num_div = win_result.select_one("div.num.bonus")
    if not bonus_num_div:
        return None
    bonus_num = int(bonus_num_div.select_one("span").text)

    desc_p = soup.select_one("p.desc")
    if not desc_p:
        return None
    draw_date_str = desc_p.text.replace("(", "").replace(")", "").replace("추첨", "").strip()

    return {
        "draw_no": draw_no,
        "draw_date": draw_date_str,
        "win_numbers": win_nums,
        "bonus_number": bonus_num
    }

def crawl_and_save_lotto_draw(db: Session, draw_no: int):
    """
    특정 회차의 로또 번호를 크롤링하고 DB에 저장합니다.
    이미 존재하는 경우 건너뜁니다.
    """
    if crud.get_lotto_draw(db, draw_no=draw_no):
        return None  # 이미 존재하면 아무것도 하지 않음

    lotto_data = get_lotto_numbers(draw_no)
    if not lotto_data:
        return None  # 크롤링 실패

    return crud.create_lotto_draw(db, lotto_data=lotto_data)
