import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. 頁面基本配置
st.set_page_config(
    page_title="Stock Recorder | 交易決策與覆盤終端",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 質感
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

# 取得 Secrets 中的設定
WEB_APP_URL = st.secrets.get("GOOGLE_WEB_APP_URL", "")
CSV_URL = st.secrets.get("GOOGLE_SHEET_CSV_URL", "")

# 讀取 Google Sheets 最新數據
@st.cache_data(ttl=5)
def fetch_sheet_data(url):
    if not url:
        return None
    try:
        df = pd.read_csv(url, encoding="utf-8")
        return df
    except Exception:
        return None

# 自動 FIFO 配對算損益的核心引擎（型態安全防護版）
def calculate_trade_pnl(df):
    if df is None or df.empty:
        return df

    df = df.copy()

    # 1. 彈性抓取「數量」欄位
    qty_col = None
    for possible_name in ["數量", "数量", "股數", "Quantity", "qty"]:
        if possible_name in df.columns:
            qty_col = possible_name
            break
            
    if qty_col:
        df["數量"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0.0).astype(float)
    else:
        df["數量"] = 0.0

    # 2. 彈性抓取「成交價」與「操作」欄位
    if "成交價" in df.columns:
        df["成交價"] = pd.to_numeric(df["成交價"], errors="coerce").fillna(0.0).astype(float)
    else:
        df["成交價"] = 0.0

    if "操作" not in df.columns:
        df["操作"] = "買進 (Buy)"

    # 3. 強制指定 float64 型態，避免 TypeError
    df["損益金額"] = pd.to_numeric(df.get("損益金額", 0), errors="coerce").fillna(0.0).astype(float)
    df["報酬率"] = pd.to_numeric(df.get("報酬率", 0), errors="coerce").fillna(0.0).astype(float)

    # 4. FIFO 配對計算
    inventory = {} # {symbol: [{'price': p, 'qty': q}]}

    for idx in range(len(df)):
        row = df.iloc[idx]
        symbol = str(row.get("股票代號/名稱", "")).strip()
        action = str(row.get("操作", ""))
        price = float(row.get("成交價", 0.0))
        qty = float(row.get("數量", 0.0))
        current_pnl = float(row.get("損益金額", 0.0))
        
        # 若試算表已手動寫死非 0 損益則跳過
        if current_pnl != 0.0:
            continue

        if symbol not in inventory:
            inventory[symbol] = []

        # 買進對應邏輯
        if any(keyword in action for keyword in ["買進", "Buy", "加碼"]):
            if qty > 0:
                inventory[symbol].append({'price': price, 'qty': qty})
        
        # 賣出對應邏輯
        elif any(keyword in action for keyword in ["賣出", "Sell", "減碼"]):
            sell_qty = qty
            realized_pnl = 0.0
            total_cost = 0.0

            # 先進先出對沖
            while sell_qty > 0 and len(inventory[symbol]) > 0:
                buy_batch = inventory[symbol][0]
                matched_qty = min(sell_qty, buy_batch['qty'])

                cost = matched_qty * buy_batch['price']
                revenue = matched_qty * price
                realized_pnl += (revenue - cost)
                total_cost += cost

                buy_batch['qty'] -= matched_qty
                sell_qty -= matched_qty

                if buy_batch['qty'] <= 0:
                    inventory[symbol].pop(0)

            # loc 安全賦值
            df.loc[df.index[idx], "損益金額"] = float(round(realized_pnl, 2))
            if total_cost > 0:
                df.loc[df.index[idx], "報酬率"] = float(round((realized_pnl / total_cost) * 100, 2))

    return df

# --- 頁頭 Header ---
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
            quantity = st.number_input("數量 (股/張)", min_value=0.1, step=1.0)

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
                    "核心理由": core_reason,
                    "平倉現價": 0.0,
                    "損益金額": 0.0,
                    "報酬率": 0.0
                }
                
                try:
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success(f"✅ 成功寫入 Google Sheets！【{symbol_name}】紀錄已更新。")
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ 寫入失敗，HTTP 狀態碼: {res.status_code}")
                except Exception as e:
                    st.error(f"❌ 連線發生錯誤: {e}")

