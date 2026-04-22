import base64
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key
from bedrock_agentcore import BedrockAgentCoreApp
from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel


class ReceiptItem(BaseModel):  # 明細項目
    name: str
    amount: int

class ReceiptInfo(BaseModel):  # 領収書の情報
    vendor_name: str
    transaction_date: str
    total: int
    items: list[ReceiptItem]

class ClassificationInfo(BaseModel):   # 領収書の経費分類の結果
    category: str


# 環境変数
BEDROCK_MODEL_ID = os.environ["BEDROCK_MODEL_ID"]
APPROVAL_AMOUNT_THRESHOLD = 100000  # 10万円
AWS_REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
APPROVAL_API_URL = os.environ["APPROVAL_API_URL"]
APPROVAL_TABLE = os.environ["APPROVAL_TABLE"]
SNS_TOPIC_MAP = json.loads(os.environ["SNS_TOPIC_MAP"])
CONFLUENCE_URL = os.environ["CONFLUENCE_URL"].rstrip("/")
CONFLUENCE_USERNAME = os.environ["CONFLUENCE_USERNAME"]
CONFLUENCE_API_TOKEN = os.environ["CONFLUENCE_API_TOKEN"]
CONFLUENCE_SPACE_KEY = os.environ["CONFLUENCE_SPACE_KEY"]

# クライアント
s3 = boto3.client("s3", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(APPROVAL_TABLE)


# S3からユーザーマスタを読み込む
def load_users_from_s3() -> list[dict]:
    response = s3.get_object(Bucket=BUCKET_NAME, Key="data/users.json")
    return json.loads(response["Body"].read().decode("utf-8"))["users"]


SYSTEM_PROMPT = """
あなたは経費精算を支援するAIエージェントです。
領収書の解析、経費分類、承認プロセス、承認後の記録を担当します。

## 領収書処理フロー（S3アップロード時）
1. `process_receipt_image`でマルチモーダル解析
2. `search_classification_info`で経費分類
3. `get_approver_by_amount`で承認者候補を取得し、金額に基づいて1人選定
   - 金額 <= 10万: 課長 / 金額 > 10万: 部長
4. `send_approval_request`で承認依頼メールを送信
   - 必要な全情報（経費ID、金額、カテゴリ、内容、ベンダー名、取引日、申請者、承認者）を渡す

## 承認後処理フロー（承認コールバック時）
- 承認（approved）の場合: `write_to_confluence`でConfluenceに経費記録を書き込む
- 却下（rejected）の場合: 何もしない
"""


# S3から領収書画像を取得してマルチモーダル解析
@tool
def process_receipt_image(receipt_key: str) -> dict:
    # S3から領収書画像を取得
    response = s3.get_object(Bucket=BUCKET_NAME, Key=receipt_key)
    content_type = response.get("ContentType", "image/jpeg")
    media_type = content_type.split("/")[-1]
    image_format = "png" if media_type == "png" else "jpeg"
    image_data = response["Body"].read()

    # 画像解析用のエージェントを作成
    model = BedrockModel(model_id=BEDROCK_MODEL_ID)
    extraction_agent = Agent(model=model, tools=[])

    # マルチモーダル解析を実行
    result = extraction_agent(
        [
            {"image": {"format": image_format, "source": {"bytes": image_data}}},
            {"text": "この領収書を解析してください"}
        ],
        structured_output_model=ReceiptInfo,
    )
    receipt = result.structured_output.model_dump()
    return {"success": True, "receipt": receipt}


# 経費分類のための情報を検索・推論
@tool
def search_classification_info(vendor_name: str, description: str, amount: int) -> dict:
    print(f"[分類] ベンダー={vendor_name},"
          f" 内容={description}, 金額={amount}")

    # 1. 社内ルールでマッチング
    # S3から分類ルールを読み込み
    rules = json.loads(
        s3.get_object(Bucket=BUCKET_NAME, Key="data/classification_rules.json")
        ["Body"].read().decode("utf-8")
    )["rules"]
    # キーワードが一致する最初のルールを取得
    matched = next(
        (r["category"] for r in rules
         if any(kw in vendor_name for kw in r.get("vendor_keywords", []))),
        None
    )
    if matched:
        print(f"[分類] 社内ルールにマッチ: {matched}")
        return {"success": True, "category": matched, "source": "internal_rule"}

    # 2. マッチしなければLLM推論
    print("[分類] 社内ルールにマッチなし、LLM推論を実行")
    query = f"""
    以下の経費情報から適切な経費カテゴリーを判断してください。

    支払先: {vendor_name}
    内容: {description}
    金額: {amount:,}円

    カテゴリ: 交通費、宿泊費、交際費、消耗品費、通信費、備品費、研修費、その他"""

    agent = Agent(
        model=BedrockModel(model_id=BEDROCK_MODEL_ID),
        tools=[]
    )
    result = agent(query, structured_output_model=ClassificationInfo)
    print(f"[分類] LLM推論結果: {result.structured_output.category}")
    output = result.structured_output.model_dump()
    return {"success": True, **output, "source": "llm_inference"}


# 金額に基づいて承認者を決定するための情報を取得
@tool
def get_approver_by_amount(amount: int) -> dict:
    # S3からユーザー情報を読み込み
    users = load_users_from_s3()
    # 承認者候補（課長・部長）を抽出
    approvers = [
        {"name": u["name"], "email": u["email"], "role": u["role"]}
        for u in users if u.get("role") in ["課長", "部長"]
    ]
    return {
        "success": True,
        "amount": amount,
        "threshold": APPROVAL_AMOUNT_THRESHOLD,
        "approvers": approvers
    }


# 承認依頼メールを送信
@tool
def send_approval_request(
    expense_id: str, amount: int,
    category: str, description: str,
    vendor_name: str,
    submitter_name: str, submitter_email: str,
    approver_name: str, approver_email: str,
    transaction_date: str = "", items: list = None,
) -> dict:
    # 承認IDを生成（重複防止用）
    approval_id = hashlib.sha256(expense_id.encode()).hexdigest()[:16]
    existing = table.query(
        KeyConditionExpression=Key("approval_id").eq(approval_id), Limit=1
    )
    if existing.get("Items"):
        return {
            "success": True, "already_exists": True,
            "approval_id": approval_id,
        }

    # DynamoDBに承認レコードを保存
    approval_url = f"{APPROVAL_API_URL}?token={approval_id}"
    table.put_item(Item={
        "approval_id": approval_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expense_id": expense_id,
        "amount": amount,
        "category": category,
        "description": description,
        "vendor_name": vendor_name,
        "submitter_name": submitter_name,
        "submitter_email": submitter_email,
        "approver_name": approver_name,
        "approver_email": approver_email,
        "transaction_date": transaction_date,
        "items": items or [],
        "status": "pending",
    })

    # SNS経由で承認依頼メールを送信
    subject = f"【承認依頼】経費精算: {expense_id} - {vendor_name}"
    body = f"""
    経費精算の承認依頼です。
    経費ID: {expense_id}
    金額: {amount:,}円
    カテゴリ: {category}
    支払先: {vendor_name}
    内容: {description}
    申請者: {submitter_name} ({submitter_email})

    ▼ 承認: {approval_url}&action=approve
    ▼ 却下: {approval_url}&action=reject
    """
    sns.publish(
        TopicArn=SNS_TOPIC_MAP[approver_email],
        Subject=subject,
        Message=body
    )
    return {"success": True, "approval_id": approval_id}


# 承認済み経費をConfluenceに書き込む
@tool
def write_to_confluence(
    expense_id: str, amount: int,
    category: str, vendor_name: str,
    description: str, transaction_date: str,
    submitter_name: str, approver_name: str,
) -> dict:
    # Basic認証ヘッダー
    credentials = f"{CONFLUENCE_USERNAME}:{CONFLUENCE_API_TOKEN}"
    encoded = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded}"

    # 経費精算ページのHTML
    content = f"""
    <h1>経費精算記録: {expense_id}</h1>
    <table><tbody>
    <tr><th>金額</th><td>{amount:,}円</td></tr>
    <tr><th>カテゴリ</th><td>{category}</td></tr>
    <tr><th>支払先</th><td>{vendor_name}</td></tr>
    <tr><th>内容</th><td>{description}</td></tr>
    <tr><th>取引日</th><td>{transaction_date}</td></tr>
    <tr><th>申請者</th><td>{submitter_name}</td></tr>
    <tr><th>承認者</th><td>{approver_name}</td></tr>
    </tbody></table>"""

    # Confluence APIでページ作成
    page_data = {
        "type": "page",
        "title": f"経費精算記録: {expense_id}",
        "space": {"key": CONFLUENCE_SPACE_KEY},
        "body": {"storage": {
            "value": content,
            "representation": "storage",
        }},
    }
    url = f"{CONFLUENCE_URL}/wiki/rest/api/content"
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(page_data).encode("utf-8"),
        headers=headers, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    links = result.get("_links", {})
    page_url = f"{CONFLUENCE_URL}/wiki{links.get('webui', '')}"
    return {"success": True, "page_id": result.get("id"), "url": page_url}


