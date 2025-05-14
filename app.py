import streamlit as st
import datetime
import pandas as pd
import requests

# -------------------------
# 🔐 Notion API情報を直接埋め込む
# -------------------------
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "1f08fe59c25a8082b405cca168b98937"

# -------------------------
# 🧠 プロフィール設定
# -------------------------
sex = "F"
age = 33
height = 170.0  # cm

# -------------------------
# 🚀 アプリタイトル
# -------------------------
st.title("毎日のカロリーログフォーム")

# -------------------------
# 📅 入力フォーム（順番調整済み）
# -------------------------
weight = st.number_input("今日の体重 (kg)", min_value=30.0, max_value=150.0, step=0.1)
cal_in = st.number_input("摂取カロリー (kcal)", min_value=0, max_value=10000, step=10)
protein = st.number_input("たんぱく質 (g)", min_value=0.0, step=0.1)
fat = st.number_input("脂質 (g)", min_value=0.0, step=0.1)
carbs = st.number_input("炭水化物 (g)", min_value=0.0, step=0.1)
exercise_cal = st.number_input("運動で消費したカロリー (kcal)", min_value=0, max_value=5000, step=10)
sleep_hours = st.number_input("睡眠時間 (時間)", min_value=0.0, max_value=24.0, step=0.1)
water = st.number_input("水分摂取量 (ml)", min_value=0, max_value=10000, step=100)
bowel = st.checkbox("排便があった")
eating_out = st.checkbox("外食した")

# -------------------------
# 📤 記録 & フィードバック
# -------------------------
if st.button("記録してフィードバック文を生成"):
    # 基礎代謝 BMR（ハリス・ベネディクト式）
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    total_out = int(bmr + exercise_cal)
    diff = cal_in - total_out
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Notion へ送信
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "title": {"title":[{"text":{"content":f"{today} | {weight}kg"}}]},
            "日付": {"date":{"start":today}},
            "体重": {"number":weight},
            "摂取カロリー": {"number":cal_in},
            "消費カロリー": {"number":total_out},
            "差分": {"number":diff},
            "排便": {"checkbox": bowel},
            "たんぱく質": {"number": protein},
            "脂質": {"number": fat},
            "炭水化物": {"number": carbs},
            "睡眠時間": {"number": sleep_hours},
            "水分摂取量": {"number": water},
            "外食": {"checkbox": eating_out}
        }
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if res.status_code in (200, 201):
        st.success("✅ Notion に記録されました！")
    else:
        st.error(f"⚠️ Notion 送信エラー: {res.status_code}")

    # ChatGPT 貼り付け用テキスト（プロンプト自動生成）
    st.markdown("### ChatGPT に貼って分析してもらうプロンプト")
    prompt = f"""
以下のデータを元に、私のダイエットと健康の進捗を以下の観点から詳細に分析してください。

【目標】
- 2025年11月末で体重73kg → 63.6kg（-9.4kg）
- 体脂肪率：32% → 25〜26%
- 胸とお尻に丸みを残しつつ、くびれと背中を引き締めたい

【今日のデータ】
- 体重：{weight}kg
- 摂取カロリー：{cal_in}kcal
- 消費カロリー：{total_out}kcal
- 差分：{diff}kcal
- 排便：{'あり' if bowel else 'なし'}
- PFC：P{protein}g / F{fat}g / C{carbs}g
- 睡眠時間：{sleep_hours}時間
- 水分摂取量：{water}ml
- 外食：{'あり' if eating_out else 'なし'}

【分析してほしい観点】
1. カロリー・PFCバランスの達成度（目標 P90g／1600〜1700kcal）
2. 体重の短期・中期トレンド（前日比／週平均）と進捗評価
3. 排便・腸内環境の状態と改善策（3日以上便がなければ特別対応）
4. 外食や睡眠の影響の仮説と提案
5. 明日の食事／行動プラン提案（停滞打破策も）
6. 最後に、やる気が出るような励ましの言葉

【出力スタイル】
- 客観的・実用的なアドバイス
- データに基づく具体的な提案
- 前向きに続けられるメッセージも添えて
"""
    st.code(prompt)
    st.markdown("---")
