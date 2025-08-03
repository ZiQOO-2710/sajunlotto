from korean_lunar_calendar import KoreanLunarCalendar

# 천간/지지와 오행 매핑 테이블
GAN_OHEANG = {
    '갑': '목', '을': '목',
    '병': '화', '정': '화',
    '무': '토', '기': '토',
    '경': '금', '신': '금',
    '임': '수', '계': '수'
}

JI_OHEANG = {
    '자': '수', '축': '토',
    '인': '목', '묘': '목',
    '진': '토', '사': '화',
    '오': '화', '미': '토',
    '신': '금', '유': '금',
    '술': '토', '해': '수'
}

def analyze_saju(year: int, month: int, day: int, hour: int):
    """
    생년월일시를 바탕으로 사주팔자를 분석하고 오행 분포를 반환합니다.
    """
    calendar = KoreanLunarCalendar()
    calendar.setSolarDate(year, month, day)

    # 간지 문자열 가져오기 (예: "갑자년 을축월 병인일")
    gapja_string = calendar.getGapJaString()

    # 년주, 월주, 일주 파싱
    parts = gapja_string.split(' ')
    year_ganji_str = parts[0].replace('년', '')
    month_ganji_str = parts[1].replace('월', '')
    day_ganji_str = parts[2].replace('일', '')

    # 천간, 지지 분리
    year_gan = year_ganji_str[0]
    year_ji = year_ganji_str[1:]

    month_gan = month_ganji_str[0]
    month_ji = month_ganji_str[1:]

    day_gan = day_ganji_str[0]
    day_ji = day_ganji_str[1:]

    saju_palja = {
        'year': (year_gan, year_ji),
        'month': (month_gan, month_ji),
        'day': (day_gan, day_ji),
        # 'time': 시주 (추후 구현: 시주는 별도의 계산 로직이 필요합니다)
    }

    # 오행 분석
    oheang_distribution = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
    for gan, ji in saju_palja.values():
        if gan in GAN_OHEANG:
            oheang_distribution[GAN_OHEANG[gan]] += 1
        if ji in JI_OHEANG:
            oheang_distribution[JI_OHEANG[ji]] += 1

    return {
        'saju': saju_palja,
        'oheang': oheang_distribution
    }

if __name__ == '__main__':
    # 테스트용 코드
    test_year, test_month, test_day, test_hour = 1990, 5, 15, 10
    saju_result = analyze_saju(test_year, test_month, test_day, test_hour)

    print(f"입력 생년월일: {test_year}년 {test_month}월 {test_day}일 {test_hour}시")
    print("사주팔자:")
    for key, value in saju_result['saju'].items():
        print(f"  {key}: {value[0]}{value[1]}")
    print("오행 분포:")
    print(f"  {saju_result['oheang']}")