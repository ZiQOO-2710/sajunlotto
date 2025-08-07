'use client';

import React, { useState } from 'react';
import { 
  Zap, 
  Brain, 
  TrendingUp, 
  Lightbulb, 
  Youtube, 
  Star,
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowRight
} from 'lucide-react';

interface EnhancedPredictionProps {
  onPredictionGenerated?: (prediction: any) => void;
}

interface PredictionRequest {
  draw_no: number;
  method?: string;
}

interface EnhancedPredictionResult {
  prediction: {
    id: number;
    predicted_numbers: number[];
    confidence: number;
    enhanced_confidence: number;
    confidence_boost: number;
    enhancement_applied: boolean;
    saju_weights: Record<string, number>;
    method: string;
  };
  enhancement: {
    applied: boolean;
    confidence_boost: number;
    knowledge_sources: number;
    knowledge_applied: string[];
    recommendations: string[];
    reason?: string;
  };
  youtube_insights?: {
    total_knowledge_sources: number;
    applied_knowledge_count: number;
    personalized_recommendations: number;
  };
}

const EnhancedPrediction = ({ onPredictionGenerated }: EnhancedPredictionProps) => {
  const [drawNo, setDrawNo] = useState(1150); // 기본값
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState<EnhancedPredictionResult | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [basicPrediction, setBasicPrediction] = useState<any>(null);

  // 기본 예측 생성
  const generateBasicPrediction = async (request: PredictionRequest) => {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/predictions/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('기본 예측 생성 실패');
    }

    const data = await response.json();
    return data.data;
  };

  // 강화된 예측 생성
  const generateEnhancedPrediction = async () => {
    if (!drawNo || drawNo < 1) {
      setMessage({ type: 'error', text: '올바른 회차 번호를 입력해주세요.' });
      return;
    }

    setIsLoading(true);
    setPrediction(null);
    setBasicPrediction(null);

    try {
      const request: PredictionRequest = {
        draw_no: drawNo,
        method: 'enhanced_saju_youtube'
      };

      // 비교 모드인 경우 기본 예측도 함께 생성
      if (comparisonMode) {
        const basicResult = await generateBasicPrediction({
          ...request,
          method: 'saju_ml'
        });
        setBasicPrediction(basicResult);
      }

      // 강화된 예측 생성
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/predictions/enhanced', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const data = await response.json();

      if (response.ok) {
        setPrediction(data.data);
        setMessage({ 
          type: 'success', 
          text: `${drawNo}회차 강화된 예측이 생성되었습니다!` 
        });
        
        if (onPredictionGenerated) {
          onPredictionGenerated(data.data);
        }
      } else {
        setMessage({ type: 'error', text: data.detail || '예측 생성 실패' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '네트워크 오류가 발생했습니다.' });
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumbers = (numbers: number[]) => {
    return numbers.sort((a, b) => a - b);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white mb-6">
        <div className="flex items-center">
          <Zap className="w-8 h-8 mr-3" />
          <div>
            <h1 className="text-2xl font-bold">YouTube 지식 기반 강화 예측</h1>
            <p className="opacity-90">사주 분석과 YouTube 학습 지식을 결합한 차세대 예측 시스템</p>
          </div>
        </div>
      </div>

      {/* 메시지 표시 */}
      {message && (
        <div className={`mb-4 p-4 rounded-lg flex items-center ${
          message.type === 'success' ? 'bg-green-100 text-green-800' :
          message.type === 'error' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5 mr-2" /> : 
           message.type === 'error' ? <AlertCircle className="w-5 h-5 mr-2" /> :
           <AlertCircle className="w-5 h-5 mr-2" />}
          {message.text}
        </div>
      )}

      {/* 예측 입력 폼 */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">예측 설정</h3>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              회차 번호
            </label>
            <input
              type="number"
              min="1"
              value={drawNo}
              onChange={(e) => setDrawNo(parseInt(e.target.value))}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
              placeholder="예: 1150"
            />
          </div>
          
          <div className="flex items-end">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={comparisonMode}
                onChange={(e) => setComparisonMode(e.target.checked)}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">기본 예측과 비교</span>
            </label>
          </div>
          
          <button
            onClick={generateEnhancedPrediction}
            disabled={isLoading}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Brain className="w-4 h-4 mr-2" />
            )}
            {isLoading ? '생성중...' : '강화 예측'}
          </button>
        </div>
      </div>

      {/* 예측 결과 */}
      {prediction && (
        <div className="space-y-6">
          {/* 기본 vs 강화 비교 */}
          {comparisonMode && basicPrediction && (
            <div className="grid md:grid-cols-2 gap-6">
              {/* 기본 예측 */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-lg font-semibold mb-4 text-gray-700">기본 예측</h4>
                <div className="flex flex-wrap gap-2 mb-4">
                  {formatNumbers(basicPrediction.predicted_numbers).map((num: number, index: number) => (
                    <div
                      key={index}
                      className="w-12 h-12 bg-gray-200 border-2 border-gray-300 rounded-full flex items-center justify-center font-bold text-gray-700"
                    >
                      {num}
                    </div>
                  ))}
                </div>
                <div className="text-sm text-gray-600">
                  <p>신뢰도: {(basicPrediction.confidence * 100).toFixed(1)}%</p>
                  <p>방법: 기본 사주 + ML</p>
                </div>
              </div>

              {/* 강화 예측 */}
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
                <h4 className="text-lg font-semibold mb-4 flex items-center text-purple-800">
                  <Zap className="w-5 h-5 mr-2" />
                  강화 예측
                </h4>
                <div className="flex flex-wrap gap-2 mb-4">
                  {formatNumbers(prediction.prediction.predicted_numbers).map((num, index) => (
                    <div
                      key={index}
                      className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-full flex items-center justify-center font-bold shadow-lg"
                    >
                      {num}
                    </div>
                  ))}
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>기본 신뢰도:</span>
                    <span>{(prediction.prediction.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-green-600 font-medium">
                    <span>강화 신뢰도:</span>
                    <span>{(prediction.prediction.enhanced_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-blue-600">
                    <span>부스트:</span>
                    <span>+{(prediction.prediction.confidence_boost * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 단일 예측 결과 */}
          {!comparisonMode && (
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border-2 border-purple-200">
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-purple-800 mb-2 flex items-center justify-center">
                  <Star className="w-6 h-6 mr-2" />
                  {drawNo}회차 강화 예측 번호
                </h3>
                <p className="text-purple-600">YouTube 학습 지식으로 강화된 결과입니다</p>
              </div>

              <div className="flex flex-wrap justify-center gap-3 mb-6">
                {formatNumbers(prediction.prediction.predicted_numbers).map((num, index) => (
                  <div
                    key={index}
                    className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-full flex items-center justify-center text-xl font-bold shadow-lg transform transition-transform hover:scale-105"
                  >
                    {num}
                  </div>
                ))}
              </div>

              <div className="grid md:grid-cols-3 gap-4 text-center">
                <div className="bg-white rounded-lg p-4">
                  <TrendingUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-blue-700">
                    {(prediction.prediction.enhanced_confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">최종 신뢰도</div>
                </div>

                <div className="bg-white rounded-lg p-4">
                  <Zap className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-green-700">
                    +{(prediction.prediction.confidence_boost * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">AI 부스트</div>
                </div>

                <div className="bg-white rounded-lg p-4">
                  <Youtube className="w-8 h-8 text-red-600 mx-auto mb-2" />
                  <div className="text-2xl font-bold text-red-700">
                    {prediction.enhancement.knowledge_sources}
                  </div>
                  <div className="text-sm text-gray-600">지식 소스</div>
                </div>
              </div>
            </div>
          )}

          {/* 강화 세부 정보 */}
          {prediction.enhancement.applied && (
            <div className="bg-white rounded-lg border p-6">
              <h4 className="text-lg font-semibold mb-4 flex items-center">
                <Brain className="w-5 h-5 mr-2 text-purple-600" />
                AI 강화 분석
              </h4>

              <div className="grid md:grid-cols-2 gap-6">
                {/* 적용된 지식 */}
                {prediction.enhancement.knowledge_applied.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3 flex items-center">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      적용된 사주 지식
                    </h5>
                    <div className="space-y-2">
                      {prediction.enhancement.knowledge_applied.map((knowledge, index) => (
                        <div key={index} className="bg-blue-50 border-l-4 border-blue-400 p-3 text-sm">
                          {knowledge}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 추천사항 */}
                {prediction.enhancement.recommendations.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-800 mb-3 flex items-center">
                      <ArrowRight className="w-4 h-4 mr-2" />
                      개인화된 추천
                    </h5>
                    <div className="space-y-2">
                      {prediction.enhancement.recommendations.map((rec, index) => (
                        <div key={index} className="bg-green-50 border-l-4 border-green-400 p-3 text-sm">
                          {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* YouTube 인사이트 */}
              {prediction.youtube_insights && (
                <div className="mt-6 pt-6 border-t">
                  <h5 className="font-medium text-gray-800 mb-3 flex items-center">
                    <Youtube className="w-4 h-4 mr-2 text-red-600" />
                    YouTube 학습 기여도
                  </h5>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="bg-red-50 rounded-lg p-3">
                      <div className="text-lg font-bold text-red-700">
                        {prediction.youtube_insights.total_knowledge_sources}
                      </div>
                      <div className="text-xs text-red-600">총 지식 소스</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3">
                      <div className="text-lg font-bold text-blue-700">
                        {prediction.youtube_insights.applied_knowledge_count}
                      </div>
                      <div className="text-xs text-blue-600">적용된 지식</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3">
                      <div className="text-lg font-bold text-green-700">
                        {prediction.youtube_insights.personalized_recommendations}
                      </div>
                      <div className="text-xs text-green-600">맞춤 추천</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 강화 미적용 안내 */}
          {!prediction.enhancement.applied && prediction.enhancement.reason && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-800 mb-2">AI 강화 미적용</h4>
                  <p className="text-yellow-700">{prediction.enhancement.reason}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 사용법 안내 */}
      {!prediction && (
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-3 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2" />
            YouTube 강화 예측이란?
          </h3>
          <div className="text-blue-700 space-y-2">
            <p>• 기존 사주 분석에 YouTube에서 학습한 실제 사주 전문가들의 지식을 결합</p>
            <p>• 개인의 사주 특성에 맞춘 맞춤형 지식을 적용하여 예측 정확도 향상</p>
            <p>• 실시간으로 축적되는 사주 전문 지식으로 지속적인 성능 개선</p>
            <p>• 기본 예측 대비 평균 5-15% 신뢰도 향상</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPrediction;