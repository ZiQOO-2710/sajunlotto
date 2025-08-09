-- ==========================================
-- SajuLotto 혁신 아키텍처 데이터베이스 스키마
-- 12가지 천재적 아이디어 구현을 위한 통합 스키마
-- ==========================================

-- ==========================================
-- 사용자 및 프로필 관리
-- ==========================================

-- 확장된 사용자 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    birth_datetime TIMESTAMP, -- 정확한 생년월일시
    birth_timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
    calendar_type VARCHAR(10) DEFAULT 'solar', -- solar, lunar
    subscription_tier VARCHAR(20) DEFAULT 'free', -- free, basic, premium, master
    subscription_expires_at TIMESTAMP,
    privacy_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

-- AI Twin 개인화 테이블
CREATE TABLE ai_twins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    twin_name VARCHAR(50) NOT NULL,
    personality_profile JSONB NOT NULL, -- 성격 특성
    appearance_config JSONB, -- 외모 설정
    conversation_style JSONB, -- 대화 스타일
    learning_data_hash VARCHAR(255), -- 암호화된 학습 데이터 해시
    evolution_level INTEGER DEFAULT 1,
    relationship_depth INTEGER DEFAULT 0, -- 관계 깊이 점수
    privacy_mode VARCHAR(20) DEFAULT 'strict', -- strict, moderate, open
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 사주 분석 및 예측 시스템
-- ==========================================

-- 확장된 사주 프로필
CREATE TABLE saju_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    birth_info JSONB NOT NULL, -- 상세 생년월일시 정보
    pillars JSONB NOT NULL, -- 사주 사기둥
    elements_analysis JSONB NOT NULL, -- 오행 분석
    personality_traits JSONB, -- 성격 특성
    life_patterns JSONB, -- 인생 패턴
    lucky_elements JSONB, -- 행운 요소들
    unlucky_elements JSONB, -- 주의 요소들
    compatibility_profile JSONB, -- 궁합 프로필
    fortune_cycles JSONB, -- 운세 주기
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI 예측 및 검증 시스템
CREATE TABLE ai_predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    prediction_type VARCHAR(50), -- lotto, fortune, life_event
    target_date DATE,
    prediction_data JSONB NOT NULL,
    confidence_score DECIMAL(5,2),
    saju_weights JSONB,
    ai_model_version VARCHAR(20),
    validation_status VARCHAR(20) DEFAULT 'pending', -- pending, validated, failed
    actual_outcome JSONB,
    accuracy_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    validated_at TIMESTAMP
);

-- ==========================================
-- 스트리밍 서비스 시스템
-- ==========================================

-- 구독 관리
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(20) NOT NULL, -- basic, premium, master
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- monthly, yearly
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    auto_renewal BOOLEAN DEFAULT true,
    payment_method JSONB,
    payment_status VARCHAR(20) DEFAULT 'active', -- active, cancelled, expired
    personalization_level INTEGER DEFAULT 1,
    streaming_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 실시간 스트림 관리
