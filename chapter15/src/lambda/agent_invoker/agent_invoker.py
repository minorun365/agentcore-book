import hashlib
import json
import os
import urllib.parse
import boto3

# 環境変数
AGENT_RUNTIME_ARN = os.environ["AGENT_RUNTIME_ARN"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

# クライアント
s3 = boto3.client("s3")
agentcore = boto3.client("bedrock-agentcore")

# S3からユーザー情報を取得
def get_user_info(user_id: str) -> dict:
    response = s3.get_object(Bucket=BUCKET_NAME, Key="data/users.json")
    users = json.loads(response["Body"].read().decode("utf-8"))["users"]
    for user in users:
        if user["user_id"] == user_id:
            return user

# AgentCoreランタイムを起動
def invoke_agent_runtime(receipt_key: str, bucket_name: str, user_id: str) -> dict:
    approval_id = hashlib.sha256(receipt_key.encode()).hexdigest()[:16]

    # 申請者情報を取得
    user_info = get_user_info(user_id)

    # ペイロードを構築
    payload = {
        "receipt_key": receipt_key,
        "submitter_email": user_info["email"],
        "submitter_name": user_info["name"],
    }

    # エージェントのRuntimeを呼び出し
    session_id = f"expense-agent-session-{approval_id}"
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=json.dumps(payload).encode("utf-8"),
    )
    result = b"".join(response.get("response", [])).decode("utf-8")
    return {"success": True, "session_id": session_id, "result": result}

# S3アップロードイベントを処理してAgentCoreランタイムを起動
def handler(event: dict, context) -> dict:
    record = event["Records"][0]
    bucket_name = record["s3"]["bucket"]["name"]
    object_key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
    user_id = object_key.split("/")[1]

    result = invoke_agent_runtime(object_key, bucket_name, user_id)
    body = json.dumps(result, ensure_ascii=False)
    return {"statusCode": 200, "body": body}
