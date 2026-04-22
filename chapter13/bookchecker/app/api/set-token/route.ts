import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

// CognitoトークンをHttpOnly Cookieに保存するAPI
export async function POST(request: Request) {
  const { token } = await request.json();
  const cookieStore = await cookies();

  // セキュアなCookieとして保存
  cookieStore.set('agentcore_user_token', token, {
    httpOnly: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 3600,
  });
  return NextResponse.json({ status: 'ok' });
}
