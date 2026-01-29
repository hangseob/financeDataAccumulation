import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import streamlit.components.v1 as components
import time
import random
import traceback

# 프로젝트 루트를 path에 추가하여 basic_library 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from basic_library.oracle_db import get_available_curves, get_all_curve_data, get_available_dates
    from basic_library.tenor_conventions import tenor_name_to_year_fraction
except Exception as e:
    st.error(f"Import Error: {e}")
    print(f"Import Error: {e}")
    traceback.print_exc()
    st.stop()

# 페이지 설정
st.set_page_config(page_title="Interest Rate Curve Viewer", layout="wide")

# --- 전역 CSS ---
st.markdown("""
<style>
    section.main { scroll-behavior: auto !important; overflow-anchor: none !important; }
    .stApp { overflow-anchor: none !important; }
</style>
""", unsafe_allow_html=True)

# --- [로그 시스템] ---
def log_feedback(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    try:
        with open("streamlit_log.txt", "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except (PermissionError, Exception):
        pass

# --- 초정밀 스크롤 보존 (강화된 requestAnimationFrame) ---
def preserve_scroll(rid):
    components.html(
        f"""
        <script>
        (function() {{
            const parentDoc = window.parent.document;
            const parentWin = window.parent;
            
            const getScrollEl = () => parentDoc.querySelector('section[data-testid="stMain"]') || parentDoc.querySelector('section.main');
            
            const getSavedPos = () => parseInt(parentWin.sessionStorage.getItem('st_scroll_y') || '0');
            
            // 스크롤 복구 (여러 프레임에 걸쳐 반복 시도)
            const restoreScroll = (attempts = 5) => {{
                const savedPos = getSavedPos();
                if (savedPos <= 0) return;
                
                const doRestore = (remaining) => {{
                    if (remaining <= 0) return;
                    parentWin.requestAnimationFrame(() => {{
                        const el = getScrollEl();
                        if (el && el.scrollTop < savedPos - 20) {{
                            el.scrollTop = savedPos;
                            // 다음 프레임에서 다시 확인/시도
                            setTimeout(() => doRestore(remaining - 1), 16);
                        }}
                    }});
                }};
                
                doRestore(attempts);
            }};
            
            // 스크롤 저장 (자연스러운 스크롤만)
            const saveScroll = () => {{
                const el = getScrollEl();
                if (el && el.scrollTop > 0) {{
                    const currentSaved = getSavedPos();
                    if (Math.abs(el.scrollTop - currentSaved) < 500 || currentSaved === 0) {{
                        parentWin.sessionStorage.setItem('st_scroll_y', el.scrollTop);
                    }}
                }}
            }};
            
            // 스크롤 리스너 등록
            const attachListener = () => {{
                const el = getScrollEl();
                if (el && !el.dataset.scrollListenerAttached) {{
                    el.addEventListener('scroll', saveScroll, {{ passive: true }});
                    el.dataset.scrollListenerAttached = 'true';
                }}
            }};
            
            // 즉시 복구 시도
            attachListener();
            restoreScroll(10);
            
            // 영구적 interval (50ms 주기)
            if (!parentWin.__scrollInterval) {{
                parentWin.__scrollInterval = setInterval(() => {{
                    attachListener();
                    const el = getScrollEl();
                    const savedPos = getSavedPos();
                    // 스크롤이 튀었으면 복구
                    if (el && savedPos > 0 && el.scrollTop < savedPos - 20) {{
                        restoreScroll(5);
                    }}
                }}, 50);
            }}
            
            // MutationObserver
            if (!parentWin.__scrollPreserverActive) {{
                parentWin.__scrollPreserverActive = true;
                
                const observer = new MutationObserver(() => {{
                    attachListener();
                    restoreScroll(10);
                }});
                
                observer.observe(parentDoc.body, {{ childList: true, subtree: true }});
            }}
        }})();
        </script>
        <div style="display:none" id="scroll-trigger-{rid}"></div>
        """,
        height=0,
    )

# --- 캐싱 및 데이터 처리 ---
@st.cache_data(ttl=3600)
def cached_available_curves(): return get_available_curves()

@st.cache_data(ttl=3600)
def cached_available_dates(curve_id): return get_available_dates(curve_id)

@st.cache_data(ttl=3600)
def cached_curve_data(curve_id, start_date, end_date):
    df = get_all_curve_data(curve_id, start_date, end_date)
    if not df.empty:
        # 데이터 정제: MID 값이 None인 경우 0으로 처리하거나 제외
        df['MID'] = pd.to_numeric(df['MID'], errors='coerce').fillna(0.0)
        df['MID'] = df['MID'] * 100.0
        df['year_fraction'] = df['TENOR_NAME'].apply(tenor_name_to_year_fraction)
        df = df.sort_values(['TDATE', 'year_fraction']).reset_index(drop=True)
        df = df[(df['TDATE'] >= start_date) & (df['TDATE'] <= end_date)]
    return df

@st.cache_resource
def get_plotly_frames(df, anim_dates, curve_id):
    grouped = df.groupby('TDATE')
    frames = []
    for d in anim_dates:
        if d in grouped.groups:
            day_data = grouped.get_group(d)
            frames.append(go.Frame(
                data=[go.Scatter(x=day_data['plot_x'], y=day_data['MID'])],
                name=d,
                layout=go.Layout(title_text=f"Curve: {curve_id}")
            ))
    return frames

@st.cache_data(ttl=3600)
def get_collapsed_df(df, threshold, enabled):
    df_res = df.copy()
    if not enabled:
        df_res['plot_x'] = df_res['year_fraction']
    else:
        unique_fractions = sorted(df_res['year_fraction'].unique())
        x_map = {f: (f if f <= threshold else threshold + i + 1) for i, f in enumerate([f for f in unique_fractions if f > threshold])}
        x_map.update({f: f for f in unique_fractions if f <= threshold})
        df_res['plot_x'] = df_res['year_fraction'].map(x_map)
    return df_res

st.title("📈 Real-time Interest Rate Curve Viewer")

# --- 전역 스크롤 보존 (최상단 배치) ---
rid_global = random.randint(0, 1000000)
preserve_scroll(rid_global)

# 1. 사이드바 설정 (키를 부여하여 안정화)
st.sidebar.header("Data Selection")
available_curves = cached_available_curves()

if not available_curves:
    st.error("❌ 사용 가능한 커브 데이터가 없습니다. DB 연결을 확인해 주세요.")
    st.stop()

curve_id = st.sidebar.selectbox(
    "Select Curve ID", 
    options=available_curves, 
    index=available_curves.index("KRWQ3L") if "KRWQ3L" in available_curves else 0, 
    key="curve_selector"
)

all_dates = cached_available_dates(curve_id)
if not all_dates:
    st.warning(f"⚠️ '{curve_id}' 커브에 대한 날짜 데이터가 없습니다.")
    st.stop()

st.sidebar.subheader("Data Period")
min_date_val = datetime.strptime(all_dates[0], "%Y%m%d")
max_date_val = datetime.strptime(all_dates[-1], "%Y%m%d")

col1, col2 = st.sidebar.columns(2)
with col1: anim_start_date = st.date_input("Start Date", value=min_date_val, key="period_start")
with col2: anim_end_date = st.date_input("End Date", value=max_date_val, key="period_end")

start_str = anim_start_date.strftime("%Y%m%d")
end_str = anim_end_date.strftime("%Y%m%d")

# --- 세션 상태 관리 (날짜 기반으로 변경) ---
if 'selected_date' not in st.session_state: st.session_state.selected_date = all_dates[0]
if 'is_cached' not in st.session_state: st.session_state.is_cached = False
if 'date_info_msg' not in st.session_state: st.session_state.date_info_msg = ""
current_config = (curve_id, start_str, end_str)
if 'last_config' not in st.session_state: st.session_state.last_config = current_config

# 설정 변경 감지 시
if st.session_state.last_config != current_config:
    st.session_state.selected_date = start_str
    st.session_state.is_cached = False
    st.session_state.date_info_msg = ""
    st.session_state.last_config = current_config

full_df = cached_curve_data(curve_id, start_str, end_str)
if full_df.empty: 
    st.warning(f"선택한 범위 내에 데이터가 없습니다.")
    st.stop()

global_mid_min, global_mid_max = full_df['MID'].min(), full_df['MID'].max()

# --- 콜백 함수 (날짜 기반 업데이트) ---
def sync_from_input():
    if "goto_date_input" in st.session_state:
        raw_val = st.session_state.goto_date_input.strip()
        if not raw_val: return
        target_date_obj = None
        for fmt in ["%Y%m%d", "%Y.%m.%d", "%Y-%m-%d"]:
            try: target_date_obj = datetime.strptime(raw_val, fmt); break
            except ValueError: continue
        if not target_date_obj: st.session_state.date_info_msg = "⚠️ 날짜 형식이 잘못되었습니다"; return
        target_date_str = target_date_obj.strftime("%Y%m%d")
        
        c = st.session_state.last_config
        if target_date_str < c[1] or target_date_str > c[2]:
            st.session_state.date_info_msg = f"⚠️ 입력한 날짜({raw_val})가 Data Period 범위를 벗어났습니다."
            return
            
        active_dates = sorted(full_df['TDATE'].unique().tolist())
        if target_date_str in active_dates:
            st.session_state.selected_date = target_date_str
            st.session_state.date_info_msg = ""
        else:
            next_dates = [d for d in active_dates if d > target_date_str]
            if next_dates:
                next_date = next_dates[0]
                st.session_state.selected_date = next_date
                st.session_state.date_info_msg = f"ℹ️ {raw_val}에 데이터가 없어 다음 데이터({next_date})를 보여드립니다."
            else: st.session_state.date_info_msg = f"⚠️ {raw_val} 이후의 데이터가 존재하지 않습니다."

# --- 메인 프래그먼트 ---
@st.fragment
def render_chart_and_controls(current_full_df):
    dates = sorted(current_full_df['TDATE'].unique().tolist())
    # 현재 선택된 날짜가 리스트에 없으면 보정
    if st.session_state.selected_date not in dates:
        st.session_state.selected_date = dates[0]
        
    current_date = st.session_state.selected_date
    idx = dates.index(current_date)
    
    log_feedback(f"Fragment Rerender - Config: {st.session_state.last_config}, Selected: {current_date}")

    c1, c2, c3, c4 = st.columns([1, 1, 1.5, 1.5])
    with c1: collapse_on = st.checkbox("Tenor Collapse", value=False)
    with c2: threshold = st.number_input("Threshold", 1, 30, 5, disabled=not collapse_on, label_visibility="collapsed")
    with c3: y_min_val = st.number_input("Y-Min (%)", value=None, format="%.2f", placeholder="Y-Min (%)", label_visibility="collapsed")
    with c4:
        if st.button("⚡ Cache for Anim", width='stretch', type="primary" if not st.session_state.is_cached else "secondary"):
            st.session_state.is_cached = True
            st.rerun()

    processed_df = get_collapsed_df(current_full_df, threshold, collapse_on)
    df_current = processed_df[processed_df['TDATE'] == current_date]
    y_min = y_min_val if y_min_val is not None else (global_mid_min - 0.2)
    y_max = (global_mid_max + 0.2) if y_min_val is None else (processed_df['MID'].max() + 0.2)

    with st.container():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_current['plot_x'], 
            y=df_current['MID'], 
            mode='lines+markers', 
            text=df_current['TENOR_NAME'], 
            hovertemplate='Tenor: %{text}<br>MID: %{y:.4f}%<extra></extra>', 
            line=dict(color='red', width=3), 
            marker=dict(size=8, color='red'), 
            name="Yield Curve"
        ))

        # X축 틱 설정을 위해 유니크한 테너 정보 추출 (정렬됨)
        unique_tenors = processed_df[['plot_x', 'TENOR_NAME', 'year_fraction']].drop_duplicates().sort_values('year_fraction')

        if st.session_state.is_cached:
            fig.frames = get_plotly_frames(processed_df, tuple(dates), curve_id)
            target_duration = max(25.0, 5000.0 / len(dates))
            fig.update_layout(
                title_text=f"Curve: {curve_id}",
                updatemenus=[
                    dict(type="buttons", direction="left", x=0, y=-0.15, xanchor="left", yanchor="top",
                         buttons=[dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=target_duration, redraw=False), fromcurrent=True, mode="immediate")]),
                                  dict(label="⏸️ Pause", method="animate", args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")])]),
                    dict(type="dropdown", direction="down", x=0.15, y=-0.15, xanchor="left", yanchor="top", showactive=True,
                         buttons=[dict(label=f"Speed: {m}x", method="relayout", args=[{"updatemenus[0].buttons[0].args": [None, dict(frame=dict(duration=target_duration/m, redraw=False), fromcurrent=True, mode="immediate")]}]) for m in [0.5, 1.0, 2.0, 5.0, 10.0]])
                ],
                sliders=[dict(active=idx, currentvalue={"prefix": "Date: ", "font": {"size": 14}}, pad={"t": 80, "b": 10}, x=0, y=-0.3,
                    steps=[dict(method="animate", args=[[d], dict(mode="immediate", frame=dict(duration=0, redraw=False))], label=f"{d[:4]}-{d[4:6]}-{d[6:8]}") for d in dates]
                )]
            )
        else:
            fig.update_layout(title_text=f"Curve: {curve_id}")
            st.info(f"💡 '지연 렌더링' 모드 (날짜: {current_date})")

        fig.update_layout(
            xaxis=dict(
                title="Tenor", 
                tickmode='array', 
                tickvals=unique_tenors['plot_x'], 
                ticktext=unique_tenors['TENOR_NAME'], 
                gridcolor='lightgrey'
            ), 
            yaxis=dict(title="MID Value (%)", range=[y_min, y_max], gridcolor='lightgrey'), 
            height=700, 
            margin=dict(l=50, r=50, t=80, b=(180 if st.session_state.is_cached else 80)), 
            template="plotly_white", 
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch', key=f"main_chart_{curve_id}_{st.session_state.is_cached}")

        sc1, sc2 = st.columns([8, 2])
        with sc1:
            if not st.session_state.is_cached:
                c = st.session_state.last_config
                # 날짜 기반으로 값을 동기화하여 '번갈아 나타나는 현상' 방지
                selected_val = st.select_slider(
                    "View Curve", 
                    options=dates, 
                    value=st.session_state.selected_date, 
                    format_func=lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}", 
                    key=f"slider_{c[0]}_{c[1]}_{c[2]}"
                )
                if selected_val != st.session_state.selected_date:
                    st.session_state.selected_date = selected_val
                    # st.rerun() # fragment 내부에서는 위젯 변경 시 자동 리렌더링되므로 제거
        with sc2:
            if st.session_state.is_cached:
                st.text_input("Go to Date", value="", placeholder="Disable in Cache Mode", key="goto_date_input_disabled", disabled=True)
            else:
                st.text_input("Go to Date", value=st.session_state.selected_date, key="goto_date_input", on_change=sync_from_input)
            if st.session_state.date_info_msg: st.caption(st.session_state.date_info_msg)
        
        st.markdown(f"<style>div[data-testid='stVerticalBlock']:has(> div #scroll-trigger-{rid_global}) {{ min-height: 850px; }}</style>", unsafe_allow_html=True)

st.write("---")
render_chart_and_controls(full_df)

with st.expander("View Data Summary"):
    st.dataframe(full_df.groupby('TDATE')['MID'].agg(['mean', 'min', 'max']).tail(10))
