#!/usr/bin/env python3
"""
대용량 로또 데이터 수집 스크립트
1회부터 최신회차까지 모든 로또 데이터를 효율적으로 수집합니다.
"""

import time
import sys
import json
from datetime import datetime
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, LottoDraw
from crawler import get_lotto_numbers
import crud

class MassLottoCrawler:
    """대용량 로또 데이터 크롤링 클래스"""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 5, delay: float = 0.5):
        """
        초기화
        
        Args:
            batch_size: 배치 단위 (한 번에 처리할 회차 수)
            max_workers: 동시 처리 스레드 수
            delay: 요청 간 대기 시간 (초)
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.delay = delay
        self.success_count = 0
        self.error_count = 0
        self.skip_count = 0
        
    def create_tables(self):
        """데이터베이스 테이블 생성"""
        Base.metadata.create_all(bind=engine)
        print("[OK] 데이터베이스 테이블이 생성되었습니다.")
    
    def check_existing_data(self, db: Session) -> Dict[str, int]:
        """현재 수집된 데이터 확인"""
        count = db.query(LottoDraw).count()
        latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
        
        missing_ranges = []
        if count > 0 and oldest and latest:
            # 빈 구간 찾기
            all_draws = db.query(LottoDraw.draw_no).order_by(LottoDraw.draw_no).all()
            existing_draws = set(draw[0] for draw in all_draws)
            
            for i in range(oldest.draw_no, latest.draw_no + 1):
                if i not in existing_draws:
                    missing_ranges.append(i)
        
        return {
            'total_count': count,
            'oldest_draw': oldest.draw_no if oldest else 0,
            'latest_draw': latest.draw_no if latest else 0,
            'missing_ranges': missing_ranges
        }
    
    def crawl_single_draw(self, draw_no: int) -> Optional[Dict]:
        """단일 회차 크롤링"""
        try:
            db = SessionLocal()
            
            # 이미 존재하는지 확인
            existing = db.query(LottoDraw).filter(LottoDraw.draw_no == draw_no).first()
            if existing:
                db.close()
                return {"status": "skip", "draw_no": draw_no, "message": "이미 존재함"}
            
            # 크롤링 실행
            lotto_data = get_lotto_numbers(draw_no)
            
            if lotto_data:
                try:
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
                    
                    return {
                        "status": "success", 
                        "draw_no": draw_no, 
                        "numbers": lotto_data['win_numbers'],
                        "bonus": lotto_data['bonus_number']
                    }
                except Exception as e:
                    db.rollback()
                    return {"status": "error", "draw_no": draw_no, "message": f"DB 저장 오류: {str(e)}"}
            else:
                return {"status": "error", "draw_no": draw_no, "message": "크롤링 실패"}
                
        except Exception as e:
            return {"status": "error", "draw_no": draw_no, "message": str(e)}
        finally:
            db.close()
            time.sleep(self.delay)  # 요청 간 대기
    
    def crawl_batch(self, draw_numbers: List[int]) -> List[Dict]:
        """배치 단위로 크롤링 실행"""
        results = []
        
        # 순차 처리 (서버 부하 고려)
        for draw_no in draw_numbers:
            result = self.crawl_single_draw(draw_no)
            results.append(result)
            
            # 진행상황 출력
            if result["status"] == "success":
                print(f"[SUCCESS] {draw_no}회: {result['numbers']} + {result['bonus']}")
                self.success_count += 1
            elif result["status"] == "skip":
                print(f"[SKIP] {draw_no}회: 이미 존재함")
                self.skip_count += 1
            else:
                print(f"[ERROR] {draw_no}회: {result['message']}")
                self.error_count += 1
        
        return results
    
    def collect_all_data(self, start_draw: int = 1, end_draw: int = 1183):
        """전체 데이터 수집"""
        print("대용량 로또 데이터 수집 시작!")
        print(f"수집 범위: {start_draw}회 ~ {end_draw}회 (총 {end_draw - start_draw + 1}회차)")
        print(f"설정: 배치크기={self.batch_size}, 지연시간={self.delay}초")
        print("="*70)
        
        # 기존 데이터 확인
        db = SessionLocal()
        data_info = self.check_existing_data(db)
        print(f"현재 수집된 데이터: {data_info['total_count']}회")
        if data_info['total_count'] > 0:
            print(f"범위: {data_info['oldest_draw']}회 ~ {data_info['latest_draw']}회")
            if data_info['missing_ranges']:
                print(f"누락된 회차: {len(data_info['missing_ranges'])}개")
        db.close()
        
        print("-"*70)
        
        # 수집할 회차 리스트 생성
        total_draws = list(range(start_draw, end_draw + 1))
        total_batches = (len(total_draws) + self.batch_size - 1) // self.batch_size
        
        start_time = time.time()
        
        # 배치별로 처리
        for batch_idx in range(total_batches):
            batch_start = batch_idx * self.batch_size
            batch_end = min(batch_start + self.batch_size, len(total_draws))
            batch_draws = total_draws[batch_start:batch_end]
            
            print(f"\n📦 배치 {batch_idx + 1}/{total_batches}: {batch_draws[0]}회~{batch_draws[-1]}회")
            print("-"*50)
            
            # 배치 크롤링 실행
            batch_results = self.crawl_batch(batch_draws)
            
            # 배치 결과 요약
            batch_success = sum(1 for r in batch_results if r["status"] == "success")
            batch_skip = sum(1 for r in batch_results if r["status"] == "skip")  
            batch_error = sum(1 for r in batch_results if r["status"] == "error")
            
            print(f"📋 배치 {batch_idx + 1} 결과: 성공={batch_success}, 건너뜀={batch_skip}, 오류={batch_error}")
            
            # 진행률 출력
            processed = (batch_idx + 1) * self.batch_size
            total = len(total_draws)
            progress = min(100.0, (processed / total) * 100)
            elapsed = time.time() - start_time
            
            if batch_idx > 0:  # 첫 번째 배치 이후 예상시간 계산
                estimated_total = elapsed * total_batches / (batch_idx + 1)
                remaining = estimated_total - elapsed
                print(f"⏱️ 진행률: {progress:.1f}% | 경과: {elapsed:.1f}초 | 예상 남은 시간: {remaining:.1f}초")
            
            # 배치 간 휴식 (서버 부하 방지)
            if batch_idx < total_batches - 1:
                print(f"😴 다음 배치까지 {self.delay * 2}초 대기...")
                time.sleep(self.delay * 2)
        
        # 최종 결과 출력
        total_time = time.time() - start_time
        print("\n" + "="*70)
        print("🎉 대용량 로또 데이터 수집 완료!")
        print(f"⏱️ 총 소요시간: {total_time:.1f}초 ({total_time/60:.1f}분)")
        print(f"📊 최종 결과:")
        print(f"   ✅ 성공: {self.success_count}회")
        print(f"   ⏭️ 건너뜀: {self.skip_count}회 (이미 존재)")
        print(f"   ❌ 오류: {self.error_count}회")
        print(f"   📈 총 처리: {self.success_count + self.skip_count + self.error_count}회")
        
        # 최종 데이터 확인
        self.final_data_check()
    
    def final_data_check(self):
        """최종 데이터 확인"""
        db = SessionLocal()
        try:
            count = db.query(LottoDraw).count()
            latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
            oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
            
            print("\n" + "="*50)
            print("📊 최종 데이터베이스 현황")
            print("="*50)
            print(f"📈 총 수집된 회차: {count}회")
            if oldest and latest:
                print(f"📅 수집 범위: {oldest.draw_no}회 ~ {latest.draw_no}회")
                print(f"🎲 최신 데이터: {latest.draw_no}회")
                print(f"   당첨번호: [{latest.n1}, {latest.n2}, {latest.n3}, {latest.n4}, {latest.n5}, {latest.n6}]")
                print(f"   보너스번호: {latest.bonus}")
                print(f"   추첨일: {latest.draw_date}")
            
            # 누락된 회차 확인
            if count > 0:
                all_draws = db.query(LottoDraw.draw_no).order_by(LottoDraw.draw_no).all()
                existing_draws = set(draw[0] for draw in all_draws)
                expected_draws = set(range(oldest.draw_no, latest.draw_no + 1))
                missing_draws = expected_draws - existing_draws
                
                if missing_draws:
                    print(f"⚠️ 누락된 회차: {len(missing_draws)}개")
                    if len(missing_draws) <= 10:
                        print(f"   누락 목록: {sorted(list(missing_draws))}")
                    else:
                        missing_list = sorted(list(missing_draws))
                        print(f"   누락 목록(일부): {missing_list[:10]}... (총 {len(missing_draws)}개)")
                else:
                    print("✅ 누락된 회차 없음 - 완벽한 데이터 수집!")
            
        finally:
            db.close()

def main():
    """메인 함수"""
    crawler = MassLottoCrawler(
        batch_size=50,    # 50개씩 배치 처리
        max_workers=1,    # 순차 처리 (서버 부하 방지)
        delay=0.8        # 0.8초 대기
    )
    
    # 테이블 생성
    crawler.create_tables()
    
    # 전체 데이터 수집 (1회 ~ 1183회)
    crawler.collect_all_data(start_draw=1, end_draw=1183)

if __name__ == "__main__":
    main()