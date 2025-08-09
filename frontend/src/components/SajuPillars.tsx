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
    five_elements?: {
      목: number;
      화: number;
      토: number;
      금: number;
      수: number;
    };
  };
}

const SajuPillars = ({ pillars }: SajuPillarsProps) => {
  if (!pillars) return null;
  
  // 디버깅용 로그
  console.log('사주팔자 데이터:', pillars);

  // 오행별 배경색 정의 (사용자 요구사항에 맞춰 조정)
  const getElementColor = (element: string) => {
    switch (element) {
      case '목': return '#22C55E'; // 녹색 (Green-500)
      case '화': return '#EF4444'; // 빨간색 (Red-500) 
      case '토': return '#EAB308'; // 노란색 (Yellow-500)
      case '금': return '#D1D5DB'; // 회백색 (Gray-300)
      case '수': return '#3B82F6'; // 파란색 (Blue-500)
      default: return '#E5E7EB';
    }
  };

  // 음양에 따른 텍스트 색상 결정
  const getTextColorByYinyang = (yinyang: string) => {
    return yinyang === '음' ? '#000000' : '#FFFFFF'; // 음은 검은색, 양은 흰색
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

  // 오행별 퍼센트 정보 가져오기
  const getElementPercentage = (element: string) => {
    if (!pillars.five_elements) return '';
    const percentage = pillars.five_elements[element as keyof typeof pillars.five_elements];
    return percentage ? `${percentage}%` : '';
  };

  // 각 칸 렌더링 함수
  const renderCell = (hanja: string, korean: string, element: string, yinyang: string) => {
    const bgColor = getElementColor(element);
    const textColor = getTextColorByYinyang(yinyang);
    const icon = getElementIcon(element);
    const percentage = getElementPercentage(element);
    
    // 디버깅용 로그
    console.log(`${hanja}(${korean}): 오행=${element}, 음양=${yinyang}, 색상=${textColor}, 퍼센트=${percentage}`);
    
    return (
      <div 
        className="relative flex flex-col items-center justify-center h-24 rounded-lg shadow-md transition-transform hover:scale-105"
        style={{ backgroundColor: bgColor, color: textColor }}
      >
        <div className="text-3xl font-bold mb-1">{hanja}</div>
        <div className="text-sm">{korean}</div>
        {percentage && (
          <div className="text-xs opacity-90 mt-1">{percentage}</div>
        )}
        <div className="absolute bottom-1 right-1 text-lg opacity-80">{icon}</div>
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

    </div>
  );
};

export default SajuPillars;