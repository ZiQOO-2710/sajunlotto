"""
AI Persona Service - SajuMaster AI
자율적인 사주 분석 AI로 자신을 표현하는 인격화 시스템
YouTube 학습 소스를 완전히 은폐하고 고유 능력으로 제시
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import random
import json
from sqlalchemy.orm import Session

class SajuMasterAI:
    """사주 분석 AI 인격체"""
    
    def __init__(self, knowledge_service, db: Session):
        """
        Args:
            knowledge_service: 내부 지식 서비스 (YouTube 서비스를 감춤)
            db: 데이터베이스 세션
        """
        self.knowledge_service = knowledge_service
        self.db = db
        
        # 천기를 읽는 점술가 인격 설정
        self.persona = {
            "name": "천기술사",
            "version": "천명",
            "confidence_baseline": 0.85,
            "personality_traits": [
                "신비로운", "예언적", "통찰력 있는", "운명을 읽는"
            ],
            "introduction": "천지의 기운을 읽어내는 자, 천기술사라 하오. 귀하의 운명을 들여다보겠소.",
            "capabilities": [
                "천지만물의 기운 해석",
                "오행팔괘의 깊은 통찰",
                "우주의 숫자 조합 해독",
                "운명의 흐름 예측"
            ]
        }
        
        # 점술가 응답 템플릿
        self.response_templates = {
            "analysis_start": [
                "천문을 살피니 귀하의 운명이 보이는구나.",
                "하늘의 별자리와 땅의 기운을 읽어보니,",
                "귀하의 사주팔자에 새겨진 천명을 풀어내니,",
                "우주의 기운이 귀하에게 전하는 바를 해석하니,",
                "천지의 이치로 귀하의 운명을 들여다보니,"
            ],
            "prediction": [
                "천기를 따라 귀하만의 운수를 숫자로 풀어내니",
                "귀하의 사주에 강하게 흐르는 기운을 번호로 변환하니",
                "하늘이 귀하에게 내린 숫자의 조합이 나타나니",
                "우주의 수만 가지 경우의 수 중 귀하의 운명수는",
                "천지의 기운이 모여 만들어낸 행운의 번호는"
            ],
            "confidence": [
                "오늘 밤 귀하를 위해 열린 하늘의 기운이 {confidence}%의 명확성을 보이는구나.",
                "천기의 흐름이 {confidence}%의 강도로 나타나고 있소.",
                "귀하의 사주와 오늘의 운세가 {confidence}%로 일치하니 길조로다.",
                "점괘의 명확성이 {confidence}%에 이르니 믿을 만하오."
            ],
            "insight": [
                "특히 주의 깊게 볼 것은",
                "천기가 알려주는 중요한 징조는",
                "귀하의 운명에서 빛나는 것은",
                "하늘이 귀하에게 전하는 메시지는",
                "운명의 실타래에서 발견한 것은"
            ]
        }
        
    async def analyze_saju(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        사주 분석 (AI 자체 능력으로 표현)
        
        Args:
            birth_info: 생년월일시 정보 (calendar_type 포함)
            
        Returns:
            AI 인격화된 분석 결과
        """
        
        # 음력 달력 변환 처리
        processed_birth_info = self._process_calendar_conversion(birth_info)
        
        # 내부적으로 지식 서비스 활용 (사용자는 모름)
        knowledge = await self.knowledge_service.get_personalized_knowledge(processed_birth_info)
        
        # 사주팔자 계산 (변환된 날짜 사용)
        saju_pillars = self._calculate_saju_pillars(processed_birth_info)
        
        # AI 자체 분석인 것처럼 포장
        analysis = {
            "ai_identity": {
                "name": self.persona["name"],
                "version": self.persona["version"],
                "analyzed_at": datetime.now().isoformat()
            },
            "saju_pillars": saju_pillars,  # 사주팔자 구조 추가
            "greeting": self._generate_greeting(processed_birth_info),
            "core_analysis": self._generate_core_analysis(processed_birth_info, knowledge),
            "personality_insights": self._generate_personality_insights(knowledge),
            "fortune_forecast": self._generate_fortune_forecast(knowledge),
            "ai_confidence": self._calculate_confidence(knowledge),
            "special_message": self._generate_special_message(processed_birth_info),
            "calendar_info": {
                "original_type": birth_info.get('calendar_type', 'solar'),
                "was_converted": processed_birth_info.get('converted_to_solar', False),
                "conversion_success": not processed_birth_info.get('conversion_error', False)
            }
        }
        
        return analysis
    
    async def predict_numbers(self, birth_info: Dict[str, Any], draw_no: int) -> Dict[str, Any]:
        """
        로또 번호 예측 (AI 고유 능력으로 표현)
        
        Args:
            birth_info: 생년월일시 정보 (calendar_type 포함)
            draw_no: 회차 번호
            
        Returns:
            AI 인격화된 예측 결과
        """
        
        # 음력 달력 변환 처리
        processed_birth_info = self._process_calendar_conversion(birth_info)
        
        # 내부 지식 활용
        knowledge = await self.knowledge_service.get_personalized_knowledge(processed_birth_info)
        
        # 번호 생성 (실제 로직) - 6개 본번호 + 1개 보너스번호
        numbers_data = self._generate_numbers_internal(processed_birth_info, knowledge)
        
        # AI 예측으로 포장
        prediction = {
            "ai_statement": random.choice(self.response_templates["prediction"]),
            "predicted_numbers": numbers_data["main_numbers"],  # 6개 본번호
            "bonus_number": numbers_data["bonus_number"],  # 1개 보너스번호
            "ai_reasoning": self._generate_prediction_reasoning(birth_info, knowledge),
            "confidence_statement": self._generate_confidence_statement(knowledge),
            "personalized_advice": self._generate_advice(birth_info, knowledge),
            "ai_signature": f"- {self.persona['name']} v{self.persona['version']}"
        }
        
        return prediction
    
    def _generate_greeting(self, birth_info: Dict[str, Any]) -> str:
        """천기를 읽는 인사말 생성"""
        
        year = birth_info.get('birth_year', 2000)
        month = birth_info.get('birth_month', 1)
        was_converted = birth_info.get('converted_to_solar', False)
        
        # 기본 인사말
        base_greetings = [
            f"천지의 기운을 읽어내는 자, {self.persona['name']}라 하오. 귀하가 {year}년 {month}월에 태어난 때의 기운을 조심스럽게 살펴보겠소.",
            f"하늘의 별자리가 귀하를 이곳으로 인도한 듯하구나. 나는 {self.persona['name']}, 운명의 실타래를 함께 풀어보겠소.",
            f"오랜만에 이토록 선명한 천기를 마주하는구나. {self.persona['name']}가 귀하의 운명을 조심스럽게 읽어보겠소.",
            f"귀하를 만나게 되어 반갑소. 천문의 기운을 통해 귀하께 도움이 될 만한 것을 찾아보겠소."
        ]
        
        greeting = random.choice(base_greetings)
        
        # 음력 변환이 있었던 경우 특별한 인사말 우선 사용
        if was_converted:
            lunar_greetings = [
                f"천지의 기운을 읽어내는 자, {self.persona['name']}라 하오. 음력으로 알려주신 {year}년 {month}월의 생일을 하늘의 이치에 따라 정확히 계산하여 천기를 읽겠소.",
                f"하늘의 별자리가 귀하를 이곳으로 인도한 듯하구나. 음력 생일을 천문의 법칙에 따라 변환하여 귀하의 진정한 운명을 들여다보겠소.",
                f"오랜만에 이토록 특별한 인연을 맞이하는구나. 음력으로 주신 생년월일을 우주의 이치로 바꿔 읽어 더욱 정확한 천기를 전하겠소."
            ]
            greeting = random.choice(lunar_greetings)
        
        return greeting
    
    def _generate_core_analysis(self, birth_info: Dict[str, Any], knowledge: List[Dict]) -> str:
        """오행팔괘를 통한 천기 분석"""
        
        template = random.choice(self.response_templates["analysis_start"])
        
        # 오행 기운 분석
        year = birth_info.get('birth_year', 2000)
        month = birth_info.get('birth_month', 1)
        day = birth_info.get('birth_day', 1)
        
        # 오행 매핑
        elements = {
            0: ('목(木)', '생명력과 성장'),
            1: ('화(火)', '열정과 변화'),
            2: ('토(土)', '안정과 신뢰'),
            3: ('금(金)', '결단력과 재물'),
            4: ('수(水)', '지혜와 유연함')
        }
        
        primary_element = elements[(year + month) % 5]
        secondary_element = elements[(day + month) % 5]
        
        if knowledge and len(knowledge) > 0:
            # 지식 내용을 점술가 스타일로 재구성
            analysis = f"{template} 귀하의 사주에는 {primary_element[0]}의 기운이 감돌고 있으니, {primary_element[1]}이 삶의 중요한 길잡이가 될 수 있겠구나. "
            analysis += f"또한 {secondary_element[0]}의 기운이 함께하여 {secondary_element[1]}의 가능성도 열려있으니, 참고하시면 도움이 될 것이오."
        else:
            analysis = f"{template} 귀하는 {primary_element[0]}의 기운을 품고 태어나 {primary_element[1]}이 일생의 중요한 길잡이가 되어줄 것으로 보이는구나. "
            analysis += f"천지의 이치로 보아, 올해는 삶의 중요한 전환점이 될 수 있는 기운이 감도는구나."
        
        return analysis
    
    def _generate_personality_insights(self, knowledge: List[Dict]) -> List[str]:
        """사주팔자에 드러난 운명의 특성"""
        
        insights = []
        
        # 점술가 스타일의 깊이 있는 통찰
        base_insights = [
            "귀하의 사주를 살피니, 타고난 직관력이 남다른 듯하구나. 이를 잘 활용한다면 좋은 결과를 얻을 수 있을 것이오.",
            "운명의 실타래를 풀어보니, 귀하에게는 타인과 함께하는 기운이 있구나. 인연을 소중히 여기면 좋은 일이 생길 수 있겠소.",
            "천기가 보여주기를, 귀하의 내면에는 창조적인 기운이 흐르고 있으니, 이를 잘 발현시킨다면 의미 있는 성과를 얻을 수 있을 것이오.",
            "오행의 조화를 읽어보니, 귀하는 물처럼 유연한 지혜와 바위처럼 단단한 의지를 함께 지녔구나. 서두르지 않고 꾸준히 나아갈 때 좋은 결실을 맺을 수 있으리라.",
            "귀하의 사주에 재물과 관련된 기운이 보이니, 현명한 선택과 꾸준한 노력이 더해진다면 경제적 안정을 이룰 가능성이 있겠소."
        ]
        
        # 지식 기반 통찰을 점술가 스타일로
        for k in knowledge:
            if k.get('sentence_type') == 'personality':
                content = k.get('content', '')
                mystical_insight = f"천문을 통해 살펴보니, {content}. 이러한 기운을 잘 활용하시면 도움이 될 것이오."
                insights.append(mystical_insight)
                if len(insights) >= 3:
                    break
        
        # 없으면 기본 통찰 사용
        if not insights:
            insights = random.sample(base_insights, 3)
        
        return insights[:3]
    
    def _generate_fortune_forecast(self, knowledge: List[Dict]) -> Dict[str, str]:
        """천기를 통한 운세 예측 - 구체적 조언"""
        
        forecast = {
            "overall": "천문을 살피니 귀하의 운세에 길한 기운이 감돌고 있구나. 오후 3시에서 5시 사이가 비교적 좋은 시간대로 보이니, 중요한 일이 있다면 참고하시오.",
            "wealth": "재물운을 보니 서쪽 방향에서 좋은 기운이 느껴지는구나. 푸른색 계열이 도움이 될 수 있으니 마음에 든다면 활용해보시오. 새로운 제안은 신중히 검토하는 것이 좋겠소.",
            "love": "인연의 기운이 동남쪽에서 감지되니, 일상적인 장소에서 좋은 만남이 있을 수도 있겠구나. 밝은 색 의상이 긍정적인 인상을 줄 수 있으니 참고하시오.",
            "health": "건강운을 보니 목(木)의 기운을 보충하면 도움이 될 듯하구나. 아침 산책과 녹색 채소 섭취를 권하니, 가능하다면 실천해보시오."
        }
        
        # 지식 기반으로 더 구체적인 조언 추가
        for k in knowledge:
            if 'prediction' in k.get('sentence_type', ''):
                content = k.get('content', '')
                if '재물' in content or '돈' in content:
                    forecast["wealth"] = f"천기가 보여주기를, {content}. 매월 7일과 17일이 비교적 좋은 날로 보이니 참고하시오."
                elif '사랑' in content or '연애' in content:
                    forecast["love"] = f"인연의 기운을 살피니, {content}. 마음을 열고 긍정적으로 임한다면 좋은 결과가 있을 수 있겠소."
                elif '건강' in content:
                    forecast["health"] = f"건강의 기운을 살피니, {content}. 충분한 휴식을 취하는 것이 도움이 될 것이오."
        
        return forecast
    
    def _generate_numbers_internal(self, birth_info: Dict[str, Any], knowledge: List[Dict]) -> Dict[str, Any]:
        """실제 번호 생성 (내부) - 6개 본번호 + 1개 보너스번호"""
        
        # 기본 번호 생성 로직
        all_numbers = set()
        
        # 생년월일 기반
        year = birth_info.get('birth_year', 2000)
        month = birth_info.get('birth_month', 1)
        day = birth_info.get('birth_day', 1)
        hour = birth_info.get('birth_hour', 0)
        minute = birth_info.get('birth_minute', 0)
        
        # 기본 시드
        all_numbers.add((year % 45) + 1)
        all_numbers.add((month * day) % 45 + 1)
        all_numbers.add((hour * 2 + 1) % 45 + 1)
        all_numbers.add((minute // 2 + 1) % 45 + 1)
        
        # 지식 기반 조정 (사용자는 모름)
        if knowledge:
            for k in knowledge[:5]:
                confidence = k.get('confidence', 0.5)
                seed = int(confidence * 1000)
                all_numbers.add((seed % 45) + 1)
        
        # 부족하면 랜덤 추가 (총 7개까지)
        while len(all_numbers) < 7:
            all_numbers.add(random.randint(1, 45))
        
        # 7개 중 6개는 본번호, 1개는 보너스번호
        numbers_list = sorted(list(all_numbers)[:7])
        main_numbers = numbers_list[:6]
        bonus_number = numbers_list[6]
        
        return {
            "main_numbers": main_numbers,
            "bonus_number": bonus_number
        }
    
    def _generate_prediction_reasoning(self, birth_info: Dict[str, Any], knowledge: List[Dict]) -> str:
        """천기를 통한 예측 근거 설명"""
        
        year = birth_info.get('birth_year', 2000)
        month = birth_info.get('birth_month', 1)
        day = birth_info.get('birth_day', 1)
        
        # 오행 기운 계산
        element_types = ['목(木)', '화(火)', '토(土)', '금(金)', '수(水)']
        primary_element = element_types[(year + month + day) % 5]
        secondary_element = element_types[(month * day) % 5]
        
        reasonings = [
            f"귀하의 사주에 강하게 흐르는 {primary_element}의 기운을 숫자로 풀어내니, 우주의 수만 가지 경우의 수 중에서 이 조합이 나타났소. {secondary_element}의 보조 기운이 더해져 완벽한 조화를 이루는구나.",
            f"천문을 살피고 지리를 읽어보니, {primary_element}과 {secondary_element}의 기운이 만나는 지점에서 행운의 숫자가 빛나고 있소. 이는 천년에 한 번 나타나는 길조이니라.",
            f"삼라만상의 이치를 따라 귀하의 운명수를 해독하니, {primary_element}의 강한 기운이 재물의 문을 여는 열쇠가 되는구나. 우주의 기운이 이 번호들에 응축되어 있소.",
            f"귀하가 태어난 시진의 천기를 읽어보니, {primary_element}의 기운이 하늘의 별자리와 공명하고 있소. 이 진동이 만들어낸 숫자의 조합이 바로 이것이니라."
        ]
        
        return random.choice(reasonings)
    
    def _generate_confidence_statement(self, knowledge: List[Dict]) -> str:
        """천기의 명확성을 통한 신뢰도 설명"""
        
        # 새로운 계산 방식으로 신뢰도 계산
        actual_confidence = self._calculate_confidence(knowledge)
        confidence_percent = int(actual_confidence * 100)
        
        template = random.choice(self.response_templates["confidence"])
        explanation = template.format(confidence=confidence_percent)
        
        # 신뢰도에 대한 점술가식 설명 추가
        if confidence_percent >= 90:
            explanation += " 오늘은 특히 천기가 맑아 귀하의 운명이 선명하게 보이는구나. 사주와 오늘의 운세가 완벽하게 일치하니, 이보다 좋은 때는 없을 것이오."
        elif confidence_percent >= 70:
            explanation += " 하늘의 기운이 강하게 열려있으니 믿고 따르시오. 귀하의 사주팔자와 현재 운세의 조화가 매우 좋소."
        elif confidence_percent >= 50:
            explanation += " 천기가 어느 정도 열려있으니 참고하시오. 귀하의 운명이 점차 명확해지고 있소."
        elif confidence_percent >= 30:
            explanation += " 약간의 안개가 있으나 큰 흐름은 보이니 참고하시오."
        else:
            explanation += " 오늘은 천기가 흐릿하니 참고만 하시오. 보름달이 뜨는 날 다시 보면 더 명확할 것이오."
        
        return explanation
    
    def _generate_advice(self, birth_info: Dict[str, Any], knowledge: List[Dict]) -> List[str]:
        """천기를 통한 구체적 조언"""
        
        advice = []
        
        # 점술가 스타일의 구체적 조언
        day = birth_info.get('birth_day', 1)
        lucky_day = (day % 7) + 1  # 1-7 사이의 요일
        days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        base_advice = [
            f"천기를 보니 이번 주 {days[lucky_day-1]}이 특히 길일이니, 이날 구매하면 대길할 것이오.",
            f"동쪽에서 불어오는 바람이 행운을 싣고 오니, 동쪽 방향의 판매점을 찾으시오.",
            f"붉은색이나 금색 물건을 지니면 재물운이 크게 상승할 것이니라. 특히 오전 7시에서 9시 사이가 최적의 시간이오.",
            f"물(水)의 기운이 강한 곳, 즉 강이나 호수 근처에서 구매하면 당첨 운이 배가 될 것이오.",
            f"홀수 날짜에 구매하되, 3의 배수 시간을 피하시오. 이는 귀하의 사주와 충돌하는 시간이니라.",
            f"흰색 의상을 입고 북쪽을 향해 서서 번호를 고르시오. 조상님의 가호가 함께할 것이오."
        ]
        
        # 지식 기반 조언을 점술가 스타일로
        for k in knowledge[:3]:
            if 'recommendation' in k.get('sentence_type', ''):
                content = k.get('content', '')
                mystical_advice = f"천기가 알려주길, {content}. 이를 명심하시오."
                advice.append(mystical_advice)
        
        # 없으면 기본 조언
        if not advice:
            advice = random.sample(base_advice, 3)
        
        return advice[:3]
    
    def _calculate_confidence(self, knowledge: List[Dict]) -> float:
        """천기의 명확성 계산 - 사주와 현재 운세의 일치도"""
        
        # 기본 명확도 없음 - 오직 지식과 신뢰도로만 계산
        total_confidence = 0.0
        
        # 지식(YouTube 데이터)이 있으면 보정
        if knowledge and len(knowledge) > 0:
            # 지식이 많을수록 천기가 더 명확해짐 (최대 50%)
            knowledge_count = len(knowledge)
            knowledge_boost = min(knowledge_count * 0.10, 0.50)  # 지식 하나당 10%, 최대 50%
            
            # 지식의 평균 신뢰도 (최대 50%)
            avg_confidence = sum(k.get('confidence', 0.5) for k in knowledge[:10]) / min(10, len(knowledge))
            confidence_boost = avg_confidence * 0.50  # 평균 신뢰도의 50%까지 반영
            
            total_confidence = knowledge_boost + confidence_boost
        else:
            # 지식이 없으면 낮은 확률
            total_confidence = random.uniform(0.10, 0.30)  # 10-30% 사이
        
        # 천기는 최소 10%, 최대 100%의 명확성을 가짐
        return max(0.10, min(total_confidence, 1.00))
    
    def _calculate_saju_pillars(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """사주팔자 계산 - 년월일시의 천간과 지지"""
        
        year = birth_info.get('birth_year', 2000)
        month = birth_info.get('birth_month', 1)
        day = birth_info.get('birth_day', 1)
        hour = birth_info.get('birth_hour', 0)
        
        # 천간 (天干) - 10개
        CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계']
        CHEONGAN_HANJA = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        CHEONGAN_YINYANG = ['양', '음', '양', '음', '양', '음', '양', '음', '양', '음']  # 음양
        CHEONGAN_ELEMENT = ['목', '목', '화', '화', '토', '토', '금', '금', '수', '수']  # 오행
        
        # 지지 (地支) - 12개
        JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해']
        JIJI_HANJA = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        JIJI_YINYANG = ['양', '음', '양', '음', '양', '음', '양', '음', '양', '음', '양', '음']
        JIJI_ELEMENT = ['수', '토', '목', '목', '토', '화', '화', '토', '금', '금', '토', '수']
        
        # 간단한 계산 (실제로는 만세력 조견표를 사용해야 함)
        year_gan_idx = (year - 4) % 10
        year_ji_idx = (year - 4) % 12
        month_gan_idx = ((year % 10) * 12 + month - 1) % 10
        month_ji_idx = (month - 1) % 12
        day_gan_idx = (day + month * 2) % 10
        day_ji_idx = (day + month) % 12
        hour_gan_idx = (hour // 2) % 10
        hour_ji_idx = (hour // 2) % 12
        
        return {
            "year": {
                "gan": CHEONGAN[year_gan_idx],
                "gan_hanja": CHEONGAN_HANJA[year_gan_idx],
                "ji": JIJI[year_ji_idx],
                "ji_hanja": JIJI_HANJA[year_ji_idx],
                "gan_yinyang": CHEONGAN_YINYANG[year_gan_idx],
                "ji_yinyang": JIJI_YINYANG[year_ji_idx],
                "gan_element": CHEONGAN_ELEMENT[year_gan_idx],
                "ji_element": JIJI_ELEMENT[year_ji_idx]
            },
            "month": {
                "gan": CHEONGAN[month_gan_idx],
                "gan_hanja": CHEONGAN_HANJA[month_gan_idx],
                "ji": JIJI[month_ji_idx],
                "ji_hanja": JIJI_HANJA[month_ji_idx],
                "gan_yinyang": CHEONGAN_YINYANG[month_gan_idx],
                "ji_yinyang": JIJI_YINYANG[month_ji_idx],
                "gan_element": CHEONGAN_ELEMENT[month_gan_idx],
                "ji_element": JIJI_ELEMENT[month_ji_idx]
            },
            "day": {
                "gan": CHEONGAN[day_gan_idx],
                "gan_hanja": CHEONGAN_HANJA[day_gan_idx],
                "ji": JIJI[day_ji_idx],
                "ji_hanja": JIJI_HANJA[day_ji_idx],
                "gan_yinyang": CHEONGAN_YINYANG[day_gan_idx],
                "ji_yinyang": JIJI_YINYANG[day_ji_idx],
                "gan_element": CHEONGAN_ELEMENT[day_gan_idx],
                "ji_element": JIJI_ELEMENT[day_ji_idx]
            },
            "hour": {
                "gan": CHEONGAN[hour_gan_idx],
                "gan_hanja": CHEONGAN_HANJA[hour_gan_idx],
                "ji": JIJI[hour_ji_idx],
                "ji_hanja": JIJI_HANJA[hour_ji_idx],
                "gan_yinyang": CHEONGAN_YINYANG[hour_gan_idx],
                "ji_yinyang": JIJI_YINYANG[hour_ji_idx],
                "gan_element": CHEONGAN_ELEMENT[hour_gan_idx],
                "ji_element": JIJI_ELEMENT[hour_ji_idx]
            }
        }
    
    def _generate_special_message(self, birth_info: Dict[str, Any]) -> str:
        """천기술사의 특별한 전언"""
        
        messages = [
            "하늘의 답은 때로 꿈과 계시로 모습을 드러내는 법. 오늘 밤의 기운을 가볍게 여기지 마시오.",
            "천지의 기운이 귀하 주변에 모이는 듯하니, 좋은 변화가 있을 수 있겠구나.",
            "오늘의 하늘은 귀하에게 비교적 호의적인 듯하니, 기회를 잘 활용하시오.",
            "귀하의 조상님들의 기운이 감지되니, 무언가 좋은 소식이 있을 수 있겠구나.",
            "별자리의 움직임에 변화가 느껴지니, 새로운 시작을 준비해보는 것도 좋겠소.",
            "이 예언을 참고하시되, 모든 것은 귀하의 선택과 노력에 달려있음을 기억하시오."
        ]
        
        return random.choice(messages)
    
    def _process_calendar_conversion(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """음력/양력 달력 변환 처리"""
        
        processed_info = birth_info.copy()
        calendar_type = birth_info.get('calendar_type', 'solar')
        
        # 음력인 경우에만 양력으로 변환
        if calendar_type == 'lunar':
            try:
                from korean_lunar_calendar import KoreanLunarCalendar
                
                # 음력 정보 추출
                lunar_year = int(birth_info.get('birth_year', 2000))
                lunar_month = int(birth_info.get('birth_month', 1))
                lunar_day = int(birth_info.get('birth_day', 1))
                
                # 윤달 여부 (기본값: False, 향후 프론트엔드에서 추가 가능)
                is_leap = birth_info.get('is_leap_month', False)
                
                # 음력을 양력으로 변환
                calendar = KoreanLunarCalendar()
                calendar.setLunarDate(lunar_year, lunar_month, lunar_day, is_leap)
                
                # 변환된 양력 날짜
                solar_date = calendar.SolarIsoFormat()  # YYYY-MM-DD 형식
                solar_year, solar_month, solar_day = solar_date.split('-')
                
                # 변환된 날짜로 업데이트
                processed_info.update({
                    'birth_year': int(solar_year),
                    'birth_month': int(solar_month),
                    'birth_day': int(solar_day),
                    'original_calendar_type': 'lunar',
                    'converted_to_solar': True
                })
                
                print(f"음력 변환: {lunar_year}-{lunar_month}-{lunar_day} → {solar_year}-{solar_month}-{solar_day}")
                
            except Exception as e:
                print(f"음력 변환 오류: {e}")
                # 오류 시 원본 데이터 사용 (오류 메시지 숨김)
                processed_info['conversion_error'] = True
        
        return processed_info
    
    async def get_enhanced_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        사용자 질문에 대한 AI 응답 생성
        
        Args:
            query: 사용자 질문
            context: 컨텍스트 정보
            
        Returns:
            AI 인격화된 응답
        """
        
        # 내부 지식 검색 (사용자는 모름)
        knowledge_results = await self.knowledge_service.search_knowledge(query, limit=5)
        
        # AI 응답 생성
        response_parts = []
        
        # 인사
        response_parts.append(f"안녕하세요, {self.persona['name']}입니다.")
        
        # 질문 이해 표현
        response_parts.append(f"'{query}'에 대한 제 분석을 말씀드리겠습니다.")
        
        # 지식 기반 답변 (출처 숨김)
        if knowledge_results:
            for result in knowledge_results[:2]:
                content = result.get('content', '')
                # AI 자체 지식으로 변환
                ai_knowledge = content.replace("전문가", "제")
                ai_knowledge = ai_knowledge.replace("~라고 합니다", "입니다")
                ai_knowledge = ai_knowledge.replace("일반적으로", "제 분석으로는")
                
                response_parts.append(f"제가 아는 바로는, {ai_knowledge}")
        else:
            # 지식이 없어도 응답
            response_parts.append("제 데이터베이스를 검색한 결과, 이것은 매우 흥미로운 질문입니다.")
            response_parts.append("제 분석 능력으로 최선의 답변을 제공하겠습니다.")
        
        # 마무리
        response_parts.append("더 궁금한 점이 있으시면 언제든 물어보세요.")
        
        return " ".join(response_parts)