'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  email: string;
  name?: string;
  created_at: string;
  last_login?: string;
  is_active: boolean;
}

interface UserProfile extends User {
  saju_profile?: any;
  prediction_count: number;
}

interface UserContextType {
  user: User | null;
  userProfile: UserProfile | null;
  isLoading: boolean;
  login: (userData: User) => void;
  logout: () => void;
  updateProfile: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

interface UserProviderProps {
  children: React.ReactNode;
}

export const UserProvider = ({ children }: UserProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 컴포넌트 마운트 시 로컬 스토리지에서 사용자 정보 로드
  useEffect(() => {
    console.log('UserContext: Loading from localStorage');
    const storedUser = localStorage.getItem('user');
    console.log('UserContext: Stored user:', storedUser);
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        console.log('UserContext: Parsed user data:', userData);
        setUser(userData);
        // 프로필 정보 로드
        updateProfile();
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    updateProfile();
  };

  const logout = () => {
    setUser(null);
    setUserProfile(null);
    localStorage.removeItem('user');
  };

  const updateProfile = async () => {
    if (!user) return;

    try {
      const response = await fetch(`http://127.0.0.1:4004/users/${user.id}/profile`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const profileData = await response.json();
        setUserProfile(profileData);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const value = {
    user,
    userProfile,
    isLoading,
    login,
    logout,
    updateProfile,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};