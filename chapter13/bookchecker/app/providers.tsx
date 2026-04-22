'use client';

import type { ReactNode } from 'react';
import { Amplify } from 'aws-amplify';
import { Authenticator, translations } from '@aws-amplify/ui-react';
import { I18n } from 'aws-amplify/utils';
import amplifyOutputs from '../amplify_outputs.json';
import '@aws-amplify/ui-react/styles.css';

// Amplifyの初期設定
Amplify.configure(amplifyOutputs);

// 認証UIを日本語化
I18n.putVocabularies(translations);
I18n.setLanguage('ja');

// 認証プロバイダーコンポーネント
export function AuthProvider({ children }: { children: ReactNode }) {
  return <Authenticator>{children}</Authenticator>;
}
