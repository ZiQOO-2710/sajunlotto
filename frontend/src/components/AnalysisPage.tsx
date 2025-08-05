'use client';

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { ArrowLeft, TrendingUp, PieChart as PieChartIcon, BarChart3, Calendar, Hash } from 'lucide-react';
import Link from 'next/link';

// 오행별 색상 정의
const ELEMENT_COLORS = {
  '목': '#22c55e', // green-500
  '화': '#ef4444', // red-500  
  '토': '#a3a3a3', // neutral-400
  '금': '#f59e0b', // amber-500
  '수': '#3b82f6'  // blue-500
};

// 히스토리컬 데이터 타입 정의
interface HistoricalData {
  total_draws: number;
  draw_range: string;
  top_numbers: { number: number; frequency: number }[];
  element_distribution: {
    [key: string]: {
      range: string;
      count: number;
      percentage: number;
    }
  };
  last_5_draws: {
    draw_no: number;
    numbers: number[];
    bonus: number;
    draw_date: string;
  }[];
}

const AnalysisPage = () => {
  const [data, setData] = useState<HistoricalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 데이터 로드
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:4002/analysis/historical');
        
        if (!response.ok) {
          throw new Error('데이터를 불러오는데 실패했습니다');
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 로딩 상태
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-slate-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">데이터 로드 실패</h2>
          <p className="text-slate-600 mb-4">{error}</p>
          <Link 
            href="/"
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            홈으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  // 오행 데이터를 파이차트용으로 변환
  const elementChartData = Object.entries(data.element_distribution).map(([element, info]) => ({
    name: element,
    value: info.count,
    percentage: info.percentage,
    fill: ELEMENT_COLORS[element as keyof typeof ELEMENT_COLORS]
  }));

  // 최빈 번호 데이터를 막대차트용으로 변환 (상위 10개만)
  const topNumbersChartData = data.top_numbers.slice(0, 10).map(item => ({
    number: item.number.toString(),
    frequency: item.frequency
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link 
              href="/"
              className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-6 h-6 text-slate-600" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">로또 데이터 분석</h1>
              <p className="text-slate-600">과거 당첨번호 패턴과 통계 분석</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        
        {/* 전체 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Hash className="w-5 h-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-slate-800">총 분석 회차</h3>
            </div>
            <p className="text-3xl font-bold text-blue-600">{data.total_draws}회</p>
            <p className="text-sm text-slate-500 mt-1">{data.draw_range}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <h3 className="font-semibold text-slate-800">최빈 번호</h3>
            </div>
            <p className="text-3xl font-bold text-green-600">{data.top_numbers[0].number}번</p>
            <p className="text-sm text-slate-500 mt-1">{data.top_numbers[0].frequency}회 출현</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Calendar className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-slate-800">분석 기간</h3>
            </div>
            <p className="text-xl font-bold text-purple-600">21주</p>
            <p className="text-sm text-slate-500 mt-1">2023.05 ~ 2023.06</p>
          </div>
        </div>

        {/* 최빈 번호 차트 */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-orange-100 rounded-lg">
              <BarChart3 className="w-5 h-5 text-orange-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800">자주 나온 번호 TOP 10</h3>
          </div>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topNumbersChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="number" 
                  stroke="#64748b"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#f8fafc', 
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    fontSize: '14px'
                  }}
                  formatter={(value) => [`${value}회`, '출현 횟수']}
                  labelFormatter={(label) => `${label}번`}
                />
                <Bar 
                  dataKey="frequency" 
                  fill="#8b5cf6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 오행별 분포 차트 */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <PieChartIcon className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-800">오행별 번호 분포</h3>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* 파이차트 */}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={elementChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    innerRadius={40}
                    dataKey="value"
                    label={({ name, percentage }) => `${name} ${percentage.toFixed(1)}%`}
                    labelLine={false}
                  >
                    {elementChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name) => [`${value}개`, `${name} (${elementChartData.find(d => d.name === name)?.percentage.toFixed(1)}%)`]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* 오행별 상세 정보 */}
            <div className="space-y-4">
              {Object.entries(data.element_distribution).map(([element, info]) => (
                <div key={element} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: ELEMENT_COLORS[element as keyof typeof ELEMENT_COLORS] }}
                    ></div>
                    <div>
                      <span className="font-semibold text-slate-800">{element}</span>
                      <span className="text-sm text-slate-500 ml-2">({info.range})</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-slate-800">{info.count}개</p>
                    <p className="text-sm text-slate-500">{info.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 최근 5회차 당첨번호 */}
        <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
          <h3 className="text-xl font-bold text-slate-800 mb-6">최근 5회차 당첨번호</h3>
          
          <div className="space-y-4">
            {data.last_5_draws.map((draw) => (
              <div key={draw.draw_no} className="p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="font-bold text-lg text-slate-800">{draw.draw_no}회</span>
                    <span className="text-sm text-slate-500 ml-3">
                      {new Date(draw.draw_date).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {draw.numbers.map((number, index) => (
                    <div
                      key={index}
                      className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm"
                    >
                      {number}
                    </div>
                  ))}
                  <div className="w-px h-6 bg-slate-300 mx-2"></div>
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {draw.bonus}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 하단 네비게이션 */}
        <div className="text-center">
          <Link 
            href="/"
            className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>홈으로 돌아가기</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;