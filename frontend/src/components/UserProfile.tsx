'use client';

import React, { useState } from 'react';
import { User, Calendar, Star, TrendingUp, LogOut, Settings, X } from 'lucide-react';
import { useUser } from '../contexts/UserContext';

interface UserProfileProps {
  isOpen: boolean;
  onClose: () => void;
}

const UserProfile = ({ isOpen, onClose }: UserProfileProps) => {
  const { user, userProfile, logout } = useUser();

  if (!isOpen || !user) return null;

  const handleLogout = () => {
    logout();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">내 프로필</h2>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* User Info */}
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-800">{user.name || '사용자'}</h3>
            <p className="text-gray-600 text-sm">{user.email}</p>
            <div className="flex items-center justify-center mt-2 text-xs text-gray-500">
              <Calendar className="w-4 h-4 mr-1" />
              가입일: {new Date(user.created_at).toLocaleDateString('ko-KR')}
            </div>
          </div>

          {/* Stats */}
          {userProfile && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-purple-50 rounded-xl p-4 text-center">
                <TrendingUp className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-purple-700">{userProfile.prediction_count}</div>
                <div className="text-sm text-purple-600">총 예측 횟수</div>
              </div>
              <div className="bg-blue-50 rounded-xl p-4 text-center">
                <Star className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-700">
                  {userProfile.saju_profile ? '완료' : '미완료'}
                </div>
                <div className="text-sm text-blue-600">사주 분석</div>
              </div>
            </div>
          )}

          {/* Saju Profile */}
          {userProfile?.saju_profile ? (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-4">
              <div className="flex items-center mb-2">
                <Star className="w-5 h-5 text-green-600 mr-2" />
                <h4 className="font-semibold text-gray-800">사주 프로필</h4>
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <p>생년월일: {userProfile.saju_profile.birth_ymdh}</p>
                <p>성별: {userProfile.saju_profile.gender === 'male' ? '남성' : '여성'}</p>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <div className="flex items-center mb-2">
                <Settings className="w-5 h-5 text-yellow-600 mr-2" />
                <h4 className="font-semibold text-gray-800">사주 프로필 필요</h4>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                정확한 예측을 위해 사주 프로필을 설정해주세요.
              </p>
              <button className="w-full bg-yellow-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-yellow-600 transition-colors">
                사주 프로필 설정하기
              </button>
            </div>
          )}

          {/* Last Login */}
          {user.last_login && (
            <div className="text-center text-xs text-gray-500">
              마지막 접속: {new Date(user.last_login).toLocaleString('ko-KR')}
            </div>
          )}

          {/* Actions */}
          <div className="space-y-3 pt-4 border-t border-gray-200">
            <button className="w-full flex items-center justify-center py-3 px-4 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
              <Settings className="w-5 h-5 mr-2 text-gray-600" />
              <span className="text-gray-700 font-medium">설정</span>
            </button>
            
            <button 
              onClick={handleLogout}
              className="w-full flex items-center justify-center py-3 px-4 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5 mr-2 text-red-600" />
              <span className="text-red-700 font-medium">로그아웃</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;