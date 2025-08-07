from database import SessionLocal
from models import LottoDraw

db = SessionLocal()
try:
    count = db.query(LottoDraw).count()
    print(f"현재 수집된 데이터: {count}회")
    
    if count > 0:
        latest = db.query(LottoDraw).order_by(LottoDraw.draw_no.desc()).first()
        oldest = db.query(LottoDraw).order_by(LottoDraw.draw_no.asc()).first()
        print(f"범위: {oldest.draw_no}회 ~ {latest.draw_no}회")
        print(f"최신: {latest.draw_no}회 - {[latest.n1, latest.n2, latest.n3, latest.n4, latest.n5, latest.n6]} + {latest.bonus}")
        
        # 진행률 계산
        progress = (count / 1183) * 100
        print(f"전체 진행률: {progress:.1f}% ({count}/1183)")
finally:
    db.close()