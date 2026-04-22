import os, requests
from strands import tool
from bedrock_agentcore.identity import requires_access_token

# AgentCoreランタイムの環境変数を取得
PROVIDER_NAME = os.getenv("CREDENTIAL_PROVIDER_NAME")
CALLBACK_URL = os.getenv("CALLBACK_URL")
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


# カレンダー操作ツールを作成する関数
def make_calendar_tool(event_queue):
    async def _on_auth_url(url: str):
        # Googleの認可URLをキューに送信
        await event_queue.put(
            {"type": "auth_url", "url": url}
        )

    @tool
    async def add_calendar_event(
        summary: str,
        start_date: str,
        end_date: str,
        description: str = "",
    ):
        """Google Calendarに終日予定を追加する。

        Args:
            summary: 予定のタイトル
            start_date: 開始日（YYYY-MM-DD形式）
            end_date: 終了日（YYYY-MM-DD形式、開始日の翌日）
            description: 予定の詳細説明
        """

        # AgentCoreアイデンティティでアクセストークンを自動取得
        @requires_access_token(
            provider_name=PROVIDER_NAME,
            scopes=CALENDAR_SCOPES,
            auth_flow="USER_FEDERATION",
            on_auth_url=_on_auth_url,
            callback_url=CALLBACK_URL,
        )
        async def call_api(access_token: str = ""):
            # Google Calendar APIのリクエストボディを構築
            event = {
                "summary": summary,
                "description": description,
                "start": {"date": start_date},
                "end": {"date": end_date},
            }
            # Google Calendar APIにイベントを追加する
            resp = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {access_token}"},
                json=event,
            )
            return resp.json()

        # API呼び出しを実行（認可が必要な場合はOAuthフローを起動）
        result = await call_api()

        # 結果に応じて成功・失敗メッセージを返す
        if "error" in result:
            return f"カレンダー登録に失敗しました: {result['error']['message']}"
        return f"カレンダーに登録しました: {result.get('summary')} ({result.get('start', {}).get('date')})"

    return add_calendar_event
