def get_slm2_prompt(question_json_text, student_answer_text):
    """
    SLM2 - 規範層評分 (純 JSON 結構化思維鏈版)

    特點：
    - 強制將思維鏈 (analysis) 置於 JSON 欄位首位，釋放小模型推理算力。
    - 不輸出任何 JSON 之外的解釋或 Markdown 包裝。
    - 維持高資訊密度的極簡指令。
    """
    return f"""
{question_json_text}

{student_answer_text}

評分層定義：
- 判斷層次：規範層（Specification）
- 評分面向：規則與指令遵循
- 核心判斷問題：是否「照題目要求的方式」撰寫。
- 判斷內容：
  * 是否使用指定控制項。
  * 是否符合指定格式。
  * 是否遵循題目要求的撰寫方式。
  * 是否違反限制條件。
- 僅依據題目要求的規範判斷，不考慮程式功能是否正確，也不考慮語法、型別、編譯是否正確。

評分規則：
1. 僅依據上述「規範層」定義評分。
2. 逐項比對每個 criterion：完全符合=1，不符合、部分符合=0。
3. 每個 criterion 必須只依據是否符合題目規範判斷，不得引用行為層或語言層理由。
4. 必須先在 "analysis" 中逐項寫下每個 criterion 的推理過程，再產生分數。
5. 只輸出以下 JSON，嚴禁任何其他文字、解釋或 Markdown 標籤：

{{
  "question_id": "...",
  "layer": "specification",
  "analysis": "在這裡逐項推導每個規範準則與程式碼結構、命名或型態的比對過程...",
  "criteria_check": [
    {{
      "criterion": "①",
      "status": 0
    }}
  ],
  "total_criteria": N,
  "met_criteria": M,
  "specification_score": "M/N"
}}
"""