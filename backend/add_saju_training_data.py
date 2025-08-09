#!/usr/bin/env python3
"""
사주 학습 데이터 직접 추가 스크립트
전문가 수준의 사주 해석 데이터를 지식베이스에 추가
"""

import sqlite3
import json
from datetime import datetime

class SajuTrainingDataAdder:
    """사주 학습 데이터 추가기"""
    
    def __init__(self):
        self.knowledge_db = 'saju_knowledge_complete.db'
        
        # 전문가 수준의 사주 해석 데이터
        self.training_data = [
            # 갑목 일주 관련
            {
                "content": "갑목 일주는 큰 나무의 기운을 가진 사람입니다. 리더십이 강하고 정직하며 포용력이 있습니다. 다른 사람을 이끄는 능력이 뛰어나고 의리를 중시합니다.",
                "saju_terms": {"천간": ["갑"], "오행": ["목"], "성격": ["성격"]},
                "sentence_type": "personality",
                "confidence": 0.95
            },
            {
                "content": "갑목 일주 사람은 봄철에 태어나면 더욱 왕성한 에너지를 발휘합니다. 사업가나 리더 역할에 적합하며 많은 사람들의 신뢰를 받습니다.",
                "saju_terms": {"천간": ["갑"], "오행": ["목"], "직업": ["사업"]},
                "sentence_type": "interpretation",
                "confidence": 0.90
            },
            
            # 을목 일주 관련
            {
                "content": "을목 일주는 작은 나무, 풀의 기운으로 섬세하고 예술적 감각이 뛰어납니다. 적응력이 좋고 부드러운 성격으로 사람들과 잘 어울립니다.",
                "saju_terms": {"천간": ["을"], "오행": ["목"], "성격": ["성격"]},
                "sentence_type": "personality", 
                "confidence": 0.93
            },
            
            # 병화 일주 관련
            {
                "content": "병화 일주는 태양의 기운을 가진 사람으로 밝고 활발한 성격입니다. 표현력이 좋고 사교적이며 많은 사람들에게 에너지를 줍니다.",
                "saju_terms": {"천간": ["병"], "오행": ["화"], "성격": ["성격"]},
                "sentence_type": "personality",
                "confidence": 0.92
            },
            
            # 정화 일주 관련
            {
                "content": "정화 일주는 촛불의 기운으로 따뜻하고 정이 많습니다. 예술 분야나 서비스업에 재능이 있으며 감성이 풍부합니다.",
                "saju_terms": {"천간": ["정"], "오행": ["화"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.91
            },
            
            # 무토 일주 관련
            {
                "content": "무토 일주는 산의 기운을 가진 사람으로 든든하고 안정적입니다. 책임감이 강하고 신뢰할 수 있으며 꾸준한 노력으로 성과를 이룹니다.",
                "saju_terms": {"천간": ["무"], "오행": ["토"], "성격": ["성격"]},
                "sentence_type": "personality",
                "confidence": 0.94
            },
            
            # 기토 일주 관련  
            {
                "content": "기토 일주는 들판의 흙 기운으로 포용력이 크고 따뜻한 마음을 가졌습니다. 농업이나 요리 분야에 재능이 있고 사람들을 돌보는 일에 적합합니다.",
                "saju_terms": {"천간": ["기"], "오행": ["토"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.90
            },
            
            # 경금 일주 관련
            {
                "content": "경금 일주는 쇠의 기운을 가진 사람으로 강직하고 의지가 강합니다. 원칙을 중시하고 도전 정신이 강하며 기술 분야에 재능이 있습니다.",
                "saju_terms": {"천간": ["경"], "오행": ["금"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.93
            },
            
            # 신금 일주 관련
            {
                "content": "신금 일주는 보석의 기운으로 세련되고 감각적입니다. 예술적 재능이 뛰어나고 미적 감각이 좋으며 패션이나 디자인 분야에 적합합니다.",
                "saju_terms": {"천간": ["신"], "오행": ["금"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.91
            },
            
            # 임수 일주 관련
            {
                "content": "임수 일주는 바다의 기운을 가진 사람으로 포용력이 크고 지혜롭습니다. 학습 능력이 뛰어나고 연구직이나 학자의 길에 적합합니다.",
                "saju_terms": {"천간": ["임"], "오행": ["수"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.92
            },
            
            # 계수 일주 관련
            {
                "content": "계수 일주는 이슬이나 빗물의 기운으로 섬세하고 감성적입니다. 직감력이 뛰어나고 예술 분야나 상담업에 재능이 있습니다.",
                "saju_terms": {"천간": ["계"], "오행": ["수"], "성격": ["성격"], "직업": ["직업"]},
                "sentence_type": "personality",
                "confidence": 0.90
            },
            
            # 십신 관련
            {
                "content": "정관이 있으면 책임감이 강하고 사회적 지위를 얻을 가능성이 높습니다. 공무원이나 관리직에 적합하며 안정된 삶을 추구합니다.",
                "saju_terms": {"십신": ["정관"], "직업": ["공무원"]},
                "sentence_type": "interpretation",
                "confidence": 0.88
            },
            
            {
                "content": "식신이 강하면 표현력이 좋고 창의적입니다. 예술가, 요리사, 방송인 등 자신을 표현하는 직업에 어울립니다.",
                "saju_terms": {"십신": ["식신"], "직업": ["예술가"]},
                "sentence_type": "interpretation", 
                "confidence": 0.87
            },
            
            # 재물운 관련
            {
                "content": "편재가 있으면 돈을 버는 능력이 뛰어납니다. 사업가적 기질이 있고 투자나 장사에 재능이 있습니다. 하지만 돈 관리에 주의해야 합니다.",
                "saju_terms": {"십신": ["편재"], "재물": ["돈", "사업", "투자"], "직업": ["사업"]},
                "sentence_type": "prediction",
                "confidence": 0.89
            },
            
            # 연애운 관련
            {
                "content": "정관이 있는 여성은 좋은 남편을 만날 확률이 높습니다. 안정적이고 책임감 있는 남성과 인연이 있으며 결혼 생활이 순탄할 것입니다.",
                "saju_terms": {"십신": ["정관"], "애정": ["결혼", "남편"]},
                "sentence_type": "relationship",
                "confidence": 0.86
            },
            
            # 건강운 관련
            {
                "content": "화가 너무 강하면 심장이나 혈압에 주의해야 합니다. 스트레스를 받으면 열이 오르기 쉽고 불면증이 올 수 있습니다.",
                "saju_terms": {"오행": ["화"], "건강": ["심장", "혈압", "스트레스"]},
                "sentence_type": "health",
                "confidence": 0.84
            },
            
            {
                "content": "수가 부족하면 신장이나 방광, 생식기 계통이 약할 수 있습니다. 충분한 수분 섭취와 하체 운동이 도움됩니다.",
                "saju_terms": {"오행": ["수"], "건강": ["신장", "방광"]},
                "sentence_type": "health",
                "confidence": 0.85
            },
            
            # 대운 관련
            {
                "content": "대운에서 자신의 일간과 같은 오행이 오면 자신감이 생기고 적극성이 향상됩니다. 새로운 도전에 유리한 시기입니다.",
                "saju_terms": {"운세": ["대운"], "오행": ["오행"]},
                "sentence_type": "prediction",
                "confidence": 0.87
            }
        ]
    
    def add_training_data(self):
        """학습 데이터를 지식베이스에 추가"""
        conn = sqlite3.connect(self.knowledge_db)
        cursor = conn.cursor()
        
        added_count = 0
        
        for data in self.training_data:
            try:
                cursor.execute("""
                    INSERT INTO saju_knowledge 
                    (video_id, video_title, content, saju_terms, 
                     sentence_type, confidence, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    'training_data',
                    '전문가 사주 해석 자료',
                    data['content'],
                    json.dumps(data['saju_terms']),
                    data['sentence_type'],
                    data['confidence'],
                    'expert_training'
                ))
                added_count += 1
            except Exception as e:
                print(f"❌ 데이터 추가 실패: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ {added_count}개 학습 데이터 추가 완료")
        return added_count

def main():
    """메인 실행"""
    adder = SajuTrainingDataAdder()
    adder.add_training_data()
    
    # 추가된 데이터 확인
    conn = sqlite3.connect('saju_knowledge_complete.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM saju_knowledge WHERE source = 'expert_training'")
    expert_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM saju_knowledge")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(confidence) FROM saju_knowledge WHERE source = 'expert_training'")
    avg_confidence = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"""
    📊 지식베이스 상태:
    - 전문가 데이터: {expert_count}개
    - 전체 데이터: {total_count}개  
    - 평균 신뢰도: {avg_confidence:.2f}
    """)

if __name__ == "__main__":
    main()