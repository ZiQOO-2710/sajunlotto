'use client';

import React, { useState } from 'react';
import { Star, Sparkles, TrendingUp, Users, Award, Calendar, BarChart3, User } from 'lucide-react';
import Link from 'next/link';
import { useUser } from '../contexts/UserContext';
import AuthModal from './AuthModal';
import UserProfile from './UserProfile';

const MainPage = () => {
  const { user, userProfile } = useUser();
  const [showForm, setShowForm] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [formData, setFormData] = useState({
    birth_year: '',
    birth_month: '',
    birth_day: '',
    birth_hour: '',
    name: '',
    gender: 'male'
  });
  const [result, setResult] = useState<any>(null);
  const [predictedNumbers, setPredictedNumbers] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // 예측 번호 생성 함수
  const handlePredict = async () => {
    setPredictionLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://127.0.0.1:4004/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          birth_year: parseInt(formData.birth_year),
          birth_month: parseInt(formData.birth_month),
          birth_day: parseInt(formData.birth_day),
          birth_hour: parseInt(formData.birth_hour),
          name: formData.name ? encodeURIComponent(formData.name) : 'User'
        }),
      });
      
      if (!response.ok) {
        throw new Error('예측 생성에 실패했습니다');
      }
      
      const predictionResult = await response.json();
      setPredictedNumbers(predictionResult);
      
    } catch (error: any) {
      console.error('예측 오류:', error);
      setError('예측 번호 생성 중 오류가 발생했습니다: ' + error.message);
    } finally {
      setPredictionLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // 바로 예측 API 호출 (사용자 생성 없이 간단하게)
      const response = await fetch('http://127.0.0.1:4004/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          birth_year: parseInt(formData.birth_year),
          birth_month: parseInt(formData.birth_month),
          birth_day: parseInt(formData.birth_day),
          birth_hour: parseInt(formData.birth_hour),
          name: formData.name ? encodeURIComponent(formData.name) : 'User'
        }),
      });
      
      if (!response.ok) {
        throw new Error('예측 생성에 실패했습니다');
      }
      
      const predictionResult = await response.json();
      setPredictedNumbers(predictionResult);
      setResult({ 
        name: formData.name || '사용자',
        birth_ymdh: `${formData.birth_year}-${formData.birth_month}-${formData.birth_day} ${formData.birth_hour}시`,
        oheng_json: predictionResult.saju_elements
      });
      
    } catch (error: any) {
      console.error('예측 오류:', error);
      setError('예측 번호 생성 중 오류가 발생했습니다: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* 애니메이션 스타일 */}
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
        }
        
        .number-ball {
          animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .number-ball:hover {
          animation: pulse 0.3s ease-in-out;
        }
      `}</style>
      
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-md mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">사주로또</h1>
                <p className="text-xs text-slate-500">운명과 행운의 만남</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Link 
                href="/analysis"
                className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
                title="로또 데이터 분석"
              >
                <BarChart3 className="w-5 h-5 text-slate-600" />
              </Link>
              
              {user ? (
                <button
                  onClick={() => setShowProfileModal(true)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-slate-100 transition-colors"
                  title="내 프로필"
                >
                  <User className="w-5 h-5 text-slate-600" />
                  <span className="text-xs font-medium text-slate-600 hidden sm:block">
                    {user.name || '프로필'}
                  </span>
                </button>
              ) : (
                <button
                  onClick={() => {
                    console.log('Login button clicked');
                    setShowAuthModal(true);
                  }}
                  className="px-3 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                >
                  로그인
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-4 py-8">
        <div className="max-w-md mx-auto text-center">
          <div className="relative mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
              <Star className="w-10 h-10 text-white" />
            </div>
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <Sparkles className="w-3 h-3 text-white" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            당신만의 행운 번호를
          </h2>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600 mb-4">
            사주로 찾아보세요
          </h3>
          <p className="text-slate-600 mb-6 leading-relaxed">
            전통 사주학과 AI가 만나 당신의 운세에 맞는<br />
            개인 맞춤형 로또 번호를 예측합니다
          </p>
          <button 
            onClick={() => {
              console.log('Button clicked! User:', user);
              if (!user) {
                console.log('Opening auth modal');
                setShowAuthModal(true);
              } else {
                console.log('Opening form');
                setShowForm(true);
              }
            }}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200"
          >
            🎯 행운 번호 예측하기
            <Sparkles className="inline-block w-5 h-5 ml-2" />
          </button>
          
          {!user && (
            <div className="mt-3 text-center">
              <p className="text-sm text-slate-500">
                로그인하고 나만의 예측 기록을 관리하세요
              </p>
            </div>
          )}
        </div>
      </section>

      {/* 에러 메시지 */}
      {error && (
        <section className="px-4 py-4">
          <div className="max-w-md mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
                <div className="ml-auto pl-3">
                  <button 
                    onClick={() => setError(null)}
                    className="text-red-400 hover:text-red-600"
                  >
                    <span className="sr-only">닫기</span>
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 사주 입력 폼 */}
      {showForm && !result && (
        <section className="px-4 py-8 bg-white">
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-bold text-slate-800 mb-6 text-center">사주 정보 입력</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">이름</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="홍길동"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">성별</label>
                <select
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="male">남성</option>
                  <option value="female">여성</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">생년</label>
                  <input
                    type="number"
                    name="birth_year"
                    value={formData.birth_year}
                    onChange={handleInputChange}
                    required
                    min="1900"
                    max="2024"
                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="1990"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">생월</label>
                  <input
                    type="number"
                    name="birth_month"
                    value={formData.birth_month}
                    onChange={handleInputChange}
                    required
                    min="1"
                    max="12"
                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="5"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">생일</label>
                  <input
                    type="number"
                    name="birth_day"
                    value={formData.birth_day}
                    onChange={handleInputChange}
                    required
                    min="1"
                    max="31"
                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="15"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">생시</label>
                  <input
                    type="number"
                    name="birth_hour"
                    value={formData.birth_hour}
                    onChange={handleInputChange}
                    required
                    min="0"
                    max="23"
                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    placeholder="10"
                  />
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 bg-slate-200 text-slate-700 py-3 rounded-lg font-medium hover:bg-slate-300 transition-colors"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {loading ? '예측 생성 중...' : '🎯 번호 예측하기'}
                </button>
              </div>
            </form>
          </div>
        </section>
      )}

      {/* 예측 결과 */}
      {result && predictedNumbers && (
        <section className="px-4 py-8 bg-gradient-to-br from-purple-50 to-blue-50">
          <div className="max-w-md mx-auto space-y-6">
            
            {/* 예측 번호 메인 표시 */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-purple-100">
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-slate-800 mb-2">🎯 당신의 행운 번호</h3>
                <p className="text-slate-600">{result.name}님을 위한 맞춤 예측</p>
              </div>

              {/* 로또 번호 7개 */}
              <div className="flex items-center justify-center space-x-1 mb-6">
                {predictedNumbers.predicted_numbers.map((number: number, index: number) => (
                  <div
                    key={index}
                    className="w-11 h-11 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-base shadow-lg transform hover:scale-105 transition-transform duration-200"
                    style={{
                      animationDelay: `${index * 0.1}s`,
                      animation: 'fadeInUp 0.6s ease-out forwards'
                    }}
                  >
                    {number}
                  </div>
                ))}
              </div>

              {/* 신뢰도 표시 */}
              <div className="text-center mb-6">
                <div className="inline-flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-700 font-medium">
                    신뢰도: {Math.round(predictedNumbers.confidence * 100)}%
                  </span>
                </div>
              </div>

              {/* 예측 방법 */}
              <div className="text-center text-sm text-slate-500 mb-6">
                예측 방법: 사주 오행 가중치 + 통계 분석
              </div>
            </div>

            {/* 사주 분석 상세 */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-purple-100">
              <h4 className="text-lg font-bold text-purple-600 mb-4 text-center">사주 분석 결과</h4>
              
              <div className="text-center mb-6">
                <p className="text-slate-600 font-medium">{formData.birth_year}-{formData.birth_month.padStart(2, '0')}-{formData.birth_day.padStart(2, '0')} {formData.birth_hour.padStart(2, '0')}시</p>
                {predictedNumbers.saju_analysis?.lunar_info && (
                  <p className="text-xs text-slate-500 mt-1">
                    음력: {predictedNumbers.saju_analysis.lunar_info.year}-{predictedNumbers.saju_analysis.lunar_info.month}-{predictedNumbers.saju_analysis.lunar_info.day}
                  </p>
                )}
              </div>

              {/* 사주팔자 표시 */}
              {predictedNumbers.saju_analysis?.raw_result?.saju && (
                <div className="mb-6">
                  <h5 className="text-md font-semibold text-slate-800 mb-3 text-center">사주팔자 (四柱八字)</h5>
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border">
                    <div className="grid grid-cols-4 gap-3 text-center">
                      <div className="space-y-2">
                        <div className="text-xs text-slate-500 font-medium">년주</div>
                        <div className="bg-white p-2 rounded-md shadow-sm">
                          <div className="text-lg font-bold text-purple-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.year[0]}
                          </div>
                          <div className="text-sm text-slate-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.year[1]}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs text-slate-500 font-medium">월주</div>
                        <div className="bg-white p-2 rounded-md shadow-sm">
                          <div className="text-lg font-bold text-purple-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.month[0]}
                          </div>
                          <div className="text-sm text-slate-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.month[1]}
                          </div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs text-slate-500 font-medium">일주</div>
                        <div className="bg-white p-2 rounded-md shadow-sm border-2 border-purple-200">
                          <div className="text-lg font-bold text-purple-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.day[0]}
                          </div>
                          <div className="text-sm text-slate-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.day[1]}
                          </div>
                        </div>
                        <div className="text-xs text-purple-500 font-medium">본인</div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-xs text-slate-500 font-medium">시주</div>
                        <div className="bg-white p-2 rounded-md shadow-sm">
                          <div className="text-lg font-bold text-purple-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.hour[0]}
                          </div>
                          <div className="text-sm text-slate-600">
                            {predictedNumbers.saju_analysis.raw_result.saju.hour[1]}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 text-center">
                      <div className="flex justify-center space-x-8 text-xs text-slate-500">
                        <span>천간</span>
                        <span>지지</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 오행 분포 */}
              <div className="mb-6">
                <h5 className="text-md font-semibold text-slate-800 mb-3">오행 분포 (사주의 기본 에너지)</h5>
                <p className="text-xs text-slate-500 mb-3">
                  목(나무): 성장·발전 | 화(불): 열정·창조 | 토(흙): 안정·포용 | 금(금속): 결단·완성 | 수(물): 지혜·유연
                </p>
                <div className="grid grid-cols-5 gap-2">
                  {predictedNumbers.saju_analysis?.oheang && Object.entries(predictedNumbers.saju_analysis.oheang).map(([element, count]) => (
                    <div key={element} className="text-center p-3 bg-slate-50 rounded-lg">
                      <div className="text-lg font-bold text-purple-600">{count as number}</div>
                      <div className="text-sm text-slate-600">{element}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 번호 생성 시간 */}
              <div className="text-center text-xs text-slate-400">
                생성 시간: {new Date(predictedNumbers.generated_at).toLocaleString('ko-KR')}
              </div>
            </div>

            {/* 번호별 사주 풀이 */}
            {predictedNumbers.number_scores && predictedNumbers.number_scores.length > 0 && (
              <div className="bg-white p-6 rounded-xl shadow-lg border border-purple-100">
                <h4 className="text-lg font-bold text-purple-600 mb-4 text-center">번호별 사주 풀이</h4>
                <div className="space-y-4">
                  {predictedNumbers.number_scores
                    .filter(score => predictedNumbers.predicted_numbers.includes(score.number))
                    .sort((a, b) => (b.compatibility || 0) - (a.compatibility || 0))
                    .map((numberInfo: any, index: number) => {
                      // 한글 사주 설명 생성
                      const elementNames = {
                        '목': '나무',
                        '화': '불',
                        '토': '흙', 
                        '금': '금속',
                        '수': '물'
                      };
                      
                      const elementTraits = {
                        '목': '성장운',
                        '화': '열정운',
                        '토': '안정운',
                        '금': '결단운',
                        '수': '지혜운'
                      };

                      const elemName = elementNames[numberInfo.element] || numberInfo.element;
                      const trait = elementTraits[numberInfo.element] || '특별운';
                      
                      // 사주 오행 분포에서 해당 원소 개수 확인
                      const userElementCount = predictedNumbers.saju_analysis?.oheang?.[numberInfo.element] || 0;
                      
                      let reason;
                      if (userElementCount >= 2) {
                        reason = `${elemName} 기운이 강함`;
                      } else if (userElementCount >= 1) {
                        reason = `${elemName} 기운과 조화`;
                      } else {
                        reason = `${elemName} 기운 보완`;
                      }
                      
                      const koreanExplanation = `${trait}의 ${numberInfo.number}번 - ${reason}`;

                    return (
                      <div key={numberInfo.number} className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                              {numberInfo.number}
                            </div>
                            <div>
                              <span className="text-sm text-slate-500">
                                {index + 1}위 추천
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-purple-600">
                              적합도 {numberInfo.compatibility || 0}%
                            </div>
                            <div className="text-xs text-slate-500">
                              {numberInfo.element || '미분류'} 원소
                            </div>
                          </div>
                        </div>
                        <p className="text-sm text-slate-700 leading-relaxed">
                          {koreanExplanation}
                        </p>
                        <div className="mt-2 flex justify-between text-xs text-slate-500">
                          <span>출현빈도: {numberInfo.frequency || 0}회</span>
                          <span>가중치: {(numberInfo.weight || 1).toFixed(2)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 액션 버튼들 */}
            <div className="space-y-3">
              <button
                onClick={() => {
                  // 새로운 예측 생성
                  handleSubmit({ preventDefault: () => {} } as any);
                }}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-teal-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50"
              >
                {loading ? '새 번호 생성 중...' : '🔄 새로운 번호 생성'}
              </button>
              
              <button
                onClick={() => {
                  setResult(null);
                  setPredictedNumbers(null);
                  setShowForm(false);
                  setError(null);
                  setFormData({
                    birth_year: '',
                    birth_month: '',
                    birth_day: '',
                    birth_hour: '',
                    name: '',
                    gender: 'male'
                  });
                }}
                className="w-full bg-slate-200 text-slate-700 py-3 rounded-lg font-medium hover:bg-slate-300 transition-colors"
              >
                다른 사주로 분석하기
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Features Grid */}
      <section className="px-4 py-8 bg-white">
        <div className="max-w-md mx-auto">
          <h3 className="text-lg font-bold text-slate-800 mb-6 text-center">주요 서비스</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-4 rounded-xl border border-purple-100">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                <Star className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-1">사주 분석</h4>
              <p className="text-sm text-slate-600">정확한 사주팔자 분석으로 오행 에너지 파악</p>
            </div>
            <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-xl border border-orange-100">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-1">AI 예측</h4>
              <p className="text-sm text-slate-600">머신러닝 기반 개인 맞춤형 번호 추천</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-br from-green-50 to-teal-50 p-4 rounded-xl border border-green-100">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-3">
                <Award className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-1">당첨 관리</h4>
              <p className="text-sm text-slate-600">예측 기록 관리 및 당첨 결과 확인</p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-100">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-slate-800 mb-1">운세 달력</h4>
              <p className="text-sm text-slate-600">일별 운세와 추천 구매 타이밍</p>
            </div>
          </div>
        </div>
      </section>

      {/* Latest Numbers */}
      <section className="px-4 py-8 bg-slate-50">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-slate-800">최근 당첨번호</h3>
            <span className="text-sm text-slate-500">1298회</span>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center justify-center space-x-3 mb-4">
              {[7, 15, 23, 31, 39, 42].map((number: number, index: number) => (
                <div
                  key={index}
                  className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg"
                >
                  {number}
                </div>
              ))}
              <div className="w-px h-6 bg-slate-300 mx-2"></div>
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
                18
              </div>
            </div>
            <div className="text-center">
              <p className="text-sm text-slate-600">추첨일: 2024.01.13 (토)</p>
              <p className="text-xs text-slate-500 mt-1">1등 당첨금: 22억 3,456만원</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="px-4 py-8 bg-white">
        <div className="max-w-md mx-auto">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-4">
              <div className="text-2xl font-bold text-purple-600 mb-1">15,432</div>
              <div className="text-sm text-slate-600">예측 생성</div>
            </div>
            <div className="p-4 border-x border-slate-200">
              <div className="text-2xl font-bold text-blue-600 mb-1">89%</div>
              <div className="text-sm text-slate-600">만족도</div>
            </div>
            <div className="p-4">
              <div className="text-2xl font-bold text-green-600 mb-1">2,341</div>
              <div className="text-sm text-slate-600">당첨 사례</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-8 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-md mx-auto text-center text-white">
          <h3 className="text-xl font-bold mb-2">지금 시작해보세요</h3>
          <p className="text-purple-100 mb-6">당신의 운명적 번호를 찾아보세요</p>
          <button className="w-full bg-white text-purple-600 py-4 rounded-xl font-semibold text-lg hover:bg-purple-50 transition-colors duration-200">
            무료로 시작하기
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-800 text-white px-4 py-8">
        <div className="max-w-md mx-auto">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold">사주로또</span>
          </div>
          <div className="grid grid-cols-2 gap-8 mb-6 text-sm text-slate-300">
            <div>
              <h4 className="font-semibold text-white mb-2">서비스</h4>
              <ul className="space-y-1">
                <li>사주 분석</li>
                <li>번호 예측</li>
                <li>당첨 확인</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">고객지원</h4>
              <ul className="space-y-1">
                <li>FAQ</li>
                <li>문의하기</li>
                <li>이용약관</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-700 pt-4 text-xs text-slate-400 text-center">
            <p>© 2024 사주로또. All rights reserved.</p>
            <p className="mt-1">책임감 있는 복권 구매를 권장합니다.</p>
          </div>
        </div>
      </footer>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={(userData) => {
          // 로그인/회원가입 성공 후 예측 폼으로 자동 이동
          setShowForm(true);
        }}
        onRegistrationSuccess={() => {
          // 회원가입 완료 시 추가 처리
          setRegistrationSuccess(true);
        }}
      />

      {/* User Profile Modal */}
      <UserProfile
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </>
  );
};

export default MainPage;