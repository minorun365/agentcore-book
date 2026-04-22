from pydantic import BaseModel, Field
from strands import Agent


# 型の定義
class Translation(BaseModel):
    language: str = Field(description="Target language in English")
    result: str = Field(description="Translation results")


agent = Agent()

result = agent(
    "「今日はいい天気です」をフランス語に翻訳して。",
    structured_output_model=Translation,  # 型を指定
)

# 構造化出力した結果を取得
translation: Translation = result.structured_output
print(translation.language)  # French
print(translation.result)  # Aujourd'hui, c'est un beau temps.
