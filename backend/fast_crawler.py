#!/usr/bin/env python3
"""
빠른 로또 데이터 수집 - 누락된 회차만 병렬 처리
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from database import SessionLocal, engine
from models import Base, LottoDraw
from crawler import get_lotto_numbers

def get_missing_draws():
    """누락된 회차 찾기"""
    db = SessionLocal()
    try:
        # 모든 기존 회차 조회
        existing_draws = set(row[0] for row in db.query(LottoDraw.draw_no).all())
        
        # 1~1183 중 누락된 회차 찾기
        all_draws = set(range(1, 1184))
        missing_draws = sorted(list(all_draws - existing_draws))
        
        print(f"누락된 회차: {len(missing_draws)}개")
        if len(missing_draws) <= 20:
            print(f"누락 목록: {missing_draws}")
        else:
            print(f"누락 범위: {missing_draws[0]}~{missing_draws[-1]} (일부 중간 구간 포함)")
        
        return missing_draws
    finally:
        db.close()

def crawl_batch_parallel(draw_numbers, max_workers=3):
    """병렬 배치 크롤링"""
    results = []
    success = 0
    errors = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 작업 제출
        future_to_draw = {
            executor.submit(crawl_and_save_draw, draw_no): draw_no 
            for draw_no in draw_numbers
        }
        
        # 결과 처리
        for future in as_completed(future_to_draw):
            draw_no = future_to_draw[future]
            try:
                result = future.result()
                if result:
                    print(f"[SUCCESS] {draw_no}회: {result}")
                    success += 1
                else:
                    print(f"[ERROR] {draw_no}회: 크롤링 실패")
                    errors += 1
            except Exception as e:
                print(f"[ERROR] {draw_no}회: {str(e)}")
                errors += 1
            
            # 요청 간 지연
            time.sleep(0.3)
    
    return success, errors

def crawl_and_save_draw(draw_no):
    """단일 회차 크롤링 및 저장"""
    try:
        lotto_data = get_lotto_numbers(draw_no)
        if not lotto_data:
            return None
        
        db = SessionLocal()
        try:
            # 중복 확인
            existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
            if existing:
                return f"SKIP - 이미 존재"
            
            # 저장
            lotto_draw = LottoDraw(
                draw_no=lotto_data['draw_no'],
                draw_date=datetime.strptime(lotto_data['draw_date'], '%Y년 %m월 %d일'),
                n1=lotto_data['win_numbers'][0],
                n2=lotto_data['win_numbers'][1], 
                n3=lotto_data['win_numbers'][2],
                n4=lotto_data['win_numbers'][3],
                n5=lotto_data['win_numbers'][4],
                n6=lotto_data['win_numbers'][5],
                bonus=lotto_data['bonus_number']
            )
            
            db.add(lotto_draw)
            db.commit()
            
            return f"{lotto_data['win_numbers']} + {lotto_data['bonus_number']}"
            
        finally:
            db.close()
            
    except Exception as e:
        return None

def fast_collect_missing():
    """누락된 데이터만 빠르게 수집"""
    print("="*60)
    print("빠른 로또 데이터 수집 - 누락된 회차만")
    print("="*60)
    
    missing_draws = get_missing_draws()
    
    if not missing_draws:
        print("모든 데이터가 수집되었습니다!")
        return
    
    print(f"\n총 {len(missing_draws)}개 회차를 수집합니다.")
    print("병렬 처리로 빠르게 수집 중...")
    print("-"*60)
    
    # 배치 크기 설정
    batch_size = 30  # 30개씩 처리
    total_batches = (len(missing_draws) + batch_size - 1) // batch_size
    
    total_success = 0
    total_errors = 0
    start_time = time.time()
    
    for i in range(0, len(missing_draws), batch_size):
        batch = missing_draws[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n배치 {batch_num}/{total_batches}: {batch[0]}~{batch[-1]}회")
        print("-"*30)
        
        batch_success, batch_errors = crawl_batch_parallel(batch, max_workers=3)
        total_success += batch_success
        total_errors += batch_errors
        
        print(f"배치 결과: 성공={batch_success}, 오류={batch_errors}")
        
        # 진행률 출력
        processed = min(i + batch_size, len(missing_draws))
        progress = (processed / len(missing_draws)) * 100
        elapsed = time.time() - start_time
        
        if processed > 0:
            avg_time = elapsed / processed
            remaining = (len(missing_draws) - processed) * avg_time
            print(f"진행률: {progress:.1f}% | 경과: {elapsed:.1f}초 | 예상 남은 시간: {remaining:.1f}초")
        
        # 배치 간 휴식
        if batch_num < total_batches:
            print("다음 배치까지 2초 대기...")
            time.sleep(2)
    
    # 최종 결과
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("빠른 수집 완료!")
    print(f"소요시간: {total_time:.1f}초 ({total_time/60:.1f}분)")
    print(f"성공: {total_success}회")
    print(f"오류: {total_errors}회")
    
    # 최종 확인
    final_check()

def final_check():
    """최종 데이터 확인"""
    db = SessionLocal()
    try:
        count = db.query(LottoDraw).count()
        latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
        
        print(f"\n최종 데이터베이스 현황:")
        print(f"총 수집된 회차: {count}회")
        print(f"전체 진행률: {(count/1183)*100:.1f}% ({count}/1183)")
        
        if oldest and latest:
            print(f"범위: {oldest.draw_no}회 ~ {latest.draw_no}회")
            
        # 완성도 확인
        if count == 1183:
            print("🎉 완벽한 데이터 수집 완료! 1~1183회 모든 데이터가 수집되었습니다!")
        else:
            missing = get_missing_draws()
            print(f"아직 {len(missing)}개 회차가 누락되었습니다.")
        
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    fast_collect_missing()