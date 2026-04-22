import json, uvicorn
from fastapi import FastAPI
from bedrock_agentcore.services.identity import IdentityClient, UserIdIdentifier

# FastAPIアプリとIdentityクライアントを作成
app = FastAPI()
client = IdentityClient(region="us-east-1")
config = json.load(open(".agentcore.json"))

# 認可完了後のリダイレクトを受け取るエンドポイント
@app.get("/oauth2/callback")
async def handle_callback(session_id: str):
    client.complete_resource_token_auth(
        session_uri=session_id,
        user_identifier=UserIdIdentifier(
            user_id=config["user_id"]))
    return "認証成功！このタブを閉じてください"

# APIサーバーを起動
uvicorn.run(app, host="127.0.0.1", port=9090)
