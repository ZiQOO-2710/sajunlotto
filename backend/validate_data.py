#!/usr/bin/env python3
"""
수집된 로또 데이터 상세 검증
"""

from database import SessionLocal
from models import LottoDraw
from collections import Counter

def validate_complete_data():
    """완전한 데이터 검증"""
    db = SessionLocal()
    try:
        print("="*60)
        print("로또 데이터 상세 검증")
        print("="*60)
        
        # 1. 기본 통계
        total_count = db.query(LottoDraw).count()
        latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
        
        print(f"총 수집된 회차: {total_count}회")
        print(f"수집 범위: {oldest.draw_no}회 ~ {latest.draw_no}회")
        print(f"완성도: {(total_count/1183)*100:.1f}%")
        
        # 2. 누락된 회차 확인
        all_draws = db.query(LottoDraw.draw_no).order_by(LottoDraw.draw_no).all()
        existing_draws = set(draw[0] for draw in all_draws)
        expected_draws = set(range(1, 1184))
        missing_draws = expected_draws - existing_draws
        
        if missing_draws:
            print(f"\n⚠️ 누락된 회차: {len(missing_draws)}개")
            print(f"누락 목록: {sorted(list(missing_draws))}")
        else:
            print(f"\n✅ 완벽한 수집! 누락된 회차 없음")
        
        # 3. 데이터 품질 검증
        print(f"\n데이터 품질 검증:")
        
        # 중복 검사
        duplicates = db.execute("""
            SELECT draw_no, COUNT(*) 
            FROM lotto_draws 
            GROUP BY draw_no 
            HAVING COUNT(*) > 1
        """).fetchall()
        
        if duplicates:
            print(f"❌ 중복된 회차: {len(duplicates)}개")
            for draw_no, count in duplicates:
                print(f"   {draw_no}회: {count}개 중복")
        else:
            print(f"✅ 중복 없음")
        
        # 번호 범위 검증
        invalid_numbers = db.execute("""
            SELECT draw_no, n1, n2, n3, n4, n5, n6, bonus
            FROM lotto_draws 
            WHERE n1 < 1 OR n1 > 45 OR n2 < 1 OR n2 > 45 OR n3 < 1 OR n3 > 45 
               OR n4 < 1 OR n4 > 45 OR n5 < 1 OR n5 > 45 OR n6 < 1 OR n6 > 45
               OR bonus < 1 OR bonus > 45
        """).fetchall()
        
        if invalid_numbers:
            print(f"❌ 잘못된 번호 범위: {len(invalid_numbers)}개")
        else:
            print(f"✅ 모든 번호가 1-45 범위 내")
        
        # 중복 번호 검증 (한 회차 내)
        invalid_duplicates = db.execute("""
            SELECT draw_no, n1, n2, n3, n4, n5, n6, bonus
            FROM lotto_draws 
            WHERE n1 = n2 OR n1 = n3 OR n1 = n4 OR n1 = n5 OR n1 = n6 OR n1 = bonus
               OR n2 = n3 OR n2 = n4 OR n2 = n5 OR n2 = n6 OR n2 = bonus
               OR n3 = n4 OR n3 = n5 OR n3 = n6 OR n3 = bonus
               OR n4 = n5 OR n4 = n6 OR n4 = bonus
               OR n5 = n6 OR n5 = bonus
               OR n6 = bonus
        """).fetchall()
        
        if invalid_duplicates:
            print(f"❌ 회차 내 중복 번호: {len(invalid_duplicates)}개")
        else:
            print(f"✅ 회차 내 중복 번호 없음")
        
        # 4. 번호 통계 분석
        print(f"\n번호 통계 분석:")
        
        # 가장 많이 나온 번호
        all_numbers = []
        for draw in db.query(LottoDraw).all():
            all_numbers.extend([draw.n1, draw.n2, draw.n3, draw.n4, draw.n5, draw.n6])
        
        number_counts = Counter(all_numbers)
        most_common = number_counts.most_common(5)
        
        print(f"가장 많이 나온 번호 TOP 5:")
        for number, count in most_common:
            percentage = (count / total_count) * 100
            print(f"   {number}번: {count}회 ({percentage:.1f}%)")
        
        # 보너스 번호 통계
        bonus_numbers = [draw.bonus for draw in db.query(LottoDraw).all()]
        bonus_counts = Counter(bonus_numbers)
        most_common_bonus = bonus_counts.most_common(3)
        
        print(f"\n가장 많이 나온 보너스 번호 TOP 3:")
        for number, count in most_common_bonus:
            percentage = (count / total_count) * 100
            print(f"   {number}번: {count}회 ({percentage:.1f}%)")
        
        # 5. 시기별 분석
        print(f"\n시기별 데이터:")
        decade_stats = db.execute("""
            SELECT 
                CASE 
                    WHEN draw_no BETWEEN 1 AND 100 THEN '초기(1-100회)'
                    WHEN draw_no BETWEEN 101 AND 500 THEN '중기(101-500회)'
                    WHEN draw_no BETWEEN 501 AND 1000 THEN '후기(501-1000회)'
                    ELSE '최신(1001-1183회)'
                END as period,
                COUNT(*) as count
            FROM lotto_draws 
            GROUP BY period
        """).fetchall()
        
        for period, count in decade_stats:
            print(f"   {period}: {count}회")
        
        # 6. 최종 요약
        print(f"\n" + "="*60)
        print(f"데이터 수집 최종 요약")
        print(f"="*60)
        if total_count == 1183 and not missing_draws and not duplicates and not invalid_numbers:
            print(f"🎉 완벽한 데이터 수집 성공!")
            print(f"   ✅ 전체 1,183회차 완전 수집")
            print(f"   ✅ 누락 없음")
            print(f"   ✅ 중복 없음")
            print(f"   ✅ 데이터 무결성 확인")
            print(f"   ✅ 1회(2002년) ~ 1183회(2025년) 전체 로또 히스토리 확보")
        else:
            print(f"⚠️ 데이터 수집에 일부 문제가 있습니다.")
            
        return total_count == 1183 and not missing_draws
        
    finally:
        db.close()

if __name__ == "__main__":
    is_complete = validate_complete_data()
    if is_complete:
        print(f"\n✅ 로또 데이터 수집이 완벽하게 완료되었습니다!")
        print(f"이제 머신러닝 모델 학습에 사용할 수 있습니다.")