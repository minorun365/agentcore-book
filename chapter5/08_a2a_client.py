import boto3
from strands import Agent
from strands_tools.a2a_client import A2AClientToolProvider
from mcp_proxy_for_aws.sigv4_helper import SigV4HTTPXAuth

# エージェントカードのURLを設定
AGENT_ARN = "<A2AサーバーのランタイムARN>"
encoded_arn = AGENT_ARN.replace(":", "%3A").replace("/", "%2F")
runtime_url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{encoded_arn}/invocations"

# IAM認証情報を取得
session = boto3.Session()
credentials = session.get_credentials()
auth = SigV4HTTPXAuth(credentials, "bedrock-agentcore", "us-east-1")

# A2Aサーバーをツールとして呼び出すエージェントを作成
provider = A2AClientToolProvider(
    known_agent_urls=[runtime_url],
    httpx_client_args={"auth": auth}
)
agent = Agent(tools=provider.tools)
agent("A2Aサーバーを使って、3たす5を計算して")