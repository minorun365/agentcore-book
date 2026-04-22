import boto3
import streamlit as st


# BedrockのモデルIDからARNを生成する
def create_bedrock_model_arn(model_id: str):
    AWS_REGION = boto3.Session().region_name
    AWS_ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]

    return f"arn:aws:bedrock:{AWS_REGION}:{AWS_ACCOUNT_ID}:inference-profile/{model_id}"


# BedrockナレッジベースのAPIを呼び出すクライアント
client = boto3.client("bedrock-agent-runtime")

knowledge_base_id = st.text_input("ナレッジベースID")

# チャット欄への入力をprompt変数で受け取る
if prompt := st.chat_input():
    # ユーザーメッセージとして画面出力
    with st.chat_message("user"):
        st.write(prompt)

    # retrieve_and_generate_stream API呼び出し
    response = client.retrieve_and_generate_stream(
        retrieveAndGenerateConfiguration={
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": knowledge_base_id,
                "modelArn": create_bedrock_model_arn(
                    "us.anthropic.claude-sonnet-4-6"
                ),
            },
            "type": "KNOWLEDGE_BASE",
        },
        input={"text": prompt},
    )

    # 変数を用意
    output_text = ""
    citations = []

    # アシスタントメッセージとして画面出力
    with st.chat_message("assistant"):
        # ストリームで受けたメッセージをコンテナ
        output = st.empty()

        for stream in response["stream"]:
            # outputに含まれる回答を、受信済みの回答に追記して出力
            if "output" in stream:
                output_text = output_text + stream["output"]["text"]
                output.markdown(output_text)

            # citationには引用が含まれる。citations変数に保持し、回答出力後にまとめて出力
            if "citation" in stream:
                citation = stream["citation"]
                citations.append(citation)

        st.divider()
        st.subheader("引用")

        # 引用を出力
        for citation in citations:
            st.json(citation, expanded=1)