CREATE TABLE destiny_streams (
    id SERIAL PRIMARY KEY,
    stream_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    stream_type VARCHAR(50), -- daily, weekly, special, live_consultation
    host_persona VARCHAR(50), -- AI 페르소나 이름
    target_audience JSONB, -- 대상 청중 조건
    content_metadata JSONB,
    viewer_count INTEGER DEFAULT 0,
    interaction_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    recording_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 스트림 상호작용
CREATE TABLE stream_interactions (
    id SERIAL PRIMARY KEY,
    stream_id INTEGER REFERENCES destiny_streams(id),
    user_id INTEGER REFERENCES users(id),
    interaction_type VARCHAR(50), -- message, question, reaction, tip
    interaction_data JSONB,
    timestamp_offset INTEGER, -- 스트림 시작 후 초 단위
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- B2B Oracle API 시스템
-- ==========================================

-- 기업 고객 관리
CREATE TABLE enterprise_clients (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    company_email VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_secret VARCHAR(255) NOT NULL,
    subscription_plan VARCHAR(50), -- startup, business, enterprise
    monthly_quota INTEGER NOT NULL,
    current_usage INTEGER DEFAULT 0,
    overage_allowed BOOLEAN DEFAULT false,
    billing_contact JSONB,
    webhook_endpoints JSONB, -- 콜백 URL들
    ip_whitelist JSONB, -- IP 제한
    rate_limit_per_minute INTEGER DEFAULT 60,
    custom_features JSONB, -- 맞춤 기능들
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, cancelled
    contract_start DATE,
    contract_end DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API 사용량 상세 추적
CREATE TABLE api_usage_logs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES enterprise_clients(id),
    endpoint_path VARCHAR(200) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    request_data JSONB,
    response_data JSONB,
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100), -- 요청 추적용 UUID
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- AI 페르소나 길드 시스템
-- ==========================================

-- AI 페르소나 정의
CREATE TABLE ai_personas (
    id SERIAL PRIMARY KEY,
    persona_key VARCHAR(50) UNIQUE NOT NULL, -- 시스템 키
    display_name VARCHAR(100) NOT NULL,
    character_description TEXT,
    specialty_areas JSONB NOT NULL, -- 전문 분야들
    personality_traits JSONB NOT NULL,
    speaking_style JSONB NOT NULL,
    knowledge_base JSONB, -- 지식 베이스 참조
    interaction_rules JSONB, -- 상호작용 규칙
    avatar_config JSONB, -- 아바타 설정
    voice_settings JSONB, -- 음성 설정
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI 길드 세션
CREATE TABLE guild_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_topic VARCHAR(300) NOT NULL,
    session_type VARCHAR(50), -- consultation, analysis, entertainment
    participating_personas JSONB NOT NULL, -- 참여한 AI들
    discussion_log JSONB, -- 대화 로그
    consensus_reached JSONB, -- 도달한 결론
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5),
    session_duration_minutes INTEGER,
    total_interactions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

-- ==========================================
-- 신뢰도 검증 시스템
-- ==========================================

-- AI 모델 신뢰도 추적
CREATE TABLE ai_credibility_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    prediction_category VARCHAR(50) NOT NULL, -- lotto, fortune, life_event
    evaluation_period VARCHAR(50) NOT NULL, -- 1year, 5year, 10year
    total_predictions INTEGER NOT NULL,
    correct_predictions INTEGER NOT NULL,
    accuracy_percentage DECIMAL(5,2) NOT NULL,
    confidence_intervals JSONB, -- 신뢰구간 데이터
    statistical_significance DECIMAL(5,3),
    benchmark_comparison JSONB, -- 벤치마크 대비 성능
    evaluation_methodology TEXT,
    calculated_at TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP
);

-- 백테스팅 결과
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(200) NOT NULL,
    test_category VARCHAR(50), -- historical_validation, cross_validation
    model_config JSONB NOT NULL,
    test_period_start DATE NOT NULL,
    test_period_end DATE NOT NULL,
    dataset_size INTEGER,
    results_summary JSONB NOT NULL, -- 결과 요약
    detailed_metrics JSONB, -- 상세 메트릭
    visualization_data JSONB, -- 그래프용 데이터
    test_status VARCHAR(20) DEFAULT 'completed', -- running, completed, failed
    execution_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 게임화 및 소셜 기능
-- ==========================================

-- 에너지 마켓플레이스
CREATE TABLE energy_marketplace (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id),
    buyer_id INTEGER REFERENCES users(id),
    energy_type VARCHAR(50), -- luck, health, wealth, love
    energy_amount INTEGER NOT NULL,
    price_per_unit DECIMAL(10,2),
    total_price DECIMAL(10,2),
    transaction_status VARCHAR(20) DEFAULT 'pending', -- pending, completed, cancelled
    energy_source JSONB, -- 에너지 출처 정보
    effectiveness_rating INTEGER, -- 구매자 평가
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 카르마 점수 시스템 (Project Echo)
CREATE TABLE karma_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL, -- donation, helping, volunteering
    action_description TEXT,
    karma_points INTEGER NOT NULL,
    fortune_impact_multiplier DECIMAL(3,2) DEFAULT 1.00,
    verification_status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    evidence_data JSONB, -- 증빙 데이터
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP
);

