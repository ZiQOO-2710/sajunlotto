#!/usr/bin/env python3
"""
로또 데이터 수집 스크립트
실제 동행복권 사이트에서 과거 로또 데이터를 수집하여 데이터베이스에 저장합니다.
"""

import time
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, LottoDraw
from crawler import get_lotto_numbers
import crud

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def collect_lotto_data(start_draw: int, end_draw: int, delay: float = 1.0):
    """
    지정된 범위의 로또 데이터를 수집합니다.
    
    Args:
        start_draw: 시작 회차
        end_draw: 종료 회차  
        delay: 요청 간 대기 시간 (초)
    """
    db = SessionLocal()
    success_count = 0
    error_count = 0
    
    try:
        print(f"로또 데이터 수집 시작: {start_draw}회 ~ {end_draw}회")
        print(f"요청 간격: {delay}초")
        print("-" * 50)
        
        for draw_no in range(start_draw, end_draw + 1):
            try:
                # 이미 존재하는 회차는 건너뛰기
                existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
                if existing:
                    print(f"[SKIP] {draw_no}회: 이미 존재함")
                    continue
                
                # 로또 데이터 크롤링
                print(f"[CRAWL] {draw_no}회 크롤링 중...", end=" ")
                lotto_data = get_lotto_numbers(draw_no)
                
                if lotto_data:
                    # 데이터베이스에 저장
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
                    
                    print(f"[SUCCESS] 저장완료: {lotto_data['win_numbers']} + {lotto_data['bonus_number']}")
                    success_count += 1
                else:
                    print(f"[ERROR] 크롤링 실패")
                    error_count += 1
                
                # 요청 간 대기
                time.sleep(delay)
                
            except Exception as e:
                print(f"[ERROR] {draw_no}회 오류: {str(e)}")
                error_count += 1
                continue
        
        print("-" * 50)
        print(f"수집 완료!")
        print(f"성공: {success_count}회")
        print(f"실패: {error_count}회")
        
    except Exception as e:
        print(f"전체 오류: {str(e)}")
    finally:
        db.close()

def check_collected_data():
    """수집된 데이터 확인"""
    db = SessionLocal()
    try:
        count = db.query(LottoDraw).count()
        latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
        
        print(f"수집된 데이터 현황:")
        print(f"   총 회차: {count}회")
        if oldest and latest:
            print(f"   범위: {oldest.draw_no}회 ~ {latest.draw_no}회")
            print(f"   최신: {latest.draw_no}회 [{latest.n1}, {latest.n2}, {latest.n3}, {latest.n4}, {latest.n5}, {latest.n6}] + {latest.bonus}")
        
    finally:
        db.close()

if __name__ == "__main__":
    # 데이터베이스 테이블 생성
    create_tables()
    
    # 현재 수집된 데이터 확인
    check_collected_data()
    
    # 사용자 입력 받기
    if len(sys.argv) >= 3:
        start_draw = int(sys.argv[1])
        end_draw = int(sys.argv[2])
    else:
        print("\n로또 데이터 수집 범위를 입력하세요:")
        start_draw = int(input("시작 회차: ") or "1050")
        end_draw = int(input("종료 회차: ") or "1100")
    
    # 데이터 수집 실행
    collect_lotto_data(start_draw, end_draw, delay=1.5)
    
    # 수집 후 데이터 확인
    print("\n" + "="*50)
    check_collected_data()