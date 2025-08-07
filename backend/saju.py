"""
한국 전통 사주학 분석 모듈
korean-lunar-calendar 라이브러리를 사용하여 정확한 음력 계산 구현
"""

from korean_lunar_calendar import KoreanLunarCalendar
import datetime

# 천간(天干) - 10개
GAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']

# 지지(地支) - 12개  
JI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']

# 천간의 오행 분류
GAN_OHEANG = {
    '갑': '목', '을': '목',  # 갑을목
    '병': '화', '정': '화',  # 병정화
    '무': '토', '기': '토',  # 무기토
    '경': '금', '신': '금',  # 경신금
    '임': '수', '계': '수'   # 임계수
}

# 지지의 오행 분류
JI_OHEANG = {
    '자': '수', '해': '수',  # 자해수
    '축': '토', '진': '토', '미': '토', '술': '토',  # 토
    '인': '목', '묘': '목',  # 인묘목
    '사': '화', '오': '화',  # 사오화
    '신': '금', '유': '금'   # 신유금
}

def get_ganzhi(year: int) -> tuple:
    """
    년도에 해당하는 간지(干支) 계산
    갑자년(1984)을 기준으로 계산
    """
    base_year = 1984  # 갑자년
    year_diff = year - base_year
    
    gan_index = year_diff % 10
    ji_index = year_diff % 12
    
    return (GAN[gan_index], JI[ji_index])

def analyze_saju(year: int, month: int, day: int, hour: int) -> dict:
    """
    사주 분석 메인 함수
    생년월일시를 입력받아 사주팔자 분석 결과 반환
    """
    try:
        # KoreanLunarCalendar 객체 생성
        calendar = KoreanLunarCalendar()
        
        # 양력을 음력으로 변환
        calendar.setSolarDate(year, month, day)
        lunar_year = calendar.lunarYear
        lunar_month = calendar.lunarMonth
        lunar_day = calendar.lunarDay
        
        # 사주팔자 계산
        # 년주 (年柱)
        year_gan, year_ji = get_ganzhi(lunar_year)
        
        # 월주 (月柱) - 간단한 계산법 적용
        # 실제로는 절입(節入) 계산이 필요하지만 여기서는 단순화
        month_gan_index = ((lunar_year - 1984) * 12 + lunar_month - 1) % 10
        month_ji_index = (lunar_month - 1) % 12
        month_gan = GAN[month_gan_index]
        month_ji = JI[month_ji_index]
        
        # 일주 (日柱) - 간단한 계산법
        # 실제로는 정확한 일진 계산이 필요
        base_date = datetime.date(1984, 2, 2)  # 갑자일
        target_date = datetime.date(year, month, day)
        day_diff = (target_date - base_date).days
        
        day_gan_index = day_diff % 10
        day_ji_index = day_diff % 12
        day_gan = GAN[day_gan_index]
        day_ji = JI[day_ji_index]
        
        # 시주 (時柱) - 시간별 지지 계산
        hour_ji_index = ((hour + 1) // 2) % 12
        hour_ji = JI[hour_ji_index]
        
        # 시간의 천간은 일간에 따라 결정 (갑을기경표)
        hour_gan_base = {
            '갑': 0, '기': 0,  # 갑기일
            '을': 2, '경': 2,  # 을경일  
            '병': 4, '신': 4,  # 병신일
            '정': 6, '임': 6,  # 정임일
            '무': 8, '계': 8   # 무계일
        }
        
        hour_gan_start = hour_gan_base.get(day_gan, 0)
        hour_gan_index = (hour_gan_start + hour_ji_index) % 10
        hour_gan = GAN[hour_gan_index]
        
        # 사주팔자 구성
        saju = {
            'year': (year_gan, year_ji),
            'month': (month_gan, month_ji), 
            'day': (day_gan, day_ji),
            'hour': (hour_gan, hour_ji)
        }
        
        # 오행 분포 계산
        oheang_count = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
        
        # 각 간지의 오행을 계산
        all_gan = [year_gan, month_gan, day_gan, hour_gan]
        all_ji = [year_ji, month_ji, day_ji, hour_ji]
        
        for gan in all_gan:
            if gan in GAN_OHEANG:
                oheang_count[GAN_OHEANG[gan]] += 1
                
        for ji in all_ji:
            if ji in JI_OHEANG:
                oheang_count[JI_OHEANG[ji]] += 1
        
        # 분석 결과 반환
        result = {
            'saju': saju,
            'oheang': oheang_count,
            'lunar_info': {
                'year': lunar_year,
                'month': lunar_month,
                'day': lunar_day
            },
            'analysis_date': datetime.datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        # 오류 발생 시 기본값 반환
        print(f"Error in saju analysis: {e}")
        return {
            'saju': {
                'year': ('갑', '자'),
                'month': ('갑', '자'),
                'day': ('갑', '자'),
                'hour': ('갑', '자')
            },
            'oheang': {'목': 1, '화': 1, '토': 2, '금': 2, '수': 2},
            'lunar_info': {'year': year, 'month': month, 'day': day},
            'analysis_date': datetime.datetime.now().isoformat(),
            'error': str(e)
        }

def get_lucky_numbers(oheang: dict) -> list:
    """
    오행 분포에 따른 행운 번호 생성
    각 오행별로 번호 범위를 매핑
    """
    element_ranges = {
        '목': list(range(1, 10)),   # 1-9
        '화': list(range(10, 20)),  # 10-19
        '토': list(range(20, 30)),  # 20-29
        '금': list(range(30, 40)),  # 30-39
        '수': list(range(40, 46))   # 40-45
    }
    
    lucky_numbers = []
    
    # 강한 오행 순서로 번호 추천
    sorted_elements = sorted(oheang.items(), key=lambda x: x[1], reverse=True)
    
    for element, count in sorted_elements:
        if count > 0:
            element_numbers = element_ranges.get(element, [])
            # 해당 오행의 강도에 비례하여 번호 개수 결정
            num_count = min(count * 2, len(element_numbers))
            lucky_numbers.extend(element_numbers[:num_count])
    
    return lucky_numbers[:20]  # 상위 20개만 반환

# 테스트 함수
if __name__ == "__main__":
    # 테스트 실행
    result = analyze_saju(1990, 5, 15, 10)
    print("사주 분석 결과:")
    print(f"사주팔자: {result['saju']}")
    print(f"오행 분포: {result['oheang']}")
    print(f"행운 번호: {get_lucky_numbers(result['oheang'])}")