-- 사주 궁합 소셜 네트워크
CREATE TABLE saju_compatibility (
    id SERIAL PRIMARY KEY,
    user1_id INTEGER REFERENCES users(id),
    user2_id INTEGER REFERENCES users(id),
    compatibility_score INTEGER CHECK (compatibility_score >= 0 AND compatibility_score <= 100),
    compatibility_analysis JSONB, -- 상세 분석
    relationship_type VARCHAR(50), -- romantic, friendship, business
    mutual_elements JSONB, -- 공통 요소
    challenge_areas JSONB, -- 주의할 부분
    recommendation JSONB, -- 관계 조언
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user1_id, user2_id, relationship_type)
);

-- ==========================================
-- 기존 시스템과의 통합을 위한 테이블들
-- ==========================================

-- 기존 LottoDraw 테이블 (참조용)
CREATE TABLE lotto_draws (
    draw_no INTEGER PRIMARY KEY,
    draw_date TIMESTAMP,
    n1 INTEGER,
    n2 INTEGER,
    n3 INTEGER,
    n4 INTEGER,
    n5 INTEGER,
    n6 INTEGER,
    bonus INTEGER
);

-- 기존 Prediction 테이블 확장
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    draw_no INTEGER,
    predicted_numbers JSONB,
    method VARCHAR(50),
    confidence DECIMAL(5,2),
    saju_weights JSONB,
    ai_model_version VARCHAR(20),
    is_winning BOOLEAN DEFAULT NULL,
    match_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- 신규 필드들
    prediction_source VARCHAR(50), -- twin, guild, streaming, api
    personalization_level INTEGER DEFAULT 1,
    context_data JSONB -- 예측 시점의 맥락 정보
);

-- YouTube 학습 시스템 (기존 연동)
CREATE TABLE youtube_rules (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    category VARCHAR(50), -- saju, fortune, lottery, general
    effectiveness_score DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE saju_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    channel_title VARCHAR(200),
    published_at TIMESTAMP,
    thumbnail_url VARCHAR(500),
    url VARCHAR(500),
    keyword VARCHAR(100),
    relevance_score INTEGER DEFAULT 0,
    saju_terms JSONB,
    fortune_keywords JSONB,
    learning_value DECIMAL(5,2), -- AI 학습에 대한 가치 점수
    processed_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 성능 최적화 인덱스
-- ==========================================

-- 사용자 및 구독 관련 인덱스
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_expires_at);
CREATE INDEX idx_users_last_active ON users(last_active_at);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id, plan_type, payment_status);

-- AI Twin 관련 인덱스  
CREATE INDEX idx_ai_twins_user ON ai_twins(user_id);
CREATE INDEX idx_ai_twins_evolution ON ai_twins(evolution_level, relationship_depth);

-- 예측 및 분석 관련 인덱스
CREATE INDEX idx_ai_predictions_user_type ON ai_predictions(user_id, prediction_type, created_at);
CREATE INDEX idx_ai_predictions_validation ON ai_predictions(validation_status, target_date);
CREATE INDEX idx_saju_profiles_user ON saju_profiles(user_id);

-- 스트리밍 관련 인덱스
CREATE INDEX idx_streams_scheduled ON destiny_streams(scheduled_at, stream_type);
CREATE INDEX idx_streams_audience ON destiny_streams USING GIN(target_audience);
CREATE INDEX idx_stream_interactions_stream ON stream_interactions(stream_id, created_at);

-- B2B API 관련 인덱스
CREATE INDEX idx_enterprise_clients_key ON enterprise_clients(api_key);
CREATE INDEX idx_api_usage_client_date ON api_usage_logs(client_id, created_at);
CREATE INDEX idx_api_usage_endpoint ON api_usage_logs(endpoint_path, status_code);

-- AI 길드 관련 인덱스
CREATE INDEX idx_guild_sessions_user ON guild_sessions(user_id, created_at);
CREATE INDEX idx_guild_sessions_topic ON guild_sessions(session_topic, session_type);
CREATE INDEX idx_ai_personas_key ON ai_personas(persona_key);

-- 신뢰도 시스템 인덱스
CREATE INDEX idx_credibility_model ON ai_credibility_metrics(model_name, model_version);
CREATE INDEX idx_backtest_results_period ON backtest_results(test_period_start, test_period_end);

-- 게임화 및 소셜 인덱스
CREATE INDEX idx_energy_marketplace_type ON energy_marketplace(energy_type, transaction_status);
CREATE INDEX idx_karma_scores_user ON karma_scores(user_id, verification_status);
CREATE INDEX idx_compatibility_users ON saju_compatibility(user1_id, user2_id);

