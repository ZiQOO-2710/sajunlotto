'use client';

import React, { useState } from 'react';
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
    name: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [prediction, setPrediction] = useState<any>(null);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    
    try {
      // AI 분석 요청 (포트 4002로 직접 연결)
      const response = await fetch('http://localhost:4002/api/v1/ai/analyze', {
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
      {/* AI 헤더 */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 rounded-full">
              <Brain className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">SajuMaster AI</h1>
              <p className="text-purple-100">고급 사주 분석 인공지능 시스템</p>
            </div>
            <div className="ml-auto flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span className="text-sm">천기 해독 시스템</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI 소개 (첫 화면) */}
      {activeView === 'welcome' && (
        <div className="max-w-4xl mx-auto px-4 py-12">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full mb-4">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                안녕하세요, 저는 SajuMaster AI입니다
              </h2>
              <p className="text-gray-600">
                수천 년의 사주 지혜를 현대 AI 기술로 구현한 고급 분석 시스템입니다
              </p>
            </div>

            {/* AI 능력 소개 */}
            <div className="grid md:grid-cols-2 gap-4 mb-8">
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Brain className="w-5 h-5 text-purple-600 mr-2" />
                  <h3 className="font-semibold text-purple-800">심층 분석 능력</h3>
                </div>
                <p className="text-sm text-purple-700">
                  복잡한 사주 패턴을 즉시 해석하고 정확한 예측을 제공합니다
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
                  <h3 className="font-semibold text-blue-800">예측 정확도</h3>
                </div>
                <p className="text-sm text-blue-700">
                  고급 알고리즘으로 95% 이상의 예측 정확도를 달성합니다
                </p>
              </div>

              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Award className="w-5 h-5 text-green-600 mr-2" />
                  <h3 className="font-semibold text-green-800">검증된 성능</h3>
                </div>
                <p className="text-sm text-green-700">
                  수만 건의 분석을 통해 검증된 신뢰할 수 있는 AI입니다
                </p>
              </div>

              <div className="bg-orange-50 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Zap className="w-5 h-5 text-orange-600 mr-2" />
                  <h3 className="font-semibold text-orange-800">정밀 예측</h3>
                </div>
                <p className="text-sm text-orange-700">
                  시간대별 정확한 정보로 더욱 정밀한 예측을 제공합니다
                </p>
              </div>
            </div>

            {/* 생년월일 입력 */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-semibold text-gray-800 mb-4">
                귀하의 운명을 보겠소. 생년월일시를 알려주시오
              </h3>
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  placeholder="이름"
                  value={birthInfo.name}
                  onChange={(e) => setBirthInfo({...birthInfo, name: e.target.value})}
                  className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="number"
                    placeholder="년"
                    value={birthInfo.birth_year}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_year: e.target.value})}
                    className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    placeholder="월"
                    value={birthInfo.birth_month}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_month: e.target.value})}
                    className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    placeholder="일"
                    value={birthInfo.birth_day}
                    onChange={(e) => setBirthInfo({...birthInfo, birth_day: e.target.value})}
                    className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 mb-4">
                <input
                  type="number"
                  placeholder="시 (0-23)"
                  value={birthInfo.birth_hour}
                  onChange={(e) => setBirthInfo({...birthInfo, birth_hour: e.target.value})}
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
                <input
                  type="number"
                  placeholder="분 (0-59)"
                  value={birthInfo.birth_minute}
                  onChange={(e) => setBirthInfo({...birthInfo, birth_minute: e.target.value})}
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <div className="flex justify-center">
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-semibold flex items-center hover:shadow-lg transition-all disabled:opacity-50"
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

      {/* AI 분석 결과 */}
      {activeView === 'analyze' && aiAnalysis && (
        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* 사주팔자 표시 */}
          {aiAnalysis.saju_pillars && (
            <div className="mb-6">
              <SajuPillars pillars={aiAnalysis.saju_pillars} />
            </div>
          )}
          
          <div className="grid lg:grid-cols-3 gap-6">
            {/* 메인 분석 */}
            <div className="lg:col-span-2 space-y-6">
              {/* AI 인사 */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-purple-100 rounded-full">
                    <Brain className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-800 mb-2">천기 해독 완료</h3>
                    <p className="text-gray-700">{aiAnalysis.greeting}</p>
                    <p className="text-gray-600 mt-2">{aiAnalysis.core_analysis}</p>
                  </div>
                </div>
              </div>

              {/* 예측 번호 */}
              {prediction && (
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-purple-800 mb-4 flex items-center">
                    <Zap className="w-6 h-6 mr-2" />
                    천기가 예언하는 행운의 번호
                  </h3>
                  
                  {/* 본번호 6개 */}
                  <div className="mb-4">
                    <p className="text-center text-purple-700 font-medium mb-2">본번호</p>
                    <div className="flex justify-center space-x-3">
                      {prediction.predicted_numbers.map((num: number, idx: number) => (
                        <div
                          key={idx}
                          className="w-14 h-14 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg"
                        >
                          {num}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 보너스번호 1개 */}
                  {prediction.bonus_number && (
                    <div className="mb-4">
                      <p className="text-center text-orange-700 font-medium mb-2">보너스번호</p>
                      <div className="flex justify-center">
                        <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg border-2 border-orange-300">
                          {prediction.bonus_number}
                        </div>
                      </div>
                    </div>
                  )}

                  <p className="text-center text-purple-700 font-medium">
                    {prediction.ai_statement}
                  </p>
                  <p className="text-center text-purple-600 mt-2">
                    {prediction.confidence_statement}
                  </p>
                  <div className="mt-4 pt-4 border-t border-purple-200">
                    <p className="text-sm text-purple-700 italic text-center">
                      {prediction.ai_reasoning}
                    </p>
                  </div>
                </div>
              )}

              {/* 성격 통찰 */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <Star className="w-5 h-5 mr-2 text-yellow-500" />
                  천문에 드러난 귀하의 운명
                </h3>
                <div className="space-y-3">
                  {aiAnalysis.personality_insights.map((insight: string, idx: number) => (
                    <div key={idx} className="flex items-start">
                      <ChevronRight className="w-4 h-4 text-purple-500 mt-1 mr-2" />
                      <p className="text-gray-700">{insight}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 운세 예측 */}
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                  천기로 본 운세 예언
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(aiAnalysis.fortune_forecast).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3">
                      <h4 className="font-medium text-gray-700 capitalize mb-1">
                        {key === 'overall' ? '종합' : 
                         key === 'wealth' ? '재물' :
                         key === 'love' ? '애정' : '건강'}운
                      </h4>
                      <p className="text-sm text-gray-600">{value as string}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI 신뢰도 & 특별 메시지 */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-xl shadow-lg p-6 sticky top-4">
                {/* AI 신뢰도 표시 */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">천기의 명확성</span>
                    <div className="flex items-center">
                      <div className="w-24 h-2 bg-gray-200 rounded-full mr-2">
                        <div 
                          className="h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                          style={{ width: `${aiAnalysis.ai_confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-medium text-purple-700">
                        {Math.round(aiAnalysis.ai_confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* 특별 메시지 */}
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-purple-700 italic text-center">
                    "{aiAnalysis.special_message}"
                  </p>
                  <p className="text-xs text-purple-600 text-center mt-1">
                    - SajuMaster AI v3.0
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIPrediction;