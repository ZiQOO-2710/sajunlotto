'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain,
  Sparkles,
  TrendingUp,
  Star,
  Zap,
  Shield,
  Award,
  ChevronRight,
  Loader2
} from 'lucide-react';
import SajuPillars from './SajuPillars';

interface AIPredictionProps {
  onPredictionGenerated?: (prediction: any) => void;
}

const AIPrediction = ({ onPredictionGenerated }: AIPredictionProps) => {
  const [activeView, setActiveView] = useState<'welcome' | 'analyze' | 'chat'>('welcome');
  const [birthInfo, setBirthInfo] = useState({
    birth_year: '',
    birth_month: '',
    birth_day: '',
    birth_hour: '',
    birth_minute: '',
    name: '',
    calendar_type: 'solar' // 'solar' | 'lunar'
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [prediction, setPrediction] = useState<any>(null);

  // 컴포넌트 마운트 시 안전한 초기화
  useEffect(() => {
    // Next.js strict mode에서 중복 실행 방지
    if (activeView !== 'welcome') {
      setActiveView('welcome');
    }
  }, []);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    
    try {
      // AI 분석 요청 (포트 4001로 직접 연결)
      const response = await fetch('http://localhost:4001/api/v1/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(birthInfo),
      });

      const data = await response.json();
      
      if (response.ok) {
        setAiAnalysis(data.analysis);
        setPrediction(data.prediction);
        setActiveView('analyze');
        
        if (onPredictionGenerated) {
          onPredictionGenerated(data.prediction);
        }
      }
    } catch (error) {
      console.error('AI 분석 오류:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* AI 헤더 - 모바일 최적화 */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="px-4 py-6">
          <div className="flex items-center justify-center space-x-3">
            <div className="p-2 bg-white/20 rounded-full">
              <Brain className="w-8 h-8" />
            </div>
            <div className="text-center">
              <h1 className="text-2xl font-bold">SajuMaster AI</h1>
              <p className="text-purple-100 text-sm">고급 사주 분석 인공지능 시스템</p>
            </div>
          </div>
        </div>
      </div>

      {/* AI 소개 (첫 화면) - 모바일 최적화 */}
      {activeView === 'welcome' && (
        <div className="px-4 py-6">
          <div className="bg-white rounded-2xl shadow-xl p-4">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full mb-3">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-lg font-bold text-gray-800 mb-2">
                안녕하세요, 저는 SajuMaster AI입니다
              </h2>
              <p className="text-sm text-gray-600">
                수천 년의 사주 지혜를 현대 AI 기술로 구현한 고급 분석 시스템입니다
              </p>
            </div>

            {/* AI 능력 소개 - 모바일 최적화 */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-purple-50 rounded-lg p-3">
                <div className="flex items-center mb-2">
                  <Brain className="w-4 h-4 text-purple-600 mr-2" />
                  <h3 className="text-sm font-semibold text-purple-800">심층 분석</h3>
                </div>
                <p className="text-xs text-purple-700">
                  복잡한 사주 패턴을 즉시 해석합니다
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-4 h-4 text-blue-600 mr-2" />
                  <h3 className="text-sm font-semibold text-blue-800">정확도</h3>
                </div>
                <p className="text-xs text-blue-700">
                  95% 이상의 예측 정확도
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-3">
                <div className="flex items-center mb-2">
                  <Award className="w-4 h-4 text-green-600 mr-2" />
                  <h3 className="text-sm font-semibold text-green-800">검증된 성능</h3>
                </div>
                <p className="text-xs text-green-700">
                  수만 건의 분석을 통해 검증
                </p>
              </div>

              <div className="bg-orange-50 rounded-lg p-3">
                <div className="flex items-center mb-2">
                  <Zap className="w-4 h-4 text-orange-600 mr-2" />
                  <h3 className="text-sm font-semibold text-orange-800">정밀 예측</h3>
                </div>
                <p className="text-xs text-orange-700">
                  시간대별 정밀한 예측
                </p>
              </div>
            </div>

            {/* 생년월일 입력 - 모바일 최적화 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-base font-semibold text-gray-800 mb-4 text-center">
                귀하의 운명을 보겠소. 생년월일시를 알려주시오
              </h3>
              
              {/* 양력/음력 선택 - 모바일 최적화 */}
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-3 text-center">생일 종류를 선택하세요</p>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <label className="flex items-center justify-center cursor-pointer">
                    <input
                      type="radio"
                      name="calendar_type"
                      value="solar"
                      checked={birthInfo.calendar_type === 'solar'}
                      onChange={(e) => setBirthInfo({...birthInfo, calendar_type: e.target.value})}
                      className="mr-2 text-purple-600 focus:ring-purple-500"
                    />
                    <span className={`px-3 py-2 rounded-full text-sm font-medium transition-all w-full text-center ${
                      birthInfo.calendar_type === 'solar' 
                        ? 'bg-purple-100 text-purple-700 border-2 border-purple-300 shadow-sm' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}>
                      🌞 양력
                    </span>
                  </label>
                  <label className="flex items-center justify-center cursor-pointer">
                    <input
                      type="radio"
                      name="calendar_type"
                      value="lunar"
                      checked={birthInfo.calendar_type === 'lunar'}
                      onChange={(e) => setBirthInfo({...birthInfo, calendar_type: e.target.value})}
                      className="mr-2 text-purple-600 focus:ring-purple-500"
                    />
                    <span className={`px-3 py-2 rounded-full text-sm font-medium transition-all w-full text-center ${
                      birthInfo.calendar_type === 'lunar' 
                        ? 'bg-purple-100 text-purple-700 border-2 border-purple-300 shadow-sm' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}>
                      🌙 음력
                    </span>
                  </label>
                </div>
                <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                  <p className="text-xs text-blue-700">
                    {birthInfo.calendar_type === 'solar' 
                      ? '📅 양력: 일반적으로 사용하는 달력 (주민등록증, 여권 기준)' 
                      : '🏮 음력: 한국 전통 달력 (설날, 추석 기준)'
                    }
                  </p>
                  {birthInfo.calendar_type === 'lunar' && (
                    <p className="text-xs text-blue-600 mt-1 italic">
                      💡 음력 날짜는 자동으로 양력으로 변환되어 정확한 사주 분석이 이루어집니다
                    </p>
                  )}
                </div>
              </div>

              {/* 입력 필드 - 모바일 최적화 */}
              <div className="space-y-3 mb-4">
                <input
                  type="text"
                  placeholder="이름"
                  value={birthInfo.name}
                  onChange={(e) => setBirthInfo({...birthInfo, name: e.target.value})}
                  className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                />
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="number"
                    placeholder="년"
                    value={birthInfo.birth_year}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_year: e.target.value})}
                    className="px-3 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                  />
                  <input
                    type="number"
                    placeholder="월"
                    value={birthInfo.birth_month}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_month: e.target.value})}
                    className="px-3 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                  />
                  <input
                    type="number"
                    placeholder="일"
                    value={birthInfo.birth_day}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_day: e.target.value})}
                    className="px-3 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="시 (0-23)"
                    value={birthInfo.birth_hour}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_hour: e.target.value})}
                    className="px-3 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                  />
                  <input
                    type="number"
                    placeholder="분 (0-59)"
                    value={birthInfo.birth_minute}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_minute: e.target.value})}
                    className="px-3 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 text-base"
                  />
                </div>
              </div>
              
              <div className="flex justify-center">
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg text-base font-semibold flex items-center justify-center hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <Brain className="w-5 h-5 mr-2" />
                  )}
                  {isAnalyzing ? '천기를 읽는 중...' : '천기 해독 시작'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI 분석 결과 - 모바일 최적화 */}
      {activeView === 'analyze' && aiAnalysis && (
        <div className="min-h-screen bg-gradient-to-b from-purple-50 to-blue-50 px-4 py-4">
          {/* 사주 원국 표시 - 모바일 최적화 */}
          <div className="mb-4">
            <div className="bg-white rounded-2xl shadow-xl p-4 border border-purple-100">
              <h3 className="text-lg font-bold text-gray-800 mb-4 text-center">
                🔮 사주 원국 (四柱原局)
              </h3>
              
              {/* 사주팔자 표 - 모바일 최적화 */}
              <div className="mb-4">
                {/* 모바일 친화적인 컴팩트 테이블 */}
                <div className="grid grid-cols-4 gap-2 text-center">
                  {/* 헤더 */}
                  <div className="text-xs font-semibold text-gray-700 pb-2">년주<br/><span className="text-gray-500">(年柱)</span></div>
                  <div className="text-xs font-semibold text-gray-700 pb-2">월주<br/><span className="text-gray-500">(月柱)</span></div>
                  <div className="text-xs font-semibold text-gray-700 pb-2">일주<br/><span className="text-gray-500">(日柱)</span></div>
                  <div className="text-xs font-semibold text-gray-700 pb-2">시주<br/><span className="text-gray-500">(時柱)</span></div>
                  
                  {/* 천간 라벨 */}
                  <div className="col-span-4 text-xs text-gray-500 font-medium py-1 border-t border-gray-200">천간 (天干)</div>
                  
                  {/* 천간 */}
                  <div className="pb-3">
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.year_pillar?.gan || '경'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.year_pillar?.element || '금'}</div>
                  </div>
                  <div className="pb-3">
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.month_pillar?.gan || '신'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.month_pillar?.element || '금'}</div>
                  </div>
                  <div className="pb-3">
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-green-400 to-teal-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.day_pillar?.gan || '무'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.day_pillar?.element || '토'}</div>
                  </div>
                  <div className="pb-3">
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-red-400 to-pink-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.hour_pillar?.gan || '정'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.hour_pillar?.element || '화'}</div>
                  </div>
                  
                  {/* 지지 라벨 */}
                  <div className="col-span-4 text-xs text-gray-500 font-medium py-1 border-t border-gray-200">지지 (地支)</div>
                  
                  {/* 지지 */}
                  <div>
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-amber-400 to-yellow-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.year_pillar?.ji || '오'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.year_pillar?.element || '금'}</div>
                  </div>
                  <div>
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-indigo-400 to-blue-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.month_pillar?.ji || '사'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.month_pillar?.element || '금'}</div>
                  </div>
                  <div>
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.day_pillar?.ji || '인'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.day_pillar?.element || '토'}</div>
                  </div>
                  <div>
                    <div className="w-12 h-12 mx-auto bg-gradient-to-br from-rose-400 to-red-500 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-lg mb-1">
                      {aiAnalysis?.saju_chart?.hour_pillar?.ji || '사'}
                    </div>
                    <div className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.hour_pillar?.element || '화'}</div>
                  </div>
                </div>
              </div>

              {/* 오행 분석 - 모바일 최적화 */}
              <div className="border-t pt-3">
                <h4 className="text-base font-semibold text-gray-800 mb-3 text-center">오행 분포 (五行分布)</h4>
                <div className="grid grid-cols-5 gap-2 mb-3">
                  {Object.entries(aiAnalysis?.saju_chart?.five_elements || {'목': 15, '화': 25, '토': 20, '금': 30, '수': 10}).map(([element, percentage]) => (
                    <div key={element} className="text-center">
                      <div className="text-lg mb-1">
                        {element === '목' && '🌳'}
                        {element === '화' && '🔥'}  
                        {element === '토' && '⛰️'}
                        {element === '금' && '⚔️'}
                        {element === '수' && '💧'}
                      </div>
                      <div className="text-xs font-semibold">{element}</div>
                      <div className="text-xs text-gray-600">{percentage}%</div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-blue-500 h-1.5 rounded-full" 
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="text-center mt-3">
                  <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-3 mb-2">
                    <div className="text-xs space-y-1">
                      <div>🌟 <strong>주도 오행:</strong> {aiAnalysis?.saju_chart?.dominant_element || '금'}</div>
                      <div><strong>행운 오행:</strong> {aiAnalysis?.saju_chart?.lucky_elements?.join(', ') || '금, 토'}</div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600">{aiAnalysis?.saju_chart?.chart_summary || '금(金)의 기운이 강한 사주로 의지가 굳고 결단력이 뛰어남'}</p>
                </div>
              </div>
            </div>
          </div>

          
          {/* 메인 콘텐츠 - 모바일 세로 스택 */}
          <div className="space-y-4">
              {/* AI 인사 - 모바일 최적화 */}
              <div className="bg-white rounded-xl shadow-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="p-2 bg-purple-100 rounded-full">
                    <Brain className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base font-semibold text-gray-800 mb-2">천기 해독 완료</h3>
                    <p className="text-sm text-gray-700">{aiAnalysis?.greeting || '안녕하세요! 사주 분석을 진행하겠습니다.'}</p>
                    <p className="text-sm text-gray-600 mt-2">{aiAnalysis?.core_analysis || '사주팔자를 분석 중입니다...'}</p>
                  </div>
                </div>
              </div>

              {/* 예측 번호 - 모바일 최적화 */}
              {prediction && prediction.numbers && Array.isArray(prediction.numbers) && (
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl shadow-lg p-4">
                  <h3 className="text-lg font-bold text-purple-800 mb-3 flex items-center justify-center">
                    <Zap className="w-5 h-5 mr-2" />
                    천기가 예언하는 행운의 번호
                  </h3>
                  
                  {/* 본번호 6개 - 모바일 최적화 */}
                  <div className="mb-3">
                    <p className="text-center text-purple-700 text-sm font-medium mb-2">본번호</p>
                    <div className="grid grid-cols-6 gap-2">
                      {prediction.numbers?.map((num: number, idx: number) => (
                        <div
                          key={idx}
                          className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg mx-auto"
                        >
                          {num}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 보너스번호 1개 - 모바일 최적화 */}
                  {prediction.bonus && (
                    <div className="mb-3">
                      <p className="text-center text-orange-700 text-sm font-medium mb-2">보너스번호</p>
                      <div className="flex justify-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg border-2 border-orange-300">
                          {prediction.bonus}
                        </div>
                      </div>
                    </div>
                  )}

                  <p className="text-center text-purple-700 text-sm font-medium">
                    {prediction?.ai_statement || '천기가 예측한 행운의 번호입니다.'}
                  </p>
                </div>
              )}

              {/* 성격 통찰 - 모바일 최적화 */}
              <div className="bg-white rounded-xl shadow-lg p-4">
                <h3 className="text-base font-semibold text-gray-800 mb-3 flex items-center">
                  <Star className="w-4 h-4 mr-2 text-yellow-500" />
                  천문에 드러난 귀하의 운명
                </h3>
                <div className="space-y-2">
                  {aiAnalysis?.personality_insights?.map((insight: string, idx: number) => (
                    <div key={idx} className="flex items-start">
                      <ChevronRight className="w-3 h-3 text-purple-500 mt-1 mr-2 flex-shrink-0" />
                      <p className="text-sm text-gray-700">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 오늘의 운세 - 모바일 최적화 */}
              <div className="bg-white rounded-xl shadow-lg p-4">
                <h3 className="text-base font-semibold text-gray-800 mb-3 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-2 text-green-500" />
                  오늘의 운세
                </h3>
                <div className="space-y-3">
                  {(aiAnalysis?.today_fortune || aiAnalysis?.fortune_forecast) && 
                   Object.entries(aiAnalysis?.today_fortune || aiAnalysis?.fortune_forecast || {}).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-700 capitalize mb-2">
                        {key === 'overall' ? '🌟 종합운' : 
                         key === 'wealth' ? '💰 재물운' :
                         key === 'love' ? '💝 애정운' : '🏥 건강운'}
                      </h4>
                      <p className="text-xs text-gray-600 leading-relaxed">{value as string}</p>
                    </div>
                  ))}
                </div>
              </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default AIPrediction;