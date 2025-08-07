'use client';

import React from 'react';

interface SajuPillar {
  gan: string;
  gan_hanja: string;
  ji: string;
  ji_hanja: string;
  gan_yinyang: string;
  ji_yinyang: string;
  gan_element: string;
  ji_element: string;
}

interface SajuPillarsProps {
  pillars: {
    year: SajuPillar;
    month: SajuPillar;
    day: SajuPillar;
    hour: SajuPillar;
  };
}

const SajuPillars = ({ pillars }: SajuPillarsProps) => {
  if (!pillars) return null;
  
  // 디버깅용 로그
  console.log('사주팔자 데이터:', pillars);

  // 오행별 색상 정의 (음양 텍스트를 위해 조정)
  const getElementColor = (element: string) => {
    switch (element) {
      case '목': return '#7CB342'; // 좀 더 어두운 녹색
      case '화': return '#E53E3E'; // 좀 더 어두운 빨간색
      case '토': return '#D69E2E'; // 좀 더 어두운 노란색
      case '금': return '#A0AEC0'; // 좀 더 어두운 회색
      case '수': return '#3182CE'; // 좀 더 어두운 파란색
      default: return '#E6E9ED';
    }
  };

  // 텍스트 색상 결정 (음양에 따라)
  const getTextColorByYinyang = (yinyang: string, element: string) => {
    // 모든 오행에 대해 동일한 규칙 적용
    if (yinyang === '양') {
      return '#FFFFFF'; // 양은 흰색 텍스트
    } else {
      return '#1A1A1A'; // 음은 검정색 텍스트  
    }
  };

  // 오행 아이콘 이모지
  const getElementIcon = (element: string) => {
    switch (element) {
      case '목': return '🌳';
      case '화': return '🔥';
      case '토': return '⛰️';
      case '금': return '⚔️';
      case '수': return '💧';
      default: return '';
    }
  };

  // 각 칸 렌더링 함수
  const renderCell = (hanja: string, korean: string, element: string, yinyang: string) => {
    const bgColor = getElementColor(element);
    const textColor = getTextColorByYinyang(yinyang, element);
    const icon = getElementIcon(element);
    
    // 디버깅용 로그
    console.log(`${hanja}(${korean}): 오행=${element}, 음양=${yinyang}, 색상=${textColor}`);
    
    return (
      <div 
        className="relative flex flex-col items-center justify-center h-24 rounded-lg shadow-md transition-transform hover:scale-105"
        style={{ backgroundColor: bgColor, color: textColor }}
      >
        <div className="text-3xl font-bold mb-1">{hanja}</div>
        <div className="text-sm">{korean}</div>
        <div className="absolute bottom-1 right-1 text-xs opacity-70">{icon}</div>
      </div>
    );
  };

  // 순서: 시주, 일주, 월주, 년주
  const orderedPillars = [
    { pillar: pillars.hour, label: '시주', sublabel: '(時柱)' },
    { pillar: pillars.day, label: '일주', sublabel: '(日柱)' },
    { pillar: pillars.month, label: '월주', sublabel: '(月柱)' },
    { pillar: pillars.year, label: '년주', sublabel: '(年柱)' }
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">
        사주팔자 (四柱八字)
      </h3>
      
      {/* 2행 4열 그리드 */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              {orderedPillars.map((item, idx) => (
                <th key={idx} className="pb-3 text-center">
                  <div className="text-sm font-semibold text-gray-700">{item.label}</div>
                  <div className="text-xs text-gray-500">{item.sublabel}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* 천간 행 */}
            <tr>
              <td colSpan={4} className="pb-2">
                <div className="text-xs text-gray-500 text-center mb-1">천간</div>
              </td>
            </tr>
            <tr>
              {orderedPillars.map((item, idx) => (
                <td key={idx} className="px-2 pb-4">
                  {renderCell(
                    item.pillar.gan_hanja,
                    item.pillar.gan,
                    item.pillar.gan_element,
                    item.pillar.gan_yinyang
                  )}
                </td>
              ))}
            </tr>
            
            {/* 지지 행 */}
            <tr>
              <td colSpan={4} className="pb-2">
                <div className="text-xs text-gray-500 text-center mb-1">지지</div>
              </td>
            </tr>
            <tr>
              {orderedPillars.map((item, idx) => (
                <td key={idx} className="px-2">
                  {renderCell(
                    item.pillar.ji_hanja,
                    item.pillar.ji,
                    item.pillar.ji_element,
                    item.pillar.ji_yinyang
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* 범례 */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        {/* 음양 범례 - 텍스트 색상으로 표시 */}
        <div className="flex justify-center items-center space-x-6 mb-3">
          <div className="flex items-center">
            <div className="w-6 h-6 rounded bg-gray-600 mr-2 flex items-center justify-center">
              <span className="text-white text-xs font-bold">양</span>
            </div>
            <span className="text-sm text-gray-600">양(陽) - 흰색 텍스트</span>
          </div>
          <div className="flex items-center">
            <div className="w-6 h-6 rounded bg-gray-300 mr-2 flex items-center justify-center">
              <span className="text-black text-xs font-bold">음</span>
            </div>
            <span className="text-sm text-gray-600">음(陰) - 검정색 텍스트</span>
          </div>
        </div>
        
        {/* 오행 범례 */}
        <div className="flex justify-center flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-1" style={{ backgroundColor: '#7CB342' }}></div>
            <span className="text-gray-600">🌳 목(木)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-1" style={{ backgroundColor: '#E53E3E' }}></div>
            <span className="text-gray-600">🔥 화(火)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-1" style={{ backgroundColor: '#D69E2E' }}></div>
            <span className="text-gray-600">⛰️ 토(土)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-1" style={{ backgroundColor: '#A0AEC0' }}></div>
            <span className="text-gray-600">⚔️ 금(金)</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-1" style={{ backgroundColor: '#3182CE' }}></div>
            <span className="text-gray-600">💧 수(水)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SajuPillars;