'use client';

import React, { useState } from 'react';
import { Star, Sparkles, TrendingUp, Users, Award, Calendar, BarChart3, Brain, Menu, X } from 'lucide-react';
import Link from 'next/link';
import AIPrediction from './AIPrediction';

const MainPage = () => {
  const [activeView, setActiveView] = useState('home'); // 'home', 'ai'
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-3">
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
            
            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-4">
              <button
                onClick={() => setActiveView('home')}
                className={`px-3 py-2 rounded-lg font-medium transition-colors ${
                  activeView === 'home' 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
                }`}
              >
                홈
              </button>
              <button
                onClick={() => setActiveView('ai')}
                className={`px-3 py-2 rounded-lg font-medium transition-colors flex items-center ${
                  activeView === 'ai' 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
                }`}
              >
                <Brain className="w-4 h-4 mr-1" />
                번호 예측
              </button>
              <Link 
                href="/analysis"
                className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
                title="로또 데이터 분석"
              >
                <BarChart3 className="w-5 h-5 text-slate-600" />
              </Link>
            </nav>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="md:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors"
            >
              {showMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Navigation Menu */}
          {showMenu && (
            <div className="md:hidden mt-3 pt-3 border-t border-slate-200">
              <nav className="space-y-2">
                <button
                  onClick={() => {
                    setActiveView('home');
                    setShowMenu(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                    activeView === 'home' 
                      ? 'bg-purple-100 text-purple-700' 
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
                  }`}
                >
                  홈
                </button>
                <button
                  onClick={() => {
                    setActiveView('ai');
                    setShowMenu(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors flex items-center ${
                    activeView === 'ai' 
                      ? 'bg-purple-100 text-purple-700' 
                      : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100'
                  }`}
                >
                  <Brain className="w-4 h-4 mr-2" />
                  번호 예측
                </button>
                <Link 
                  href="/analysis"
                  className="w-full text-left px-3 py-2 rounded-lg font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 transition-colors flex items-center"
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  데이터 분석
                </Link>
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      {activeView === 'ai' && (
        <AIPrediction />
      )}
      
      {activeView === 'home' && (
        <div>
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
              <div className="space-y-3">
                <button 
                  onClick={() => setActiveView('ai')}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-200"
                >
                  🤖 AI 사주 예측하기
                  <Brain className="inline-block w-5 h-5 ml-2" />
                </button>
                <div className="text-center">
                  <p className="text-sm text-gray-500">
                    고급 AI가 당신의 사주를 분석하여 맞춤 번호를 예측합니다
                  </p>
                </div>
              </div>
            </div>
          </section>




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
                  <p className="text-sm text-slate-600">고급 AI 시스템이 개인 맞춤형 번호 추천</p>
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
                  {[7, 15, 23, 31, 39, 42].map((number, index) => (
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
      )}
    </div>
  );
};

export default MainPage;