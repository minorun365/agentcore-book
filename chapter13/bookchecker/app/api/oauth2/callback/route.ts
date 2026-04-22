import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';
import { BedrockAgentCoreClient, CompleteResourceTokenAuthCommand } from '@aws-sdk/client-bedrock-agentcore';

// AgentCoreクライアントを作成
const client = new BedrockAgentCoreClient({
  region: process.env.AWS_REGION ?? 'us-east-1',
});

// 3LOコールバック処理（AgentCoreからリダイレクトされる）
export async function GET(request: NextRequest) {
  // URLパラメーターからセッションIDを取得
  const sessionId =
    request.nextUrl.searchParams.get('session_id');
  if (!sessionId) {
    return new NextResponse(
      'session_idが未指定です', { status: 400 }
    );
  }

  // Cookieに保存済みのCognitoトークンを取得
  const cookieStore = await cookies();
  const token =
    cookieStore.get('agentcore_user_token')?.value;
  if (!token) {
    return new NextResponse(
      'トークンが未設定です', { status: 401 }
    );
  }

  // セッションバインディングを完了させる
  try {
    await client.send(
      new CompleteResourceTokenAuthCommand({
        sessionUri: sessionId,
        userIdentifier: { userToken: token },
      })
    );
  } catch (err) {
    return new NextResponse(
      `Google連携エラー: ${err}`, { status: 500 }
    );
  }

  // 連携完了ページを表示
  return new NextResponse(
    '<html><body style="text-align:center;' +
    ' padding:60px; font-family:sans-serif">' +
    '<p>Google連携が完了しました！タブを閉じてOKです</p></body></html>',
    {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    }
  );
}
