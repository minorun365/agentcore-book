import json
import re

# SQLインジェクション検出パターン
SQL_PATTERNS = [
    r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP)",
    r"UNION\s+SELECT",
    r"DROP\s+TABLE",
]

def lambda_handler(event, context):
    mcp_data = event.get("mcp", {})
    request = mcp_data.get("gatewayRequest", {})
    body = request.get("body", {})

    # ツール呼び出し以外はそのまま通過
    if body.get("method") != "tools/call":
        return {
            "interceptorOutputVersion": "1.0",
            "mcp": {
                "transformedGatewayRequest":
                    request
            }
        }

    # ツール引数にSQLインジェクションがないか検査
    params_str = json.dumps(
        body.get("params", {}),
        ensure_ascii=False
    )
    for pattern in SQL_PATTERNS:
        if re.search(
            pattern, params_str, re.IGNORECASE
        ):
            # 不正な入力を検出、403でブロック
            return {
                "interceptorOutputVersion": "1.0",
                "mcp": {
                    "transformedGatewayResponse": {
                        "statusCode": 403,
                        "body": body
                    }
                }
            }

    # 問題なければリクエストを通過
    return {
        "interceptorOutputVersion": "1.0",
        "mcp": {
            "transformedGatewayRequest": request
        }
    }