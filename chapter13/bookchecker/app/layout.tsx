import type { ReactNode } from 'react';
import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from './providers';

// ページタイトルの設定
export const metadata: Metadata = { title: '新刊チェッカー' };

// 全ページ共通のレイアウト（認証プロバイダーで囲む）
export default function RootLayout(
  { children }: { children: ReactNode }
) {
  return (
    <html lang="ja">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
