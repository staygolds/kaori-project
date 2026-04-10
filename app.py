import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ページ設定
st.set_page_config(page_title="香りのしごとプロジェクト記録入力", layout="wide")

st.title("🌿 香りのしごとプロジェクト 記録システム")
st.caption("撮影した写真はダウンロードボタンでご自身の端末に保存してください")

# --- リスト読み込み用の関数 ---
def load_list(file_name):
    try:
        df = pd.read_csv(file_name, header=None, encoding='utf-8-sig')
        return df[0].dropna().tolist()
    except:
        try:
            df = pd.read_excel(file_name, header=None)
            return df[0].dropna().tolist()
        except:
            return []

# 各リストの読み込み
staff_names = load_list("職員名.xlsx")
male_users = load_list("男性利用者.xlsx")
female_users = load_list("女性利用者.xlsx")
all_users = sorted(male_users + female_users)

if not staff_names: staff_names = ["（名簿を読み込めませんでした）"]
if not all_users: all_users = ["（名簿を読み込めませんでした）"]

# 保存用フォルダの作成
SAVE_DIR = "records"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

DAILY_LOG_FILE = f"{SAVE_DIR}/daily_report.csv"
INDIVIDUAL_LOG_FILE = f"{SAVE_DIR}/individual_report.csv"

# サイドメニュー
menu = st.sidebar.radio("メニューを選択", ["日報（全体・プロジェクト）", "個別支援記録（利用者別）", "過去の記録を確認"])

# --- モード1：日報（全体） ---
if menu == "日報（全体・プロジェクト）":
    st.header("📝 プロジェクト日報入力")
    
    with st.form("daily_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            date = st.date_input("活動日", datetime.now())
        with col2:
            weather = st.selectbox("天候", ["晴", "曇", "雨", "雪"])
        with col3:
            staff = st.selectbox("記入職員名", staff_names)

        phase = st.multiselect("本日の工程", ["①栽培（屋外）", "②加工（室内）", "③表現（デザイン）", "④販売（接客）"])
        star_user = st.selectbox("本日の「主役」", ["選択してください"] + all_users)
        activity_detail = st.text_area("活動内容の詳細")

        st.subheader("📸 写真を撮影（任意）")
        img_file = st.camera_input("カメラを起動", key="daily_cam")

        st.subheader("✅ 安全・衛生チェック")
        c1, c2, c3 = st.columns(3)
        safety_1 = c1.checkbox("水分補給・休憩の実施")
        safety_2 = c2.checkbox("刃物・道具の管理")
        safety_3 = c3.checkbox("手指消毒・衛生管理")

        submitted = st.form_submit_button("日報を保存する")
        
        if submitted:
            new_data = pd.DataFrame([{
                "日付": date, "天候": weather, "記入者": staff, "工程": ", ".join(phase),
                "本日の主役": star_user, "内容": activity_detail, 
                "安全チェック": f"水分:{safety_1}/道具:{safety_2}/衛生:{safety_3}",
                "画像撮影": "あり" if img_file else "なし"
            }])
            new_data.to_csv(DAILY_LOG_FILE, index=False, mode='a', header=not os.path.exists(DAILY_LOG_FILE), encoding='utf-8-sig')
            st.success("日報を保存しました！")

    if img_file:
        st.write("---")
        st.image(img_file, width=400, caption="撮影された写真")
        st.download_button("写真をダウンロード", img_file, file_name=f"daily_{date}.jpg", mime="image/jpeg")

# --- モード2：個別支援記録（ここを復活させました！） ---
elif menu == "個別支援記録（利用者別）":
    st.header("👤 利用者個別 支援記録")
    
    with st.form("individual_form"):
        col1, col2 = st.columns(2)
        with col1:
            u_date = st.date_input("日付", datetime.now())
            u_name = st.selectbox("利用者氏名", ["選択してください"] + all_users)
        with col2:
            u_category = st.selectbox("重点を置いた適性", ["栽培（体力・ルーティン）", "加工（器用さ・丁寧さ）", "表現（色彩・創作）", "販売（挨拶・交流）"])
        
        u_observation = st.text_area("本日の様子・成長が見られた点")
        u_support = st.text_area("具体的な支援内容（環境調整など）")
        
        st.subheader("📸 本人の活動を撮影（任意）")
        u_img_file = st.camera_input("カメラを起動", key="user_cam")

        u_submitted = st.form_submit_button("個別記録を保存する")
        
        if u_submitted:
            new_u_data = pd.DataFrame([{
                "日付": u_date, "氏名": u_name, "項目": u_category, 
                "様子・成長": u_observation, "支援内容": u_support,
                "画像撮影": "あり" if u_img_file else "なし"
            }])
            new_u_data.to_csv(INDIVIDUAL_LOG_FILE, index=False, mode='a', header=not os.path.exists(INDIVIDUAL_LOG_FILE), encoding='utf-8-sig')
            st.success(f"{u_name}様の記録を保存しました。")

    if u_img_file:
        st.write("---")
        st.image(u_img_file, width=400, caption=f"{u_name}様の活動写真")
        st.download_button("写真をダウンロード", u_img_file, file_name=f"individual_{u_date}_{u_name}.jpg", mime="image/jpeg")

# --- モード3：データ確認 ---
elif menu == "過去の記録を確認":
    st.header("📊 記録の確認と出力")
    
    st.subheader("日報データ")
    if os.path.exists(DAILY_LOG_FILE):
        df_daily = pd.read_csv(DAILY_LOG_FILE)
        st.dataframe(df_daily)
        st.download_button("日報CSVをダウンロード", df_daily.to_csv(index=False, encoding='utf-8-sig'), "daily_reports.csv", "text/csv")

    st.subheader("個別支援データ")
    if os.path.exists(INDIVIDUAL_LOG_FILE):
        df_indiv = pd.read_csv(INDIVIDUAL_LOG_FILE)
        st.dataframe(df_indiv)
        st.download_button("個別記録CSVをダウンロード", df_indiv.to_csv(index=False, encoding='utf-8-sig'), "individual_reports.csv", "text/csv")
