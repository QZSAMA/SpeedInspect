import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/store/providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SpeedInspect - 房屋状况智能检查系统',
  description: '基于AI技术的房屋状况智能检查系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
