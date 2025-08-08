#!/usr/bin/env python3
"""
학습 시스템 상태 확인 스크립트
"""

import sqlite3
import subprocess
import os
from datetime import datetime

def check_processes():
    """실행 중인 학습 프로세스 확인"""
    print("🔄 실행 중인 학습 프로세스:")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            "ps aux | grep -E 'background_saju|youtube_learning|start_youtube' | grep -v grep",
            shell=True, capture_output=True, text=True
        )
        
        if result.stdout:
            processes = result.stdout.strip().split('\n')
            for proc in processes:
                parts = proc.split()
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                name = ' '.join(parts[10:])
                print(f"  ✅ PID: {pid} | CPU: {cpu}% | MEM: {mem}% | {name}")
        else:
            print("  ❌ 실행 중인 학습 프로세스 없음")
    except Exception as e:
        print(f"  ❌ 오류: {e}")

def check_database():
    """데이터베이스 상태 확인"""
    print("\n💾 데이터베이스 상태:")
    print("-" * 60)
    
    db_path = 'saju_knowledge_complete.db'
    
    if not os.path.exists(db_path):
        print(f"  ❌ 데이터베이스 파일 없음: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 전체 지식 수
        cursor.execute("SELECT COUNT(*) FROM saju_knowledge")
        total = cursor.fetchone()[0]
        print(f"  📚 총 학습된 지식: {total:,}개")
        
        # 지식 유형별 통계
        cursor.execute("""
            SELECT knowledge_type, COUNT(*) 
            FROM saju_knowledge 
            GROUP BY knowledge_type 
            ORDER BY COUNT(*) DESC
        """)
        
        print("\n  📊 지식 유형별 분포:")
        for row in cursor.fetchall():
            type_name = row[0] or 'general'
            count = row[1]
            print(f"    - {type_name}: {count:,}개")
        
        # 최근 학습 내용
        cursor.execute("""
            SELECT content, created_at 
            FROM saju_knowledge 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        print("\n  📝 최근 학습 내용:")
        for row in cursor.fetchall():
            content = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
            created = row[1]
            print(f"    [{created}] {content}")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ 데이터베이스 오류: {e}")

def check_logs():
    """로그 파일 확인"""
    print("\n📄 로그 파일 상태:")
    print("-" * 60)
    
    log_files = [
        'saju_learning.log',
        'youtube_learning_output.log',
        'saju_bg_learning.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
            print(f"  ✅ {log_file}: {size:.1f}KB | 수정: {mtime}")
        else:
            print(f"  ❌ {log_file}: 파일 없음")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎓 사주 학습 시스템 상태 확인")
    print("=" * 60)
    
    check_processes()
    check_database()
    check_logs()
    
    print("\n" + "=" * 60)
    print("💡 재부팅 후 재시작 명령어:")
    print("-" * 60)
    print("  1. 사주 학습: python3 background_saju_learning.py &")
    print("  2. 유튜브 학습: python3 start_youtube_learning.py &")
    print("  3. 상태 확인: python3 check_learning_status.py")
    print("=" * 60 + "\n")