import type { Metadata } from 'next'
import './globals.css'
import { UserProvider } from '../contexts/UserContext'

export const metadata: Metadata = {
  title: '사주로또 - 운명과 행운의 만남',
  description: '전통 사주학과 AI가 만나 당신의 운세에 맞는 개인 맞춤형 로또 번호를 예측합니다.',
  keywords: '사주, 로또, 예측, 운세, 번호추천, AI',
  authors: [{ name: 'SajuLotto Team' }],
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  themeColor: '#6366f1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head></head>
      <body className="font-sans antialiased">
        <UserProvider>
          {children}
        </UserProvider>
      </body>
    </html>
  )
}