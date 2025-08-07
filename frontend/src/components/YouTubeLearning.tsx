'use client';

import React, { useState, useEffect } from 'react';
import { 
  Youtube, 
  Brain, 
  TrendingUp, 
  Search, 
  Plus, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  BookOpen,
  Zap,
  Database
} from 'lucide-react';

interface YouTubeLearningProps {
  isAdmin?: boolean;
}

interface KnowledgeSummary {
  total_knowledge_entries: number;
  total_videos_processed: number;
  sentence_type_distribution: Record<string, number>;
  average_confidence: number;
  database_path: string;
}

interface KnowledgeItem {
  video_id: string;
  video_title: string;
  content: string;
  saju_terms: Record<string, string[]>;
  sentence_type: string;
  confidence: number;
  created_at: string;
}

const YouTubeLearning = ({ isAdmin = false }: YouTubeLearningProps) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'learn' | 'search' | 'status'>('overview');
  const [videoId, setVideoId] = useState('');
  const [batchVideoIds, setBatchVideoIds] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [summary, setSummary] = useState<KnowledgeSummary | null>(null);
  const [searchResults, setSearchResults] = useState<KnowledgeItem[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null);

  // 지식 요약 로드
  const loadSummary = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/youtube/knowledge/summary', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSummary(data.data);
      }
    } catch (error) {
      console.error('요약 로드 실패:', error);
    }
  };

  // 시스템 상태 로드
  const loadSystemStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/youtube/system/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data.data);
      }
    } catch (error) {
      console.error('상태 로드 실패:', error);
    }
  };

  // 단일 영상 학습
  const learnFromVideo = async () => {
    if (!videoId.trim()) {
      setMessage({ type: 'error', text: '영상 ID를 입력해주세요.' });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/youtube/learn/single', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId.trim() }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `학습 완료! ${data.data.learned_sentences}개 문장 학습됨` 
        });
        setVideoId('');
        loadSummary(); // 요약 업데이트
      } else {
        setMessage({ type: 'error', text: data.detail || '학습 실패' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '네트워크 오류가 발생했습니다.' });
    } finally {
      setIsLoading(false);
    }
  };

  // 일괄 영상 학습
  const learnFromMultipleVideos = async () => {
    const videoIds = batchVideoIds.split(',').map(id => id.trim()).filter(id => id);
    
    if (videoIds.length === 0) {
      setMessage({ type: 'error', text: '영상 ID들을 입력해주세요.' });
      return;
    }

    if (videoIds.length > 20) {
      setMessage({ type: 'error', text: '한 번에 최대 20개까지만 학습 가능합니다.' });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/youtube/learn/batch', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_ids: videoIds }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `${videoIds.length}개 영상 일괄 학습이 백그라운드에서 시작되었습니다.` 
        });
        setBatchVideoIds('');
        setTimeout(() => loadSummary(), 5000); // 5초 후 요약 업데이트
      } else {
        setMessage({ type: 'error', text: data.detail || '일괄 학습 실패' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '네트워크 오류가 발생했습니다.' });
    } finally {
      setIsLoading(false);
    }
  };

  // 지식 검색
  const searchKnowledge = async () => {
    if (!searchQuery.trim()) {
      setMessage({ type: 'error', text: '검색어를 입력해주세요.' });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/youtube/knowledge/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery.trim(), limit: 10 }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setSearchResults(data.data);
        setMessage({ 
          type: 'info', 
          text: `'${searchQuery}' 검색 결과 ${data.data.length}개 발견` 
        });
      } else {
        setMessage({ type: 'error', text: data.detail || '검색 실패' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '네트워크 오류가 발생했습니다.' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
    loadSystemStatus();
  }, []);

  // YouTube URL에서 Video ID 추출 헬퍼
  const extractVideoId = (url: string): string => {
    const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : url;
  };

  const handleVideoIdChange = (value: string) => {
    const extractedId = extractVideoId(value);
    setVideoId(extractedId);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-gradient-to-r from-red-600 to-purple-600 rounded-lg p-6 text-white mb-6">
        <div className="flex items-center">
          <Youtube className="w-8 h-8 mr-3" />
          <div>
            <h1 className="text-2xl font-bold">YouTube 학습 시스템</h1>
            <p className="opacity-90">YouTube 영상에서 사주 지식을 학습하고 예측을 향상시킵니다</p>
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

      {/* 탭 네비게이션 */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
        {[
          { id: 'overview', label: '개요', icon: TrendingUp },
          ...(isAdmin ? [
            { id: 'learn', label: '학습', icon: Brain },
            { id: 'search', label: '검색', icon: Search },
            { id: 'status', label: '상태', icon: Database }
          ] : [
            { id: 'search', label: '검색', icon: Search }
          ])
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <tab.icon className="w-4 h-4 mr-2" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* 개요 탭 */}
      {activeTab === 'overview' && summary && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <BookOpen className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-blue-700">
                    {summary.total_knowledge_entries.toLocaleString()}
                  </div>
                  <div className="text-sm text-blue-600">학습된 지식</div>
                </div>
              </div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center">
                <Youtube className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-green-700">
                    {summary.total_videos_processed.toLocaleString()}
                  </div>
                  <div className="text-sm text-green-600">처리된 영상</div>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center">
                <Zap className="w-8 h-8 text-purple-600 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-purple-700">
                    {(summary.average_confidence * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-purple-600">평균 신뢰도</div>
                </div>
              </div>
            </div>

            <div className="bg-orange-50 rounded-lg p-4">
              <div className="flex items-center">
                <Brain className="w-8 h-8 text-orange-600 mr-3" />
                <div>
                  <div className="text-2xl font-bold text-orange-700">
                    {Object.keys(summary.sentence_type_distribution).length}
                  </div>
                  <div className="text-sm text-orange-600">문장 유형</div>
                </div>
              </div>
            </div>
          </div>

          {/* 문장 유형별 분포 */}
          {Object.keys(summary.sentence_type_distribution).length > 0 && (
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">학습된 내용 분포</h3>
              <div className="space-y-2">
                {Object.entries(summary.sentence_type_distribution).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="capitalize text-gray-700">{type}</span>
                    <span className="font-medium text-gray-900">{count.toLocaleString()}개</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 학습 탭 (관리자만) */}
      {activeTab === 'learn' && isAdmin && (
        <div className="space-y-6">
          {/* 단일 영상 학습 */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Plus className="w-5 h-5 mr-2" />
              단일 영상 학습
            </h3>
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="YouTube URL 또는 영상 ID 입력"
                  value={videoId}
                  onChange={(e) => handleVideoIdChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  예: https://youtube.com/watch?v=VIDEO_ID 또는 VIDEO_ID
                </p>
              </div>
              <button
                onClick={learnFromVideo}
                disabled={isLoading}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center"
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
                학습하기
              </button>
            </div>
          </div>

          {/* 일괄 영상 학습 */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Youtube className="w-5 h-5 mr-2" />
              일괄 영상 학습
            </h3>
            <div className="space-y-4">
              <textarea
                placeholder="영상 ID들을 쉼표로 구분하여 입력 (최대 20개)&#10;예: VIDEO_ID1, VIDEO_ID2, VIDEO_ID3"
                value={batchVideoIds}
                onChange={(e) => setBatchVideoIds(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={learnFromMultipleVideos}
                disabled={isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
                일괄 학습하기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 검색 탭 */}
      {activeTab === 'search' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border p-6">
            <div className="flex space-x-4 mb-6">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="사주 관련 검색어 입력 (예: 갑목, 건강, 성격)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchKnowledge()}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
              <button
                onClick={searchKnowledge}
                disabled={isLoading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
              >
                {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
                검색
              </button>
            </div>

            {/* 검색 결과 */}
            <div className="space-y-4">
              {searchResults.map((item, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-800 truncate flex-1 mr-4">
                      {item.video_title || '제목 없음'}
                    </h4>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {item.sentence_type}
                      </span>
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                        {(item.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-700 mb-2">{item.content}</p>
                  {Object.keys(item.saju_terms).length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(item.saju_terms).map(([category, terms]) => 
                        terms.map((term) => (
                          <span key={`${category}-${term}`} className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                            {term}
                          </span>
                        ))
                      )}
                    </div>
                  )}
                </div>
              ))}
              
              {searchResults.length === 0 && searchQuery && (
                <div className="text-center text-gray-500 py-8">
                  검색 결과가 없습니다. 다른 검색어를 시도해보세요.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 상태 탭 (관리자만) */}
      {activeTab === 'status' && isAdmin && systemStatus && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* 라이브러리 상태 */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">라이브러리 상태</h3>
              <div className="space-y-2">
                {Object.entries(systemStatus.library_status).map(([lib, status]) => (
                  <div key={lib} className="flex justify-between items-center">
                    <span className="text-gray-700">{lib}</span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {status ? '설치됨' : '미설치'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 기능 상태 */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">사용 가능한 기능</h3>
              <div className="space-y-2">
                {Object.entries(systemStatus.features_available).map(([feature, available]) => (
                  <div key={feature} className="flex justify-between items-center">
                    <span className="text-gray-700 capitalize">{feature.replace('_', ' ')}</span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      available ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {available ? '사용 가능' : '제한됨'}
                    </span>
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

export default YouTubeLearning;