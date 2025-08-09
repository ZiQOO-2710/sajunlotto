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

              {/* 입력 필드 - 개선된 레이아웃 */}
              <div className="space-y-4 mb-4">
                {/* 이름 입력 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">이름</label>
                  <input
                    type="text"
                    placeholder="이름을 입력하세요"
                    value={birthInfo.name}
                    onChange={(e) => {
                      const value = e.target.value;
                      // 한글(완성형+조합형), 영문, 공백만 허용 (숫자 및 특수문자 제외)
                      const filteredValue = value.replace(/[^가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z\s]/g, '');
                      
                      console.log('이름 입력:', value, '→ 필터링:', filteredValue);
                      setBirthInfo({...birthInfo, name: filteredValue});
                    }}
                    maxLength={20}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-base focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    style={{ 
                      color: '#000000 !important', 
                      backgroundColor: '#ffffff !important',
                      WebkitTextFillColor: '#000000',
                      opacity: 1
                    }}
                  />
                </div>

                {/* 생년월일 입력 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">생년월일</label>
                  <div className="space-y-2">
                    {/* 년도 */}
                    <input
                      type="text"
                      placeholder="년 (예: 1990)"
                      value={birthInfo.birth_year}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, ''); // 숫자만 허용
                        
                        // 년도는 4자리로 제한, 1900-2100 범위
                        if (value.length <= 4) {
                          if (value.length === 4) {
                            const year = parseInt(value);
                            if (year >= 1900 && year <= 2100) {
                              console.log('년도 입력 (유효):', value);
                              setBirthInfo({...birthInfo, birth_year: value});
                            } else {
                              console.log('년도 입력 (범위 외):', value);
                            }
                          } else {
                            console.log('년도 입력:', value);
                            setBirthInfo({...birthInfo, birth_year: value});
                          }
                        }
                      }}
                      maxLength={4}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-base text-center focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      style={{ 
                        color: '#000000 !important', 
                        backgroundColor: '#ffffff !important',
                        WebkitTextFillColor: '#000000',
                        opacity: 1
                      }}
                    />
                    {/* 월일 통합 */}
                    <input
                      type="text"
                      placeholder="월일 (예: 1207 = 12월 7일)"
                      value={
                        birthInfo.birth_month && birthInfo.birth_day 
                          ? `${birthInfo.birth_month.padStart(2, '0')}${birthInfo.birth_day.padStart(2, '0')}`
                          : birthInfo.birth_month 
                          ? birthInfo.birth_month
                          : ''
                      }
                      onChange={(e) => {
                        const rawValue = e.target.value;
                        const value = rawValue.replace(/\D/g, ''); // 숫자만 허용
                        console.log('월일 입력:', rawValue, '→ 숫자만:', value);
                        
                        if (value.length <= 4) {
                          if (value.length >= 2) {
                            const month = value.substring(0, 2);
                            const day = value.length > 2 ? value.substring(2, 4) : '';
                            
                            // 월 유효성 검사 (01-12)
                            const monthNum = parseInt(month);
                            if (monthNum >= 1 && monthNum <= 12) {
                              // 일 유효성 검사 (01-31)
                              if (day) {
                                const dayNum = parseInt(day);
                                if (dayNum >= 1 && dayNum <= 31) {
                                  console.log('월일 파싱 (유효):', { month, day });
                                  setBirthInfo({
                                    ...birthInfo, 
                                    birth_month: month,
                                    birth_day: day
                                  });
                                }
                              } else {
                                setBirthInfo({
                                  ...birthInfo, 
                                  birth_month: month,
                                  birth_day: ''
                                });
                              }
                            }
                          } else if (value.length === 1) {
                            setBirthInfo({
                              ...birthInfo,
                              birth_month: value,
                              birth_day: ''
                            });
                          } else {
                            setBirthInfo({
                              ...birthInfo,
                              birth_month: '',
                              birth_day: ''
                            });
                          }
                        }
                      }}
                      maxLength={4}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-base text-center focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      style={{ 
                        color: '#000000 !important', 
                        backgroundColor: '#ffffff !important',
                        WebkitTextFillColor: '#000000',
                        opacity: 1
                      }}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      💡 예시: 12월 7일 → 1207, 1월 15일 → 0115
                    </p>
                  </div>
                </div>

                {/* 시분 입력 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">태어난 시간</label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="시 (0-23)"
                      value={birthInfo.birth_hour}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, ''); // 숫자만 허용
                        
                        // 시간은 0-23 범위, 2자리 제한
                        if (value.length <= 2) {
                          if (value.length >= 1) {
                            const hour = parseInt(value);
                            if (hour >= 0 && hour <= 23) {
                              console.log('시간 입력 (유효):', value);
                              setBirthInfo({...birthInfo, birth_hour: value});
                            } else {
                              console.log('시간 입력 (범위 외):', value);
                            }
                          } else {
                            setBirthInfo({...birthInfo, birth_hour: value});
                          }
                        }
                      }}
                      maxLength={2}
                      className="px-3 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-base text-center focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      style={{ 
                        color: '#000000 !important', 
                        backgroundColor: '#ffffff !important',
                        WebkitTextFillColor: '#000000',
                        opacity: 1
                      }}
                    />
                    <input
                      type="text"
                      placeholder="분 (0-59)"
                      value={birthInfo.birth_minute}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, ''); // 숫자만 허용
                        
                        // 분은 0-59 범위, 2자리 제한
                        if (value.length <= 2) {
                          if (value.length >= 1) {
                            const minute = parseInt(value);
                            if (minute >= 0 && minute <= 59) {
                              console.log('분 입력 (유효):', value);
                              setBirthInfo({...birthInfo, birth_minute: value});
                            } else {
                              console.log('분 입력 (범위 외):', value);
                            }
                          } else {
                            setBirthInfo({...birthInfo, birth_minute: value});
                          }
                        }
                      }}
                      maxLength={2}
                      className="px-3 py-3 border border-gray-300 rounded-lg bg-white text-gray-900 text-base text-center focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      style={{ 
                        color: '#000000 !important', 
                        backgroundColor: '#ffffff !important',
                        WebkitTextFillColor: '#000000',
                        opacity: 1
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    ⏰ 정확한 시간을 모르시면 12시 0분으로 입력하세요
                  </p>
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
          {/* 사용자 정보 표시 */}
          <div className="mb-4">
            <div className="bg-white rounded-xl shadow-lg p-4">
              <h3 className="text-lg font-bold text-gray-800 mb-3 text-center">사주 정보</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-purple-50 rounded-lg p-3">
                  <span className="font-medium text-purple-700">성명:</span>
                  <span className="ml-2 text-gray-800">{birthInfo.name || '미입력'}</span>
                </div>
                <div className="bg-blue-50 rounded-lg p-3">
                  <span className="font-medium text-blue-700">양력/음력:</span>
                  <span className="ml-2 text-gray-800">{birthInfo.calendar_type === 'solar' ? '🌞 양력' : '🌙 음력'}</span>
                </div>
                <div className="bg-green-50 rounded-lg p-3 col-span-2">
                  <span className="font-medium text-green-700">생년월일:</span>
                  <span className="ml-2 text-gray-800">
                    {birthInfo.birth_year}년 {birthInfo.birth_month}월 {birthInfo.birth_day}일
                  </span>
                </div>
                <div className="bg-orange-50 rounded-lg p-3 col-span-2">
                  <span className="font-medium text-orange-700">태어난 시간:</span>
                  <span className="ml-2 text-gray-800">
                    {birthInfo.birth_hour}시 {birthInfo.birth_minute}분
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 사주 원국 표시 - 모바일 최적화 */}
          <div className="mb-4">
            {/* SajuPillars 컴포넌트 사용 */}
            {aiAnalysis?.saju_chart && (
              <SajuPillars pillars={aiAnalysis.saju_chart} />
            )}
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

              {/* 사주 풀이 - 모바일 최적화 */}
              <div className="bg-white rounded-xl shadow-lg p-4">
                <h3 className="text-base font-semibold text-gray-800 mb-3 flex items-center">
                  <Shield className="w-4 h-4 mr-2 text-purple-500" />
                  사주 팔자 해석
                </h3>
                <div className="space-y-3">
                  {/* 년주 해석 */}
                  <div className="bg-purple-50 rounded-lg p-3">
                    <h4 className="text-sm font-semibold text-purple-700 mb-2">🏛️ 년주 (조상과 뿌리)</h4>
                    <p className="text-xs text-gray-700">
                      {aiAnalysis?.saju_chart?.year && (
                        `${aiAnalysis.saju_chart.year.gan_hanja}(${aiAnalysis.saju_chart.year.gan}) ${aiAnalysis.saju_chart.year.ji_hanja}(${aiAnalysis.saju_chart.year.ji}) - 
                        ${aiAnalysis.saju_chart.year.gan_element}(${aiAnalysis.saju_chart.year.gan_yinyang})과 ${aiAnalysis.saju_chart.year.ji_element}(${aiAnalysis.saju_chart.year.ji_yinyang})의 조화로 조상의 기운과 태생적 성향을 나타냅니다.`
                      )}
                    </p>
                  </div>

                  {/* 월주 해석 */}
                  <div className="bg-blue-50 rounded-lg p-3">
                    <h4 className="text-sm font-semibold text-blue-700 mb-2">👥 월주 (사회와 직업)</h4>
                    <p className="text-xs text-gray-700">
                      {aiAnalysis?.saju_chart?.month && (
                        `${aiAnalysis.saju_chart.month.gan_hanja}(${aiAnalysis.saju_chart.month.gan}) ${aiAnalysis.saju_chart.month.ji_hanja}(${aiAnalysis.saju_chart.month.ji}) - 
                        ${aiAnalysis.saju_chart.month.gan_element}과 ${aiAnalysis.saju_chart.month.ji_element}의 기운으로 사회적 관계와 직업 운세를 주관합니다.`
                      )}
                    </p>
                  </div>

                  {/* 일주 해석 */}
                  <div className="bg-green-50 rounded-lg p-3">
                    <h4 className="text-sm font-semibold text-green-700 mb-2">💖 일주 (자아와 배우자)</h4>
                    <p className="text-xs text-gray-700">
                      {aiAnalysis?.saju_chart?.day && (
                        `${aiAnalysis.saju_chart.day.gan_hanja}(${aiAnalysis.saju_chart.day.gan}) ${aiAnalysis.saju_chart.day.ji_hanja}(${aiAnalysis.saju_chart.day.ji}) - 
                        본인의 핵심 성격과 배우자 궁을 나타내며, ${aiAnalysis.saju_chart.day.gan_element}과 ${aiAnalysis.saju_chart.day.ji_element}의 균형이 중요합니다.`
                      )}
                    </p>
                  </div>

                  {/* 시주 해석 */}
                  <div className="bg-orange-50 rounded-lg p-3">
                    <h4 className="text-sm font-semibold text-orange-700 mb-2">👶 시주 (자녀와 말년)</h4>
                    <p className="text-xs text-gray-700">
                      {aiAnalysis?.saju_chart?.hour && (
                        `${aiAnalysis.saju_chart.hour.gan_hanja}(${aiAnalysis.saju_chart.hour.gan}) ${aiAnalysis.saju_chart.hour.ji_hanja}(${aiAnalysis.saju_chart.hour.ji}) - 
                        ${aiAnalysis.saju_chart.hour.gan_element}과 ${aiAnalysis.saju_chart.hour.ji_element}의 기운으로 자녀운과 말년의 복을 예측할 수 있습니다.`
                      )}
                    </p>
                  </div>

                  {/* 오행 균형 해석 */}
                  <div className="bg-gray-50 rounded-lg p-3">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">⚖️ 오행 균형</h4>
                    <p className="text-xs text-gray-700">
                      {aiAnalysis?.saju_chart?.five_elements && (
                        `목 ${aiAnalysis.saju_chart.five_elements.목}%, 화 ${aiAnalysis.saju_chart.five_elements.화}%, 토 ${aiAnalysis.saju_chart.five_elements.토}%, 금 ${aiAnalysis.saju_chart.five_elements.금}%, 수 ${aiAnalysis.saju_chart.five_elements.수}%의 분포로 
                        ${aiAnalysis.saju_chart.dominant_element}의 기운이 강하여 ${aiAnalysis.saju_chart.chart_summary || '균형잡힌 성향을 보입니다'}.`
                      )}
                    </p>
                  </div>
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