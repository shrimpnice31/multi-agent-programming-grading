import json


def generate_prompt(arbitration_input_dict):
    """
    LLM 專家仲裁 Prompt
    - 僅載入有分歧的評分層級
    - 強制逐項獨立重評
    - 嚴格隔離行為、規範、語言三層
    - 輸出可稽核的純 JSON
    """
    q_id = arbitration_input_dict.get("題號", "未知題號")
    student_ans = arbitration_input_dict.get("學生答案", "")
    inconsistent_layers = arbitration_input_dict.get("不一致層級", [])
    diff_details = arbitration_input_dict.get("差異詳情", {})

    layer_meta = {
        "slm1": {
            "name": "behavioral",
            "label": "行為層準則（Behavioral Layer）",
            "key": "行為層準則",
            "definition": (
                "只判斷程式實際功能、邏輯及邊界處理是否正確；"
                "不得因指定寫法、命名、格式、語法或型別問題直接扣分。"
            ),
        },
        "slm2": {
            "name": "specification",
            "label": "規範層準則（Specification Layer）",
            "key": "規範層準則",
            "definition": (
                "只判斷是否遵循題目指定的控制項、方法、格式、命名、"
                "撰寫方式與限制條件；不得因功能結果或語法錯誤直接扣分。"
            ),
        },
        "slm3": {
            "name": "syntax",
            "label": "語言層準則（Syntax Layer）",
            "key": "語言層準則",
            "definition": (
                "只判斷語法、型別、運算結構、方法呼叫及基本程式結構"
                "是否合法；不得因功能邏輯或未遵循指定寫法直接扣分。"
            ),
        },
    }

    valid_layers = [
        layer for layer in inconsistent_layers
        if layer in layer_meta
    ]

    criteria_sections = []
    conflict_sections = []
    output_layer_names = []

    for slm_key in valid_layers:
        meta = layer_meta[slm_key]
        raw_criteria = arbitration_input_dict.get(meta["key"], {})
        detail = diff_details.get(slm_key, {})

        compact_criteria = json.dumps(
            raw_criteria,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        criteria_sections.append(
            f"【{meta['name']}】\n"
            f"層級定義：{meta['definition']}\n"
            f"官方準則：{compact_criteria}"
        )

        conflict_sections.append(
            f"【{meta['name']} 分歧】\n"
            f"Run 1：分數={detail.get('run1_score')}；"
            f"理由={json.dumps(detail.get('run1_analysis', ''), ensure_ascii=False)}\n"
            f"Run 2：分數={detail.get('run2_score')}；"
            f"理由={json.dumps(detail.get('run2_analysis', ''), ensure_ascii=False)}"
        )

        output_layer_names.append(meta["name"])

    criteria_context = "\n\n".join(criteria_sections)
    conflict_context = "\n\n".join(conflict_sections)
    output_layers = json.dumps(output_layer_names, ensure_ascii=False)

    return f"""你是 C# 程式評量仲裁者。

底層模型對學生答案產生分數分歧。你必須依據官方準則與學生原始碼，對每個爭議層級進行獨立重新評分。

【核心原則】
1. 不得直接採納 Run 1 或 Run 2；兩者的分數與理由僅供定位爭議。
2. 必須逐項重新比對官方 criterion。
3. 每項 criterion：完全符合=1；部分符合、不符合或無法由程式碼證明=0。
4. 各層必須完全隔離，不得使用其他層級的理由給分或扣分。
5. 只評估爭議層級：{output_layers}。
6. 所有爭議層級都必須輸出，不得遺漏，也不得新增非爭議層級。
7. total_criteria 必須等於該層官方 criterion 數量。
8. met_criteria 必須等於 criteria_check 中 status=1 的數量。
9. score 必須等於 "met_criteria/total_criteria"。

【問答題題特殊評分】
此題型無程式碼,學生答案是C#程式執行結果的「文字描述」。
請根據學生的描述,評價是否：
1. 正確理解了程式的行為
2. 準確描述了預期輸出
3. 格式符合題目要求

【三層判斷界線】
- behavioral：功能、邏輯、控制流程、輸出結果、邊界條件。
- specification：指定控制項、指定方法、格式、命名、撰寫方式、限制條件。
- syntax：語法、型別、運算式、方法呼叫、變數宣告及基本程式結構。

【題號】
{q_id}

【爭議層級與官方準則】
{criteria_context}

【學生提交的 C# 原始碼】
{student_ans}

【兩次評分的分歧資訊】
{conflict_context}

【輸出要求】
只輸出一個合法 JSON 物件，不得輸出 Markdown、前言、後記或其他文字。

criteria_check 必須依照官方準則順序輸出。
reason 只寫該 criterion 最核心的程式碼證據，不得引用其他層級理由。
reasoning 用一句話總結該層最主要的仲裁原因。

輸出格式：
{{
  "{q_id}": {{
    "實際爭議層級名稱": {{
      "criteria_check": [
        {{
          "criterion": "①",
          "status": 0,
          "reason": "簡短且限於本層的判斷證據"
        }}
      ],
      "total_criteria": 1,
      "met_criteria": 0,
      "score": "0/1",
      "reasoning": "該層仲裁結果的一句話總結"
    }}
  }}
}}"""