-- ==========================================
-- 초기 데이터 삽입
-- ==========================================

-- AI 페르소나 기본 데이터
INSERT INTO ai_personas (persona_key, display_name, character_description, specialty_areas, personality_traits, speaking_style) VALUES
('sage_kim', '현자 김정호', '전통 사주학의 대가로 깊은 통찰력을 가진 현자', 
 '["traditional_saju", "classical_interpretation", "historical_patterns"]',
 '{"wisdom": 95, "tradition": 90, "patience": 85, "formality": 80}',
 '{"tone": "formal", "pace": "slow", "examples": "historical", "language": "classical"}'),

('futurist_luna', '미래학자 루나', '현대적 관점으로 사주를 해석하는 미래지향적 전문가',
 '["modern_interpretation", "trend_analysis", "technology_integration"]',
 '{"innovation": 90, "adaptability": 95, "optimism": 80, "openness": 90}',
 '{"tone": "casual", "pace": "moderate", "examples": "contemporary", "language": "modern"}'),

('psychologist_minji', '심리학자 민지', '사주와 심리학을 융합한 분석을 제공하는 전문가',
 '["psychological_analysis", "personality_traits", "behavioral_patterns"]',
 '{"empathy": 95, "analytical": 90, "supportive": 85, "professional": 80}',
 '{"tone": "warm", "pace": "moderate", "examples": "psychological", "language": "professional"}'),

('investor_rich', '투자전문가 리치', '재물운과 투자에 특화된 사주 분석 전문가',
 '["wealth_fortune", "investment_timing", "business_opportunities"]',
 '{"practical": 90, "ambitious": 85, "realistic": 80, "confident": 95}',
 '{"tone": "confident", "pace": "fast", "examples": "business", "language": "practical"}'),

('love_coach_cupid', '연애코치 큐피드', '애정운과 인간관계에 특화된 따뜻한 상담사',
 '["love_fortune", "relationship_compatibility", "social_connections"]',
 '{"warmth": 95, "understanding": 90, "romantic": 85, "encouraging": 90}',
 '{"tone": "warm", "pace": "gentle", "examples": "romantic", "language": "emotional"}');

-- 기본 구독 플랜 설정용 참조 데이터
COMMENT ON COLUMN subscriptions.plan_type IS 'Subscription tiers: basic(₩9,900), premium(₩19,900), master(₩39,900)';
COMMENT ON COLUMN enterprise_clients.subscription_plan IS 'B2B plans: startup(₩100k), business(₩500k), enterprise(₩2M)';

-- ==========================================
-- 뷰 및 함수들
-- ==========================================

-- 사용자 구독 현황 뷰
CREATE VIEW user_subscription_status AS
SELECT 
    u.id as user_id,
    u.name,
    u.subscription_tier,
    s.plan_type as active_plan,
    s.end_date as subscription_end,
    CASE 
        WHEN s.end_date > NOW() THEN 'active'
        WHEN s.end_date IS NULL THEN 'free'
        ELSE 'expired'
    END as status
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.payment_status = 'active';

-- AI 신뢰도 요약 뷰
CREATE VIEW ai_credibility_summary AS
SELECT 
    model_name,
    prediction_category,
    AVG(accuracy_percentage) as avg_accuracy,
    COUNT(*) as evaluation_count,
    MAX(calculated_at) as last_updated
FROM ai_credibility_metrics
WHERE calculated_at > NOW() - INTERVAL '30 days'
GROUP BY model_name, prediction_category;

-- 스트림 인기도 뷰
CREATE VIEW stream_popularity AS
SELECT 
    ds.id,
    ds.title,
    ds.stream_type,
    ds.viewer_count,
    COUNT(si.id) as total_interactions,
    AVG(CASE 
        WHEN si.interaction_type = 'reaction' THEN 1 
        WHEN si.interaction_type = 'question' THEN 2
        WHEN si.interaction_type = 'tip' THEN 3
        ELSE 1 
    END) as engagement_score
FROM destiny_streams ds
LEFT JOIN stream_interactions si ON ds.id = si.stream_id
GROUP BY ds.id, ds.title, ds.stream_type, ds.viewer_count
ORDER BY engagement_score DESC, ds.viewer_count DESC;