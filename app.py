import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 頁面配置
st.set_page_config(
    page_title="Stock Recorder | 交易決策與覆盤終端",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0b0f19; }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-quote {
        color: #10b981;
        font-size: 1.05rem;
        font-weight: 500;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 取得 Secrets 中的 Google Web App API 網址
WEB_APP_URL = st.secrets.get("GOOGLE_WEB_APP_URL", "")

st.markdown('<div class="hero-title">📈 股票買賣與每日歷史決策紀錄表</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-quote">「歷史不會重複，但總是吟唱著相同的押韻」—— 記錄當下情境，打造專屬交易系統</div>', unsafe_allow_html=True)

tab_new, tab_history = st.tabs(["📝 新增交易決策", "📊 歷史決策總覽與覆盤"])

# ==========================================
# TAB 1: 新增交易決策
# ==========================================
with tab_new:
    st.caption("請填寫當下的交易邏輯與心理狀態，點擊底部提交以同步儲存至 Google Sheets。")
    
    with st.form(key="trade_entry_form", clear_on_submit=True):
        st.markdown("### 1. 基本屬性與交易參數")
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_date = st.date_input("交易日期", datetime.now())
            symbol_name = st.text_input("股票代號與名稱", placeholder="例: NVDA 輝達 / 2330 台積電")
        with col2:
            action_type = st.selectbox("操作類別", ["買進 (Buy)", "賣出 (Sell)", "加碼 (Add)", "減碼 (Reduce)", "觀察紀錄 (Watch)"])
            strategy_period = st.selectbox("策略週期", ["超短線 (Day Trade)", "波段交易 (Swing)", "趨勢中長線 (Trend)", "長期配置 (Long-term)"])
        with col3:
            price = st.number_input("成交單價", min_value=0.0, step=0.1, format="%.2f")
            quantity = st.number_input("數量 (股/張)", min_value=1, step=1)

        st.divider()

        st.markdown("### 2. 技術面與大盤環境")
        col4, col5 = st.columns(2)
        with col4:
            trend_status = st.selectbox("當前走勢型態", ["突破前高 (Breakout)", "量縮回測 (Pullback)", "底部打底 (Base)", "高檔震盪 (Consolidation)", "空頭反彈 (Rebound)"])
            support_level = st.text_input("關鍵支撐位", placeholder="例: 50MA (120$) / 前低點")
            resistance_level = st.text_input("關鍵壓力位", placeholder="例: 歷史高點 (140$) / 均線反壓")
        with col5:
            volume_pattern = st.text_input("量能與型態特徵", placeholder="例: 帶量突破 2 倍均量 / 縮量整理")
            market_env = st.text_input("大盤環境與籌碼流向", placeholder="例: 那斯達克站上月線 / 外資連續買超")

        st.divider()

        st.markdown("### 3. 催化劑與風險心態控制")
        col6, col7 = st.columns(2)
        with col6:
            catalyst = st.text_input("當下新聞 / 催化劑", placeholder="例: 財報超預期 (Earnings Beat) / 降息預期")
            stop_loss = st.number_input("預設停損價位", min_value=0.0, step=0.1, format="%.2f")
            take_profit = st.number_input("預設停利價位", min_value=0.0, step=0.1, format="%.2f")
        with col7:
            mindset = st.select_slider(
                "下單當下心態評估",
                options=["極度恐慌", "謹慎依據計畫", "冷靜客觀", "稍微著急", "衝動追高 (FOMO)"],
                value="冷靜客觀"
            )
            core_reason = st.text_area("為什麼「當下」下單？(核心理由)", placeholder="請簡述當下非買/賣不可的核心邏輯...", height=100)

        submit_button = st.form_submit_button(label="🚀 儲存至 Google Sheets 資料庫", use_container_width=True)
        
        if submit_button:
            if not symbol_name:
                st.warning("⚠️ 請輸入股票代號與名稱！")
            elif not WEB_APP_URL:
                st.error("⚠️ 請在 Streamlit Secrets 設定 GOOGLE_WEB_APP_URL！")
            else:
                payload = {
                    "交易日期": str(trade_date),
                    "股票代號/名稱": symbol_name,
                    "操作": action_type,
                    "策略週期": strategy_period,
                    "成交價": price,
                    "數量": quantity,
                    "關鍵支撐": support_level,
                    "關鍵壓力": resistance_level,
                    "量能型態": volume_pattern,
                    "大盤籌碼": market_env,
                    "催化劑": catalyst,
                    "停損價": stop_loss,
                    "停利價": take_profit,
                    "下單心態": mindset,
                    "核心理由": core_reason
                }
                
                try:
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ 成功寫入 Google Sheets！【{symbol_name}】紀錄已更新。")
                    else:
                        st.error(f"❌ 寫入失敗，HTTP 狀態碼: {res.status_code}")
                except Exception as e:
                    st.error(f"❌ 連線發生錯誤: {e}")

# ==========================================
# TAB 2: 歷史決策總覽與覆盤
# ==========================================
with tab_history:
    st.markdown("### 📊 歷史紀錄檢視")
    st.info("💡 提醒：你可以隨時開啟 Google Sheets 直接進行資料刪除、修改與後台維護。")
    if st.button("🔄 重新整理資料庫"):
        st.rerun()
