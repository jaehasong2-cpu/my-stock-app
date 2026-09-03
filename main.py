import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 디자인 (따뜻한 톤)
# ==========================================
st.set_page_config(
    page_title="따뜻한 주식 비교 보관소",
    page_icon="📈",
    layout="wide"
)

# 따뜻한 톤을 위한 커스텀 CSS 스타일 적용
st.markdown("""
    <style>
    /* 전체 배경색 설정 (따뜻한 크림/연노랑 톤) */
    .stApp {
        background-color: #FFFDF0;
    }
    /* 메트릭(지표) 카드 스타일 설정 */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 2px solid #FFE082;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 메인 제목 및 안내 문구
# ==========================================
st.title("🌱 따뜻한 주식 비교 보관소")
st.write("두 종목을 한눈에 비교하고 기간별 주가 흐름과 요약 통계(최고/최저/평균가)를 확인해 보세요.")
st.caption("💡 Tip: 한국 주식은 `005930.KS`(삼성전자), `000660.KS`(SK하이닉스) / 미국 주식은 `AAPL`(애플), `NVDA`(엔비디아)")

st.write("---")

# ==========================================
# 3. 사용자 입력창 (2개 종목 & 기간 선택)
# ==========================================
# 종목 입력창을 2개 컬럼으로 나란히 배치
col_input1, col_input2 = st.columns(2)

with col_input1:
    ticker1_input = st.text_input(
        label="🔍 첫 번째 종목 코드",
        value="005930.KS",
        placeholder="예: 005930.KS"
    )

with col_input2:
    ticker2_input = st.text_input(
        label="🔍 두 번째 종목 코드 (선택)",
        value="000660.KS",
        placeholder="예: 000660.KS (비워둘 수 있습니다)"
    )

# 기간 선택 라디오 버튼 (가로로 배치)
period_label = st.radio(
    label="📅 조회할 기간을 선택하세요",
    options=["1개월", "6개월", "1년", "5년"],
    index=2, # 기본값: 1년
    horizontal=True
)

# 선택한 기간에 따른 일수(days) 설정
period_days_map = {
    "1개월": 30,
    "6개월": 180,
    "1년": 365,
    "5년": 365 * 5
}
selected_days = period_days_map[period_label]

# ==========================================
# 4. 데이터 수집 및 처리 함수
# ==========================================
def fetch_stock_data(ticker_symbol, days):
    """yfinance를 통해 데이터를 불러오는 함수"""
    if not ticker_symbol.strip():
        return None, None
    
    code = ticker_symbol.strip().upper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        df = yf.download(code, start=start_date, end=end_date, progress=False)
        if df.empty:
            return None, code
        
        # MultiIndex 컬럼 다듬기
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df, code
    except Exception:
        return None, code

# 두 종목 데이터 수집
df1, code1 = fetch_stock_data(ticker1_input, selected_days)
df2, code2 = fetch_stock_data(ticker2_input, selected_days)

# 두 종목에 사용할 대표 색상 (따뜻한 주황 & 편안한 녹색/파랑 계열)
COLOR1 = "#D97706"  # 주황색
COLOR2 = "#2563EB"  # 파란색

# ==========================================
# 5. 현재가 및 등락률 카드 표시
# ==========================================
st.write("---")

if df1 is None and ticker1_input.strip():
    st.error(f"⚠️ [{code1}] 주가 데이터를 찾을 수 없습니다. 종목 코드를 확인해 주세요.")

if df2 is None and ticker2_input.strip():
    st.error(f"⚠️ [{code2}] 주가 데이터를 찾을 수 없습니다. 종목 코드를 확인해 주세요.")

if df1 is not None:
    # 2개 종목을 비교할 수 있도록 대형 컬럼 나눔
    col_stock1, col_stock2 = st.columns(2)
    
    # ------------------ 종목 1 지표 ------------------
    with col_stock1:
        st.subheader(f"📌 {code1}")
        curr1 = float(df1['Close'].iloc[-1])
        first1 = float(df1['Close'].iloc[0])
        change1 = curr1 - first1
        return1 = (change1 / first1) * 100
        curr_symbol1 = "원" if code1.endswith((".KS", ".KQ")) else "$"
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                label="현재가",
                value=f"{curr1:,.0f} 원" if curr_symbol1 == "원" else f"${curr1:,.2f}"
            )
        with m2:
            st.metric(
                label=f"최근 {period_label} 등락률",
                value=f"{return1:+.2f}%",
                delta=f"{change1:+,.0f} 원" if curr_symbol1 == "원" else f"${change1:+,.2f}"
            )

    # ------------------ 종목 2 지표 ------------------
    if df2 is not None:
        with col_stock2:
            st.subheader(f"📌 {code2}")
            curr2 = float(df2['Close'].iloc[-1])
            first2 = float(df2['Close'].iloc[0])
            change2 = curr2 - first2
            return2 = (change2 / first2) * 100
            curr_symbol2 = "원" if code2.endswith((".KS", ".KQ")) else "$"
            
            m1, m2 = st.columns(2)
            with m1:
                st.metric(
                    label="현재가",
                    value=f"{curr2:,.0f} 원" if curr_symbol2 == "원" else f"${curr2:,.2f}"
                )
            with m2:
                st.metric(
                    label=f"최근 {period_label} 등락률",
                    value=f"{return2:+.2f}%",
                    delta=f"{change2:+,.0f} 원" if curr_symbol2 == "원" else f"${change2:+,.2f}"
                )

    # ==========================================
    # 6. Plotly 라인 차트 (2개 종목 나란히)
    # ==========================================
    st.write("---")
    st.subheader(f"📈 주가 흐름 비교 ({period_label})")
    
    fig = go.Figure()
    
    # 종목 1 선 추가
    fig.add_trace(go.Scatter(
        x=df1.index,
        y=df1['Close'],
        mode='lines',
        name=code1,
        line=dict(color=COLOR1, width=2.5),
        hovertemplate=f'<b>{code1}</b><br>날짜: %{{x|%Y-%m-%d}}<br>주가: %{{y:,.2f}}<extra></extra>'
    ))
    
    # 종목 2 선 추가 (데이터가 있는 경우만)
    if df2 is not None:
        fig.add_trace(go.Scatter(
            x=df2.index,
            y=df2['Close'],
            mode='lines',
            name=code2,
            line=dict(color=COLOR2, width=2.5),
            hovertemplate=f'<b>{code2}</b><br>날짜: %{{x|%Y-%m-%d}}<br>주가: %{{y:,.2f}}<extra></extra>'
        ))
        
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#FFFBEB',
        xaxis=dict(title="날짜", showgrid=True, gridcolor='#FDE68A'),
        yaxis=dict(title="주가", showgrid=True, gridcolor='#FDE68A', tickformat=","),
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # 7. 최고가 / 최저가 / 평균가 요약 카드
    # ==========================================
    st.write("---")
    st.subheader(f"📊 {period_label} 기간 요약 통계")
    
    def render_summary_cards(df, title, color_code):
        """최고가, 최저가, 평균가를 카드로 만들어주는 보조 함수"""
        st.markdown(f"##### <span style='color:{color_code};'>■</span> {title}", unsafe_allow_html=True)
        
        max_price = float(df['Close'].max())
        min_price = float(df['Close'].min())
        avg_price = float(df['Close'].mean())
        
        unit = "원" if title.endswith((".KS", ".KQ")) else "$"
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                label="🔴 기간 최고가",
                value=f"{max_price:,.0f} 원" if unit == "원" else f"${max_price:,.2f}"
            )
        with c2:
            st.metric(
                label="🔵 기간 최저가",
                value=f"{min_price:,.0f} 원" if unit == "원" else f"${min_price:,.2f}"
            )
        with c3:
            st.metric(
                label="🟡 기간 평균가",
                value=f"{avg_price:,.0f} 원" if unit == "원" else f"${avg_price:,.2f}"
            )

    # 종목별 요약 카드 출력
    if df2 is not None:
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            render_summary_cards(df1, code1, COLOR1)
        with col_stat2:
            render_summary_cards(df2, code2, COLOR2)
    else:
        render_summary_cards(df1, code1, COLOR1)