# ==========================================
# TAB 2: 歷史決策總覽與覆盤
# ==========================================
with tab_history:
    st.markdown("### 📊 歷史紀錄與統計驗證")
    
    if not CSV_URL:
        st.warning("⚠️ 請至 Streamlit Secrets 設定 GOOGLE_SHEET_CSV_URL。")
    else:
        raw_df = fetch_sheet_data(CSV_URL)
        
        if raw_df is None or raw_df.empty:
            st.info("💡 目前歷史資料庫為空，請先新增交易紀錄。")
        else:
            # 依日期排序並進行全域 FIFO 對沖計算
            if "交易日期" in raw_df.columns:
                raw_df["交易日期"] = pd.to_datetime(raw_df["交易日期"]).dt.date
                raw_df = raw_df.sort_values(by="交易日期").reset_index(drop=True)
            
            # 1. 計算全域正確損益（跨月對沖）
            df_calculated = calculate_trade_pnl(raw_df)
            
            # 2. 建立月份欄位供動態篩選
            df_calculated["月份"] = pd.to_datetime(df_calculated["交易日期"]).dt.strftime("%Y-%m")
            available_months = ["全部歷史 (All Time)"] + sorted(list(df_calculated["月份"].unique()), reverse=True)

            # 上方控置列：刷新按鈕與月份選擇器
            col_filter, col_btn, col_info = st.columns([2, 1, 3])
            with col_filter:
                selected_month = st.selectbox("📅 選擇分析月份", available_months)
            with col_btn:
                st.write("") # 垂直置中調效
                st.write("")
                if st.button("🔄 重新整理", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            with col_info:
                st.caption("💡 說明：系統先進行全歷史買賣對沖演算，再根據所選月份精準展現當月勝率與已實現損益。")

            st.divider()

            # 3. 根據選取月份過濾資料
            if selected_month == "全部歷史 (All Time)":
                df = df_calculated.copy()
            else:
                df = df_calculated[df_calculated["月份"] == selected_month].copy()

            # 計算當前檢視範圍的累積損益
            df["累積損益"] = df["損益金額"].cumsum()

            # 計算統計數字（以平倉賣出單為主）
            sell_trades = df[df["操作"].astype(str).str.contains("賣出|Sell|減碼")]
            total_sells = len(sell_trades)
            winning_trades = len(sell_trades[sell_trades["損益金額"] > 0])
            losing_trades = len(sell_trades[sell_trades["損益金額"] < 0])
            
            win_rate = (winning_trades / total_sells * 100) if total_sells > 0 else 0.0
            total_pnl = df["損益金額"].sum()
            avg_roi = sell_trades["報酬率"].mean() if total_sells > 0 else 0.0

            # --- 頂部指標面板 ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("當前檢視筆數", f"{len(df)} 筆", f"已平倉 {total_sells} 筆")
            m2.metric("勝率 (Win Rate)", f"{win_rate:.1f}%", f"{winning_trades} 勝 / {losing_trades} 負")
            m3.metric("累積已實現淨損益", f"${total_pnl:,.2f}", delta=f"${total_pnl:,.2f}")
            m4.metric("平均平倉報酬率", f"{avg_roi:+.2f}%")

            st.divider()

            # --- 資金成長曲線圖 ---
            st.markdown(f"### 📈 資金成長曲線 - {selected_month}")
            
            fig_equity = px.line(
                df, 
                x="交易日期", 
                y="累積損益", 
                title=f"資產權益成長走勢圖 ({selected_month})",
                markers=True,
                hover_data=["股票代號/名稱", "操作", "成交價", "損益金額", "報酬率"]
            )
            fig_equity.update_traces(line_color="#10b981", line_width=3)
            fig_equity.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="日期",
                yaxis_title="累積損益 ($)"
            )
            st.plotly_chart(fig_equity, use_container_width=True)

            # 兩欄式統計圖表
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### 🎯 策略週期分佈")
                if "策略週期" in df.columns:
                    fig_pie = px.pie(
                        df, 
                        names="策略週期", 
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)

            with chart_col2:
                st.markdown("#### 📊 單筆平倉報酬率 (%)")
                if not sell_trades.empty:
                    fig_bar = px.bar(
                        sell_trades, 
                        x="股票代號/名稱", 
                        y="報酬率",
                        color="報酬率",
                        color_continuous_scale=["#ef4444", "#94a3b8", "#10b981"],
                        hover_data=["交易日期", "損益金額"]
                    )
                    fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("當前篩選範圍內無賣出平倉紀錄。")

            st.divider()

            # --- 詳細歷史清單 ---
            st.markdown("### 📋 歷史明細清單")
            search_term = st.text_input("🔍 搜尋股票代號 / 核心理由", "")
            
            df_display = df.drop(columns=["月份"], errors="ignore")
            if search_term:
                df_display = df_display[
                    df_display["股票代號/名稱"].astype(str).str.contains(search_term, case=False, na=False) |
                    df_display["核心理由"].astype(str).str.contains(search_term, case=False, na=False)
                ]
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
