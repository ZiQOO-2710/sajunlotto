#!/usr/bin/env python3
"""
간단한 YouTube 학습 시스템
YouTubeService를 래핑하여 간편하게 사용할 수 있도록 함
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class SimpleYouTubeLearner:
    """YouTube 크롤링 및 학습 시스템 간소화 버전"""
    
    def __init__(self, db_path: str = "saju_knowledge_complete.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 필요한 테이블이 없으면 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saju_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                content TEXT,
                knowledge_type TEXT,
                confidence REAL DEFAULT 0.5,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def search_learned_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """
        학습된 지식 검색
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        try:
            cursor.execute('''
                SELECT content, knowledge_type, confidence, metadata
                FROM saju_knowledge
                WHERE content LIKE ?
                ORDER BY confidence DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            rows = cursor.fetchall()
            for row in rows:
                results.append({
                    'content': row[0],
                    'type': row[1],
                    'confidence': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {}
                })
        except Exception as e:
            print(f"[ERROR] 지식 검색 중 오류: {e}")
        finally:
            conn.close()
        
        return results
    
    def add_knowledge(self, content: str, knowledge_type: str = "general", 
                     source: str = "youtube", confidence: float = 0.5,
                     metadata: Optional[Dict] = None):
        """
        새로운 지식 추가
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO saju_knowledge (source, content, knowledge_type, confidence, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (source, content, knowledge_type, confidence, 
                  json.dumps(metadata) if metadata else "{}"))
            
            conn.commit()
            print(f"[SUCCESS] 새로운 지식 추가됨: {content[:50]}...")
        except Exception as e:
            print(f"[ERROR] 지식 추가 중 오류: {e}")
        finally:
            conn.close()
    
    def get_knowledge_count(self) -> int:
        """
        저장된 지식 개수 반환
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM saju_knowledge")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_recent_knowledge(self, limit: int = 10) -> List[Dict]:
        """
        최근 학습된 지식 반환
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, knowledge_type, confidence, created_at
            FROM saju_knowledge
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'content': row[0],
                'type': row[1],
                'confidence': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return results


if __name__ == "__main__":
    # 테스트
    learner = SimpleYouTubeLearner()
    print(f"현재 저장된 지식 수: {learner.get_knowledge_count()}개")
    
    # 테스트 지식 추가
    learner.add_knowledge(
        "경인년생은 백호의 해로 강한 의지와 리더십을 가진다",
        knowledge_type="띠별특성",
        confidence=0.8
    )
    
    # 최근 지식 조회
    recent = learner.get_recent_knowledge(5)
    print(f"최근 학습 내용: {len(recent)}개")