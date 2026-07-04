import json

from google import genai
from google.genai import types

from .reference_db import get_ref_stats


def build_prompt(summary, issues, ref_db=None):
    """슬라이드 9: 구조화된 편차 데이터(JSON) + 투어 프로 코치 페르소나"""
    issue_text = "\n".join([f"- [{lvl.upper()}] {msg}" for lvl, msg in issues])

    # 페이즈별 통계 JSON
    phase_json = json.dumps(summary.get("phase_stats", {}), ensure_ascii=False, indent=2)

    # 프로 기준 비교 블록 (DB 있을 때만)
    ref_block = ""
    if ref_db:
        pro_s = get_ref_stats(ref_db, "prefs")  # placeholder
        pro_s = get_ref_stats(ref_db, "프로")
        am_s  = get_ref_stats(ref_db, "아마추어")
        if pro_s:
            label_map = {
                "spine_angle_delta":     "척추각 변화량",
                "x_factor":              "X-Factor",
                "shoulder_rotation_max": "어깨 최대 회전",
                "left_elbow_top":        "왼팔(백스윙톱)",
                "left_knee_addr":        "왼쪽 무릎(어드레스)",
                "right_knee_addr":       "오른쪽 무릎(어드레스)",
            }
            user_vals = {
                "spine_angle_delta":     summary.get("spine_angle_delta"),
                "x_factor":              summary.get("x_factor"),
                "shoulder_rotation_max": summary.get("shoulder_rotation_max"),
                "left_elbow_top":        (summary.get("phase_stats", {}).get("백스윙 톱") or {}).get("left_elbow"),
                "left_knee_addr":        (summary.get("phase_stats", {}).get("어드레스") or {}).get("left_knee"),
                "right_knee_addr":       (summary.get("phase_stats", {}).get("어드레스") or {}).get("right_knee"),
            }
            rows = []
            for m, lbl in label_map.items():
                if m not in pro_s:
                    continue
                pm, ps_ = pro_s[m]["mean"], pro_s[m]["std"]
                uv = user_vals.get(m)
                uv_str = f"{uv:.1f}°" if uv is not None else "-"
                am_str = f"{am_s[m]['mean']:.1f}°" if m in am_s else "-"
                rows.append(f"| {lbl} | {uv_str} | {pm:.1f}±{ps_:.1f}° | {am_str} |")
            if rows:
                n_pro = ref_db.get("프로", {}).get("n", 0)
                n_am  = ref_db.get("아마추어", {}).get("n", 0)
                ref_block = f"""
## 학습된 기준 데이터와 비교 (프로 {n_pro}명 / 아마추어 {n_am}명)
| 지표 | 이번 스윙 | 프로 기준(평균±σ) | 아마추어 평균 |
|------|-----------|-------------------|---------------|
""" + "\n".join(rows)

    return f"""당신은 20년 경력의 투어 프로 출신 골프 코치입니다.
원인과 결과를 항상 함께 설명하며, 수치 데이터에 기반한 구체적인 교정 방법을 제시합니다.

## 구조화된 스윙 분석 데이터 (JSON)
```json
{{
  "총_분석_프레임": {summary['total_frames']},
  "척추각": {{
    "평균": {summary['spine_angle_avg']}°,
    "변화량_delta": {summary['spine_angle_delta']}°,
    "최소": {summary['spine_angle_min']}°,
    "최대": {summary['spine_angle_max']}°
  }},
  "회전_분석": {{
    "어깨_최대_회전": {summary['shoulder_rotation_max']}°,
    "골반_최대_회전": {summary['hip_rotation_max']}°,
    "X_Factor_꼬임": {summary['x_factor']}°
  }},
  "관절_평균": {{
    "왼쪽_무릎": {summary['left_knee_avg']}°,
    "오른쪽_무릎": {summary['right_knee_avg']}°,
    "왼팔_팔꿈치": {summary['left_elbow_avg']}°,
    "오른팔_팔꿈치": {summary['right_elbow_avg']}°
  }},
  "7단계_페이즈별_데이터": {phase_json}
}}
```

## AI 자동 진단 이슈
{issue_text}
{ref_block}
위 데이터를 기반으로 정확히 아래 형식으로 코칭 리포트를 작성하세요:

### 🏌️ 종합 스윙 평가
(전반적인 강점과 가장 시급한 개선점을 2~3문장으로)

### ⚠️ 핵심 교정 포인트 (원인 → 결과 → 해결책)
**[1번 포인트]**: (원인) ~ 때문에, (결과) ~ 현상이 발생합니다. (해결) ~을 실천하세요.
**[2번 포인트]**: ...
**[3번 포인트]**: ...

### 💪 맞춤형 연습 드릴
**드릴 1**: (이름) — (구체적 방법과 횟수)
**드릴 2**: (이름) — (구체적 방법과 횟수)

### 🎯 다음 라운드 전 ONE THING
(가장 우선순위가 높은 단 하나의 집중 과제를 굵게 강조)

한국어로, 친절하지만 프로답게 작성해주세요."""


def get_llm_feedback(summary, issues, provider, api_key, model_name=None, ref_db=None):
    """슬라이드 9: LLM 피드백 생성 (Gemini / Claude / GPT 선택)"""
    prompt = build_prompt(summary, issues, ref_db=ref_db)

    if provider == "Gemini":
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name or "gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    elif provider == "Claude":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model_name or "claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

    elif provider == "GPT":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name or "gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        return resp.choices[0].message.content

    return "지원하지 않는 LLM 공급자입니다."
