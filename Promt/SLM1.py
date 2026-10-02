def get_slm1_prompt(question_json_text, student_answer_text):
    """
    SLM1 - 行為層評分 (純 JSON 結構化思維鏈版)

    特點：
    - 強制將思維鏈 (analysis) 置於 JSON 欄位首位，釋放小模型推理算力。
    - 不輸出任何 JSON 之外的解釋或 Markdown 包裝。
    - 維持高資訊密度的極簡指令。
    """
    return f"""
{question_json_text}

{student_answer_text}

評分層定義：
- 判斷層次：行為層（Behavior）
- 評分面向：語意與邏輯
- 核心判斷問題：程式「實際做了什麼」是否正確。
- 判斷內容：
  * 功能是否完整。
  * 邏輯是否正確。
  * 是否處理邊界條件。
- 僅依據程式實際行為判斷，不考慮是否遵循題目指定寫法，也不考慮語法、型別、編譯是否正確。

評分規則：
1. 僅依據上述「行為層」定義評分。
2. 逐項比對每個 criterion：完全符合=1，不符合、部分符合=0。
3. 每個 criterion 必須只依據程式實際行為是否達成，不得引用規範層或語言層理由。
4. 必須先在 "analysis" 中逐項寫下每個 criterion 的推理過程，再產生分數。
5. 只輸出以下 JSON，嚴禁任何其他文字、解釋或 Markdown 標籤：

{{
  "question_id": "...",
  "layer": "behavioral",
  "analysis": "在這裡逐項推導每個行為準則與程式碼控制流的比對過程...",
  "criteria_check": [
    {{
      "criterion": "①",
      "status": 0
    }}
  ],
  "total_criteria": N,
  "met_criteria": M,
  "behavioral_score": "M/N"
}}
"""