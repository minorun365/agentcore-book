import json
import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

# 環境変数
AGENT_RUNTIME_NAME = os.environ["AGENT_RUNTIME_NAME"]
SNS_TOPIC_MAP = json.loads(os.environ["SNS_TOPIC_MAP"])
APPROVAL_TABLE = os.environ["APPROVAL_TABLE"]

# クライアント
dynamodb = boto3.resource("dynamodb")
agentcore_control = boto3.client("bedrock-agentcore-control")
agentcore = boto3.client("bedrock-agentcore")
sns = boto3.client("sns")
table = dynamodb.Table(APPROVAL_TABLE)

# Runtime名からARNを取得
def _get_runtime_arn() -> str:
    response = agentcore_control.list_agent_runtimes()
    for runtime in response.get("agentRuntimes", []):
        if runtime["agentRuntimeName"] == AGENT_RUNTIME_NAME:
            return runtime["agentRuntimeArn"]

# 承認IDから承認レコードを取得
def _get_approval_by_token(approval_id: str) -> dict | None:
    response = table.query(
        KeyConditionExpression=Key("approval_id").eq(approval_id),
        Limit=1
    )
    items = response.get("Items", [])
    return items[0] if items else None

# 承認ステータスを更新
def _update_approval_status(approval_id: str, created_at: str, new_status: str) -> None:
    table.update_item(
        Key={"approval_id": approval_id, "created_at": created_at},
        UpdateExpression="SET #status = :status, updated_at = :updated_at",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": new_status,
            ":updated_at": datetime.now(timezone.utc).isoformat()
        },
    )

# AgentCoreランタイムを呼び出して承認後処理を実行
def _invoke_agent_for_approval(record: dict, action: str) -> dict:
    payload = {"action": action, "approval_record": record}
    aid = record['approval_id']
    session_id = f"approval-callback-session-{aid}"
    runtime_arn = _get_runtime_arn()
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(payload, default=str).encode("utf-8"),
    )
    result = b"".join(response.get("response", [])).decode("utf-8")
    return {"success": True, "result": result}

# 申請者にSNS経由で通知を送信
def _send_notification(record: dict, status: str) -> None:
    submitter_email = record["submitter_email"]
    topic_arn = SNS_TOPIC_MAP[submitter_email]

    status_text = "承認" if status == "approved" else "却下"
    subject = f"【{status_text}完了】経費精算: {record['expense_id']}"
    body = f"""
    経費精算が{status_text}されました。
    経費ID: {record['expense_id']}
    金額: {int(record['amount']):,}円
    支払先: {record['vendor_name']}
    """

    sns.publish(TopicArn=topic_arn, Subject=subject, Message=body)

# 承認・却下完了画面のHTMLを生成
def _generate_success_html(action: str, record: dict) -> str:
    action_text = "承認" if action == "approve" else "却下"
    icon = "✅" if action == "approve" else "❌"
    return f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head><meta charset="UTF-8">
    <title>経費精算 {action_text}完了</title></head>
    <body style="text-align: center; padding: 50px;">
        <h1>{icon} 経費精算を{action_text}しました</h1>
        <p>このページを閉じてください。</p>
    </body>
    </html>"""

# Lambda Function URLレスポンスを生成
def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }

# 承認/却下コールバックを処理
def handler(event: dict, context) -> dict:
    # クエリパラメーターからトークンとアクションを取得
    params = event.get("queryStringParameters", {}) or {}
    token = params.get("token")
    action = params.get("action")

    # パラメーターの検証
    if not token or action not in ["approve", "reject"]:
        return _response(400, {"error": "Invalid parameters"})

    # 承認レコードの取得と状態確認
    approval_record = _get_approval_by_token(token)
    if not approval_record or approval_record["status"] != "pending":
        return _response(400, {"error": "Invalid or already processed"})

    # 承認ステータスを更新
    new_status = "approved" if action == "approve" else "rejected"
    _update_approval_status(
        approval_record["approval_id"],
        approval_record["created_at"],
        new_status
    )

    # AgentCoreランタイムで承認後処理を実行
    _invoke_agent_for_approval(
        approval_record, action
    )

    # 申請者に結果を通知
    _send_notification(approval_record, new_status)

    # 完了画面のHTMLを返却
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "body": _generate_success_html(action, approval_record),
    }
