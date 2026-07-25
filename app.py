import streamlit as st
import pandas as pd
import datetime

# 頁面標題與寬螢幕佈局設定
st.set_page_config(page_title="股票歷史決策與走勢覆盤系統", layout="wide", page_icon="📈")

st.title("📈 股票買賣與每日歷史決策紀錄表")
st.caption("「歷史不會重複，但總是吟唱著相同的押韻」—— 記錄當下情境，打造專屬交易系統")

# 初始化 Session State 來存放當前交易紀錄
if "journal_data" not in st.session_state:
    st.session_state.journal_data = pd.DataFrame(columns=[
        "交易日期", "股票標的", "操作類別", "策略週期", "買賣價格", "部位數量",
        "當前走勢", "關鍵支撐", "關鍵壓力", "量能與型態",
        "大盤環境", "當下新聞與事件", "觸發買賣核心理由",
        "預設停損", "預設停利", "下單心態", "歷史走勢對照與覆盤"
    ])

# 頁面分頁設計
tab1, tab2 = st.tabs(["📝 新增交易決策紀錄", "📊 歷史決策總覽與覆盤"])

# ==================== 分頁 1: 新增紀錄 ====================
with tab1:
    st.subheader("新增交易 / 每日決策覆盤")
    
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 1. 基本屬性")
            trade_date = st.date_input("交易日期", datetime.date.today())
            stock_symbol = st.text_input("股票代號與名稱", placeholder="例如：2330 台積電")
            trade_action = st.selectbox("操作類別", ["買進", "加碼", "減碼", "獲利停利", "嚴格停損", "觀望"])
            strategy_type = st.selectbox("策略週期", ["短線 (1-3天)", "波段 (數周~數月)", "長線 (半年以上)", "當沖"])
            price = st.number_input("成交單價", min_value=0.0, step=0.5)
            quantity = st.number_input("數量 (股/張)", min_value=0, step=1000)

        with col2:
            st.markdown("##### 2. 技術面與大盤")
            trend = st.selectbox("當前走勢", ["多頭排列", "箱型整理", "跌深反彈", "空頭初跌", "打底階段"])
            support = st.text_input("關鍵支撐位", placeholder="例如：月線 $1000、前低 $980")
            resistance = st.text_input("關鍵壓力位", placeholder="例如：前高 $1080、整數 $1100")
            volume_pattern = st.text_input("量能與型態", placeholder="例如：帶量突破箱型、量縮回測")
            market_env = st.text_area("大盤環境與籌碼", placeholder="例如：加權站穩月線、外資連三買")

        with col3:
            st.markdown("##### 3. 催化劑與心態")
            news_event = st.text_area("當下新聞/催化劑", placeholder="例如：營收創新高、法說會展望優")
            reason = st.text_area("為什麼「當下」下單？(核心理由)", placeholder="例如：帶量突破型態＋基本面利多，風報酬比 1:3")
            stop_loss = st.number_input("預設停損價位", min_value=0.0, step=0.5)
            take_profit = st.number_input("預設停利價位", min_value=0.0, step=0.5)
            mindset = st.select_slider("下單當下心態", options=["極度恐慌", "冷靜計畫執行", "衝動追高 (FOMO)"])
            review = st.text_area("歷史對照與事後覆盤", placeholder="例如：型態像今年3月突破，事後證明停損設定合理")

        submitted = st.form_submit_button("💾 儲存這筆決策紀錄")
        
        if submitted:
            new_data = {
                "交易日期": str(trade_date), "股票標的": stock_symbol, "操作類別": trade_action,
                "策略週期": strategy_type, "買賣價格": price, "部位數量": quantity,
                "當前走勢": trend, "關鍵支撐": support, "關鍵壓力": resistance,
                "量能與型態": volume_pattern, "大盤環境": market_env,
                "當下新聞與事件": news_event, "觸發買賣核心理由": reason,
                "預設停損": stop_loss, "預設停利": take_profit,
                "下單心態": mindset, "歷史走勢對照與覆盤": review
            }
            new_df = pd.DataFrame([new_data])
            st.session_state.journal_data = pd.concat([st.session_state.journal_data, new_df], ignore_index=True)
            st.success(f"成功儲存！【{stock_symbol}】的交易紀錄已寫入歷史資料庫。")

# ==================== 分頁 2: 檢視與檢討 ====================
with tab2:
    st.subheader("📚 歷史交易資料庫與覆盤總覽")
    
    df = st.session_state.journal_data
    if df.empty:
        st.info("目前尚無筆記，請至第一個分頁填寫並提交紀錄！")
    else:
        selected_stock = st.selectbox("依股票標的篩選", ["全部"] + list(df["股票標的"].unique()))
        filtered_df = df if selected_stock == "全部" else df[df["股票標的"] == selected_stock]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # 提供一鍵匯出成 CSV 檔案功能
        csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("📥 匯出歷史紀錄 (.csv)", data=csv_data, file_name="trading_journal.csv", mime="text/csv")
