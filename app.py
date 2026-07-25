import streamlit as st
import pandas as pd
from datetime import datetime

# 頁面基本配置（Apple / 科技暗色主題）
st.set_page_config(
    page_title="Stock Recorder | 交易決策與覆盤終端",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 提升介面質感（去雜亂、現代微光擬態）
st.markdown("""
<style>
    /* 全局背景與字型微調 */
    .main {
        background-color: #0b0f19;
    }
    /* 標題與金句樣式 */
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
    /* 卡片式外框 */
    .section-card {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 頁頭 Header ---
st.markdown('<div class="hero-title">📈 股票買賣與每日歷史決策紀錄表</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-quote">「歷史不會重複，但總是吟唱著相同的押韻」—— 記錄當下情境，打造專屬交易系統</div>', unsafe_allow_html=True)

# 使用 Tabs 將「新增紀錄」與「歷史覆盤」分開，徹底告別畫面擁擠！
tab_new, tab_history = st.tabs(["📝 新增交易決策", "📊 歷史決策總覽與覆盤"])

# ==========================================
# TAB 1: 新增交易決策（三步模組化表單）
# ==========================================
with tab_new:
    st.caption("請填寫當下的交易邏輯與心理狀態，點擊底部提交以儲存至資料庫。")
    
    with st.form(key="trade_entry_form", clear_on_submit=True):
        
        # --- 第一區塊：基本屬性與交易參數 ---
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

        # --- 第二區塊：技術面與大盤環境 ---
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

        # --- 第三區塊：催化劑、風控與心態 ---
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

        # 提交按鈕
        submit_button = st.form_submit_button(label="🚀 儲存交易紀錄", use_container_width=True)
        
        if submit_button:
            st.success(f"✅ 已成功紀錄【{symbol_name}】的交易決策！")

# ==========================================
# TAB 2: 歷史決策總覽與覆盤
# ==========================================
with tab_history:
    st.markdown("### 📊 歷史紀錄檢視與事後覆盤")
    
    # 搜尋與篩選列
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔍 搜尋股票代號或關鍵字", placeholder="輸入代號如 NVDA...")
    with col_s2:
        filter_action = st.multiselect("篩選類別", ["買進", "賣出", "加碼", "減碼"], default=["買進", "賣出"])
    
    # 預設展示數據表格 (可替換為實際讀取的 CSV / 資料庫數據)
    dummy_data = pd.DataFrame({
        "交易日期": ["2026-07-20", "2026-07-22"],
        "股票代號/名稱": ["NVDA 輝達", "AAPL 蘋果"],
        "操作": ["買進 (Buy)", "賣出 (Sell)"],
        "成交價": [128.5, 224.3],
        "數量": [100, 50],
        "停損價": [120.0, 215.0],
        "下單心態": ["冷靜客觀", "衝動追高 (FOMO)"],
        "核心理由": ["帶量突破 50日均線，財報催化", "看到大漲急著追入，未達進場點"]
    })
    
    st.dataframe(dummy_data, use_container_width=True, hide_index=True)
    
    # 折疊式事後覆盤區塊
    with st.expander("🔍 針對選定交易進行「事後檢討與覆盤筆記」"):
        review_select = st.selectbox("選擇要覆盤的交易紀錄", dummy_data["股票代號/名稱"].tolist())
        review_note = st.text_area("事後覆盤心得 (這筆交易執行得如何？是否有遵守紀律？)", height=120)
        if st.button("更新覆盤筆記"):
            st.success("✅ 覆盤筆記更新成功！")
