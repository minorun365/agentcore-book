'use client';

import { useState, useRef, useEffect, type FormEvent } from 'react';
import { fetchAuthSession } from 'aws-amplify/auth';
import ReactMarkdown from 'react-markdown';

// 環境変数からエージェントのARNを取得
const AGENT_ARN = process.env.NEXT_PUBLIC_AGENT_ARN;

// チャットメッセージの型定義
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStatus?: boolean;
  statusText?: string;
  statusCompleted?: boolean;
  authUrl?: string;
}

// ツール名を日本語の表示名に変換する
function getToolDisplayName(toolName: string): string {
  const names: Record<string, string> = {
    browser: 'Webブラウザ',
    add_calendar_event: 'カレンダー登録',
  };
  return names[toolName] || toolName;
}

export default function Chat() {
  // チャットの状態管理
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  // セッションIDをランダム生成（タブごとに固有）
  const sessionId = useRef(`session_${crypto.randomUUID()}`);

  // メッセージ追加時に自動スクロール
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // フォーム送信時のハンドラー
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    // ユーザーメッセージを追加して入力欄をクリア
    const userText = input.trim();
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', content: userText }]);
    setInput('');
    setLoading(true);

    // メッセージ吹き出しの状態管理
    let textAccumulator = '';
    let currentTextMsgId = crypto.randomUUID();
    let needNewTextMsg = false;

    // 「考え中…」シマー表示用の空メッセージを追加
    setMessages((prev) => [...prev, { id: currentTextMsgId, role: 'assistant', content: '' }]);

    try {
      // Cognito 認証トークンを取得
      const session = await fetchAuthSession();
      const token = session.tokens?.accessToken?.toString();

      // コールバックハンドラーに Cognito JWT を事前登録（3LO フロー用）
      // 同一オリジンの /api/set-token に送信（Next.js Route Handler）
      await fetch('/api/set-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      }).catch(() => {}); // エラーは無視して続行

      // AgentCore Runtime API を呼び出し
      const region = AGENT_ARN!.split(':')[3];
      const url = `https://bedrock-agentcore.${region}.amazonaws.com/runtimes/${encodeURIComponent(AGENT_ARN!)}/invocations?qualifier=DEFAULT`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userText, session_id: sessionId.current }),
      });

      // SSE ストリーミングを処理
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();

      // レスポンスを1チャンクずつ読み取る
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        // SSEの各行をパースしてイベントを処理
        for (const line of decoder.decode(value, { stream: true }).split('\n')) {
          if (!line.startsWith('data: ')) continue;
          try {
            const event = JSON.parse(line.slice(6));

            // テキストイベント: 吹き出しにテキストを追記
            if (event.type === 'text' && event.data) {
              textAccumulator += event.data;
              if (needNewTextMsg) {
                // ツール完了後、新しい吹き出しでテキストを表示 + ステータスを完了に
                currentTextMsgId = crypto.randomUUID();
                needNewTextMsg = false;
                setMessages((prev) => [
                  ...prev.map((m) =>
                    m.isStatus && !m.statusCompleted
                      ? { ...m, statusCompleted: true, statusText: 'ツール実行完了' }
                      : m
                  ),
                  { id: currentTextMsgId, role: 'assistant', content: textAccumulator },
                ]);
              } else {
                // 既存の吹き出しにテキストを追記
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === currentTextMsgId ? { ...m, content: textAccumulator } : m
                  )
                );
              }
            // ツール使用イベント: ステータスバッジを表示
            } else if (event.type === 'tool_use') {
              needNewTextMsg = true;
              textAccumulator = '';
              const displayName = getToolDisplayName(event.tool_name || 'ツール');
              setMessages((prev) => {
                const filtered = prev.filter(
                  (m) => !(m.id === currentTextMsgId && !m.content && !m.isStatus)
                );
                // リトライ時は既存バッジを再利用
                const lastStatusIdx = filtered.findLastIndex((m) => m.isStatus);
                const hasTextAfterStatus =
                  lastStatusIdx !== -1 &&
                  filtered.slice(lastStatusIdx + 1).some((m) => !m.isStatus && m.content);
                if (lastStatusIdx !== -1 && !hasTextAfterStatus) {
                  return filtered.map((m, i) =>
                    i === lastStatusIdx
                      ? { ...m, statusText: `${displayName} を実行中…`, statusCompleted: false }
                      : m
                  );
                }
                return [
                  ...filtered,
                  {
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: '',
                    isStatus: true,
                    statusText: `${displayName} を実行中…`,
                    statusCompleted: false,
                  },
                ];
              });
            // ツール完了イベント: バッジを完了状態に更新
            } else if (event.type === 'tool_result') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.isStatus && !m.statusCompleted
                    ? { ...m, statusCompleted: true, statusText: 'ツール実行完了' }
                    : m
                )
              );
            // 認可URLイベント: Google連携ボタンを表示
            } else if (event.type === 'auth_url' && event.url) {
              currentTextMsgId = crypto.randomUUID();
              textAccumulator = '';
              setMessages((prev) => [
                ...prev.map((m) =>
                  m.isStatus && !m.statusCompleted
                    ? { ...m, statusText: 'Google連携を待機中…' }
                    : m
                ),
                {
                  id: currentTextMsgId,
                  role: 'assistant',
                  content: 'Googleアカウントの接続が必要です。下のボタンをクリックしてください。',
                  authUrl: event.url,
                },
              ]);
              needNewTextMsg = true;
            }
          } catch {
            continue;
          }
        }
      }
    } finally {
      // ローディング解除と空メッセージの削除
      setLoading(false);
      setMessages((prev) =>
        prev.filter((m) => !(m.role === 'assistant' && !m.isStatus && !m.content.trim()))
      );
    }
  };

  // チャットUIのレンダリング
  return (
    <div className="app">
      {/* ヘッダー */}
      <header className="header">
        <h1>新刊チェッカー</h1>
        <p>技術書の新刊を調べて、Googleカレンダーに登録します</p>
      </header>

      {/* メッセージ一覧 */}
      <div className="messages">
        {/* 初期表示（メッセージがない場合） */}
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📖</div>
            <p>気になる技術書のジャンルや、</p>
            <p>登録したい予定を教えてください</p>
          </div>
        )}
        {/* 各メッセージの表示 */}
        {messages.map((m) => {
          // ステータスバッジの表示（ツール実行中/完了）
          if (m.isStatus) {
            return (
              <div key={m.id} className="message-row assistant">
                <div className={`status-badge ${m.statusCompleted ? 'completed' : 'active'}`}>
                  {m.statusCompleted ? (
                    <span className="check-icon">&#10003;</span>
                  ) : (
                    <span className="spinner" />
                  )}
                  <span>{m.statusText}</span>
                </div>
              </div>
            );
          }
          // ユーザー/アシスタントのチャット吹き出し
          return (
            <div key={m.id} className={`message-row ${m.role}`}>
              <div className={`bubble ${m.role}`}>
                {m.role === 'assistant' ? (
                  m.content ? (
                    <>
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                      {m.authUrl && (
                        <a
                          href={m.authUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="auth-button"
                        >
                          Google連携を開始 →
                        </a>
                      )}
                    </>
                  ) : (
                    <span className="shimmer-text">考え中…</span>
                  )
                ) : (
                  m.content
                )}
              </div>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>

      {/* 入力フォーム */}
      <form className="input-area" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="メッセージを入力…"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? '⏳' : '送信'}
        </button>
      </form>
    </div>
  );
}
