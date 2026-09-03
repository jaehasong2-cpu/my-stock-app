import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. 페이지 기본 설정 및 디자인 (따뜻한 톤)
# ==========================================
st.set_page_config(
    page_title="따뜻한 주식 차트 보관소",
    page_icon="📈",
    layout="centered"
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
        padding: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 메인 제목 및 안내 문구
# ==========================================
st.title("🌱 따뜻한 주식 차트 보관소")
st.write("주식 종목 코드를 입력하시면 최근 1년 동안의 주가 흐름을 한눈에 알기 쉽게 보여드립니다.")
st.caption("💡 Tip: 한국 주식은 `005930.KS`(삼성전자), `000660.KS`(SK하이닉스) / 미국 주식은 `AAPL`(애플), `TSLA`(테슬라)")

# ==========================================
# 3. 사용자 입력창
# ==========================================
# 기본 입력값으로 '005930.KS' (삼성전자) 설정
ticker_input = st.text_input(
    label="🔍 궁금한 주식의 종목 코드를 입력하세요",
    value="005930.KS",
    placeholder="예: 005930.KS 또는 AAPL"
)

# 입력값이 있을 때 주가 데이터 가져오기 실행
if ticker_input:
    # 입력된 종목 코드의 대문자 변환 및 양쪽 공백 제거
    ticker_code = ticker_input.strip().upper()
    
    # 최근 1년 기간 계산 (오늘부터 365일 전까지)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # yfinance 라이브러리로 주가 데이터 다운로드
    try:
        stock_data = yf.download(ticker_code, start=start_date, end=end_date, progress=False)
        
        # 데이터가 없는 비정상적인 종목 코드 처리
        if stock_data.empty:
            st.error("⚠️ 주가 데이터를 찾을 수 없습니다. 종목 코드가 올바른지 확인해 주세요.")
        else:
            # yfinance 최신 버전의 MultiIndex 컬럼 다듬기
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.get_level_values(0)

            # ==========================================
            # 4. 주요 지표 계산 (현재가 & 1년 등락률)
            # ==========================================
            # 가장 최근 종가와 1년 전 첫 거래일 종가 추출
            current_price = float(stock_data['Close'].iloc[-1])
            first_price = float(stock_data['Close'].iloc[0])
            
            # 1년간 가격 변동액 및 변동률(%) 계산
            price_change = current_price - first_price
            return_rate = (price_change / first_price) * 100
            
            # 통화 단위 구분 (.KS, .KQ로 끝나면 원화, 그 외는 달러)
            currency_symbol = "원" if ticker_code.endswith((".KS", ".KQ")) else "$"
            
            # 지표 카드를 나란히 놓기 위한 2개 컬럼 생성
            col1, col2 = st.columns(2)
            
            with col1:
                # 현재가 표시
                formatted_price = f"{current_price:,.0f} 원" if currency_symbol == "원" else f"${current_price:,.2f}"
                st.metric(
                    label="📌 현재 주가",
                    value=formatted_price
                )
                
            with col2:
                # 1년 등락률 및 등락금액 표시 (자동으로 상승/하락 색상 반영)
                formatted_change = f"{price_change:+,.0f} 원" if currency_symbol == "원" else f"${price_change:+,.2f}"
                st.metric(
                    label="📊 최근 1년 등락률",
                    value=f"{return_rate:+.2f}%",
                    delta=formatted_change
                )

            # ==========================================
            # 5. Plotly 꺾은선 차트 시각화
            # ==========================================
            st.write("---")
            st.subheader(f"📈 [{ticker_code}] 최근 1년 주가 흐름")
            
            # Plotly 그래프 객체 생성
            fig = go.Figure()
            
            # 주가 꺾은선 추세선 추가 (따뜻한 앰버/주황색)
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name='종가',
                line=dict(color='#D97706', width=2.5),
                hovertemplate='<b>날짜</b>: %{x|%Y-%m-%d}<br><b>주가</b>: %{y:,.2f}<extra></extra>'
            ))
            
            # 차트의 배경색, 축, 레이아웃 세부 설정
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', # 전체 바탕 투명 처리
                plot_bgcolor='#FFFBEB',          # 그래프 내부 연한 주황/크림 배경
                xaxis=dict(
                    title="날짜",
                    showgrid=True,
                    gridcolor='#FDE68A'
                ),
                yaxis=dict(
                    title=f"주가 ({currency_symbol})",
                    showgrid=True,
                    gridcolor='#FDE68A',
                    tickformat=","
                ),
                margin=dict(l=20, r=20, t=30, b=20),
                hovermode="x unified"
            )
            
            # 스트림릿에 Plotly 그래프 출력
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