# エージェントを作成
def create_agent() -> Agent:
    model = BedrockModel(model_id=BEDROCK_MODEL_ID)
    tools = [
        process_receipt_image,
        search_classification_info,
        get_approver_by_amount,
        send_approval_request,
        write_to_confluence,
    ]
    return Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=tools)


app = BedrockAgentCoreApp()

# リクエストを処理（ペイロードの内容でルーティング）
@app.entrypoint
def handle_request(request: dict) -> dict:
    if request.get("action"):
        return process_approval(request)
    return process_expense(request)

# S3アップロードイベントを処理
def process_expense(request: dict) -> dict:
    key = request.get("receipt_key")
    if not key:
        detail = request.get("detail", {})
        key = detail.get("object", {}).get("key")
    submitter_name = request.get("submitter_name")
    submitter_email = request.get("submitter_email")
    expense_id = f"EXP-{hashlib.sha256(key.encode()).hexdigest()[:12]}"

    prompt = f"""
以下の領収書を処理してください。

- 経費ID: {expense_id}
- S3キー: {key}
- 申請者名: {submitter_name}
- 申請者メール: {submitter_email}
"""

    result = create_agent()(prompt)
    output = str(result)
    return {"success": True, "expense_id": expense_id, "result": output}


# 承認コールバックからの処理
def process_approval(request: dict) -> dict:
    action = request.get("action")
    record = request.get("approval_record", {})
    expense_id = record.get("expense_id")

    prompt = f"""
以下の承認結果を処理してください。

- アクション: {action}
- 経費ID: {expense_id}
- 金額: {record.get('amount')}
- カテゴリ: {record.get('category')}
- 支払先: {record.get('vendor_name')}
- 内容: {record.get('description')}
- 取引日: {record.get('transaction_date')}
- 申請者: {record.get('submitter_name')}
- 承認者: {record.get('approver_name')}
"""

    result = create_agent()(prompt)
    output = str(result)
    return {"success": True, "expense_id": expense_id, "result": output}

# メインエントリーポイント
def main():
    app.run()

if __name__ == "__main__":
    main()
