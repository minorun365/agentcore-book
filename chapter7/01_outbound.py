import httpx
from strands import Agent, tool
from bedrock_agentcore.identity import requires_access_token

# Confluenceのサイト情報を取得するツール
@tool
def get_confluence_sites():

    # OAuthトークンを取得してAPIを呼び出す
    @requires_access_token(
        provider_name="AtlassianProvider",
        scopes=["read:confluence-content.all"],
        auth_flow="USER_FEDERATION",
        on_auth_url=lambda url: print(url),
        callback_url="http://localhost:9090/oauth2/callback",
    )
    def call_api(access_token: str = ""):
        response = httpx.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return response.json()

    return call_api()

# AIエージェントを作成して呼び出す
agent = Agent(tools=[get_confluence_sites])
agent("Atlassianのサイト一覧を取得して")
