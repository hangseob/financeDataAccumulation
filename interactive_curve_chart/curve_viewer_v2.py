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
    st.stop()

# 페이지 설정
st.set_page_config(page_title="Curve Viewer V2", layout="wide")

# --- 전역 CSS (스크롤 및 레이아웃 안정화) ---
st.markdown("""
<style>
    /* 스크롤 튀는 현상 방지 */
    html { scroll-behavior: auto !important; }
    section.main { scroll-behavior: auto !important; overflow-anchor: none !important; }
    .stApp { overflow-anchor: none !important; }
    /* 위젯 간격 최적화 */
    .stNumberInput, .stCheckbox, .stButton { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

# --- [로그 시스템] ---
def log_v2(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"[V2][{timestamp}] {message}"
    print(log_msg)
    try:
        with open("debug_log_v2.txt", "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass

# --- 초정밀 스크롤 보존 ---
def preserve_scroll_v2(rid):
    components.html(
        f"""
        <script>
        (function() {{
            const parentWin = window.parent;
            const parentDoc = parentWin.document;
            const getEl = () => parentDoc.querySelector('section[data-testid="stMain"]') || parentDoc.querySelector('section.main');
            const saved = parentWin.sessionStorage.getItem('v2_scroll_pos');
            if (saved) {{
                const pos = parseInt(saved);
                const el = getEl();
                if (el) {{
                    el.scrollTo(0, pos);
                    for(let i=0; i<10; i++) {{ setTimeout(() => el.scrollTo(0, pos), i * 50); }}
                }}
            }}
            const el = getEl();
            if (el && !el.dataset.v2Attached) {{
                el.addEventListener('scroll', () => {{ parentWin.sessionStorage.setItem('v2_scroll_pos', el.scrollTop); }}, {{ passive: true }});
                el.dataset.v2Attached = 'true';
            }}
        }})();
        </script>
        <div style="display:none" id="v2-trigger-{rid}"></div>
        """,
        height=0,
    )

# --- 캐싱 ---
@st.cache_data(ttl=3600)
def cached_curves(): return get_available_curves()

@st.cache_data(ttl=3600)
def cached_dates(curve_id): return get_available_dates(curve_id)

@st.cache_data(ttl=3600)
def cached_data(curve_id, start, end):
    df = get_all_curve_data(curve_id, start, end)
    if not df.empty:
        df['MID'] = pd.to_numeric(df['MID'], errors='coerce').fillna(0.0) * 100.0
        df['year_fraction'] = df['TENOR_NAME'].apply(tenor_name_to_year_fraction)
        df = df.sort_values(['TDATE', 'year_fraction']).reset_index(drop=True)
        df = df[(df['TDATE'] >= start) & (df['TDATE'] <= end)]
    return df

@st.cache_resource
def get_frames_v3(curve_id, start_str, end_str, collapse_active, threshold):
    """데이터프레임 대신 ID와 설정값을 키로 사용하여 캐시 안정성 확보"""
    df = cached_data(curve_id, start_str, end_str)
    if df.empty: return []
    
    p_df = df.copy()
    if collapse_active:
        u_f = sorted(p_df['year_fraction'].unique())
        x_map = {f: (f if f <= threshold else threshold + i + 1) for i, f in enumerate([f for f in u_f if f > threshold])}
        x_map.update({f: f for f in u_f if f <= threshold})
        p_df['plot_x'] = p_df['year_fraction'].map(x_map)
    else:
        p_df['plot_x'] = p_df['year_fraction']
        
    dates = sorted(p_df['TDATE'].unique().tolist())
    grouped = p_df.groupby('TDATE')
    frames = []
    for d in dates:
        if d in grouped.groups:
            day_data = grouped.get_group(d)
            frames.append(go.Frame(
                data=[go.Scatter(x=day_data['plot_x'], y=day_data['MID'])],
                name=d,
                layout=go.Layout(title_text=f"Curve: {curve_id} ({d})")
            ))
    return frames

# --- 초기화 ---
if "v2_is_cached" not in st.session_state: st.session_state.v2_is_cached = False
if "v2_selected_date" not in st.session_state: st.session_state.v2_selected_date = None
if "v2_date_msg" not in st.session_state: st.session_state.v2_date_msg = ""
if "v2_last_curve_id" not in st.session_state: st.session_state.v2_last_curve_id = ""

# 2. 사이드바
st.sidebar.header("Data Selection")
available_curves = cached_curves()
if not available_curves: st.stop()
sel_curve = st.sidebar.selectbox("Curve ID", options=available_curves, key="v2_curve")

all_available_dates = cached_dates(sel_curve)
if not all_available_dates: st.stop()
d_min = datetime.strptime(all_available_dates[0], "%Y%m%d")
d_max = datetime.strptime(all_available_dates[-1], "%Y%m%d")

# 💡 커브 변경 시 세션 상태를 완전히 초기화하여 잔상 및 꼬임 방지
if st.session_state.v2_last_curve_id != sel_curve:
    st.session_state.v2_start = d_min
    st.session_state.v2_end = d_max
    st.session_state.v2_last_curve_id = sel_curve
    st.session_state.v2_selected_date = all_available_dates[0]
    st.session_state.v2_is_cached = False
    # 슬라이더 관련 키 모두 삭제
    for k in list(st.session_state.keys()):
        if k.startswith("v2_slider_"):
            del st.session_state[k]
    log_v2(f"!!! Curve Changed to {sel_curve} -> State Reset & Rerun !!!")
    st.rerun()

def sync_period():
    st.session_state.v2_start = st.session_state.v2_start_input
    st.session_state.v2_end = st.session_state.v2_end_input
    st.session_state.v2_is_cached = False
    log_v2(f"Period changed: {st.session_state.v2_start} ~ {st.session_state.v2_end}")

col1, col2 = st.sidebar.columns(2)
with col1: st.date_input("Start Date", value=st.session_state.v2_start, key="v2_start_input", on_change=sync_period)
with col2: st.date_input("End Date", value=st.session_state.v2_end, key="v2_end_input", on_change=sync_period)

s_str = st.session_state.v2_start.strftime("%Y%m%d")
e_str = st.session_state.v2_end.strftime("%Y%m%d")

# --- 헬퍼 ---
def sync_slider_v2(skey):
    st.session_state.v2_selected_date = st.session_state[skey]
    log_v2(f"Slider Sync: {st.session_state.v2_selected_date}")

def sync_goto_v2(gkey, skey, dates):
    val = st.session_state[gkey]
    raw = val.replace(".","").replace("-","").strip()
    if len(raw) == 8 and raw.isdigit():
        target = raw if raw in dates else ([d for d in dates if d > raw] or [dates[0]])[0]
        st.session_state.v2_selected_date = target
        st.session_state[skey] = target
        log_v2(f"GoTo Sync: {target}")

# --- 프래그먼트 ---
@st.fragment
def show_main_v2(curve_id, start_str, end_str, is_cached):
    # 💡 인자로 받은 curve_id와 세션 상태의 curve_id가 다르면 렌더링 중단 (레이스 컨디션 방지)
    if curve_id != st.session_state.v2_curve:
        return

    df = cached_data(curve_id, start_str, end_str)
    if df.empty: 
        st.warning("No data for selected period.")
        return
    
    rid = random.randint(0, 1000000)
    preserve_scroll_v2(rid)
    dates = sorted(df['TDATE'].unique().tolist())
    
    skey = f"v2_slider_{start_str}_{end_str}_{curve_id}"
    gkey = f"v2_goto_{curve_id}"
    
    if st.session_state.v2_selected_date not in dates:
        st.session_state.v2_selected_date = dates[0]
    
    if skey not in st.session_state:
        st.session_state[skey] = st.session_state.v2_selected_date
    
    curr_date = st.session_state.v2_selected_date
    log_v2(f"Fragment Run: {curve_id} | {curr_date} | Cached={is_cached}")

    # 상단 컨트롤바
    c1, c2, c3, c4 = st.columns([1, 1, 1.5, 1.5])
    with c1: collapse_active = st.checkbox("Tenor Collapse", key=f"v2_collapse_{curve_id}", value=False)
    with c2: thresh = st.number_input("Threshold", 1, 30, 5, key=f"v2_thresh_{curve_id}", label_visibility="collapsed")
    with c3: ymin_in = st.number_input("Y-Min (%)", value=None, format="%.2f", key=f"v2_ymin_{curve_id}", label_visibility="collapsed")
    with c4:
        if st.button("⚡ Cache for Anim", use_container_width=True, key=f"v2_cache_btn_{curve_id}"):
            st.session_state.v2_is_cached = True
            st.rerun()

    p_df = df.copy()
    if collapse_active:
        u_f = sorted(p_df['year_fraction'].unique())
        x_map = {f: (f if f <= thresh else thresh + i + 1) for i, f in enumerate([f for f in u_f if f > thresh])}
        x_map.update({f: f for f in u_f if f <= thresh})
        p_df['plot_x'] = p_df['year_fraction'].map(x_map)
    else:
        p_df['plot_x'] = p_df['year_fraction']
        
    df_curr = p_df[p_df['TDATE'] == curr_date]
    y_min = ymin_in if ymin_in is not None else (p_df['MID'].min() - 0.2)
    y_max = p_df['MID'].max() + 0.2

    fig = go.Figure()
    # 💡 데이터 포인트가 실제로 해당 커브인지 검증하기 위해 이름에 명시
    fig.add_trace(go.Scatter(
        x=df_curr['plot_x'], 
        y=df_curr['MID'], 
        mode='lines+markers', 
        name=f"Curve: {curve_id}", 
        line=dict(color='red', width=3)
    ))
    
    u_tenors = p_df[['plot_x', 'TENOR_NAME', 'year_fraction']].drop_duplicates().sort_values('year_fraction')

    if is_cached:
        # 💡 캐시 안정성이 높은 v3 함수 사용
        fig.frames = get_frames_v3(curve_id, start_str, end_str, collapse_active, thresh)
        fig.update_layout(
            updatemenus=[dict(type="buttons", buttons=[dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=50, redraw=False), fromcurrent=True)])])],
            sliders=[dict(active=dates.index(curr_date), steps=[dict(method="animate", args=[[d], dict(mode="immediate", frame=dict(duration=0, redraw=False))], label=d) for d in dates])]
        )
    else:
        fig.update_layout(title_text=f"ID: {curve_id} | Date: {curr_date}")

    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=u_tenors['plot_x'], ticktext=u_tenors['TENOR_NAME']), 
        yaxis=dict(range=[y_min, y_max]), 
        height=600, 
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # 💡 차트 키에 curve_id를 포함시켜 강제 리프레시 유도
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{curve_id}_{start_str}_{end_str}_{is_cached}")

    sc1, sc2 = st.columns([8, 2])
    with sc1:
        if not is_cached:
            st.select_slider("View Curve", options=dates, key=skey, on_change=sync_slider_v2, args=(skey,), format_func=lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]}")
    with sc2:
        if not is_cached:
            st.text_input("Go to Date", value=curr_date, key=gkey, on_change=sync_goto_v2, args=(gkey, skey, dates))
        if st.session_state.v2_date_msg: st.caption(st.session_state.v2_date_msg)

    st.markdown("<div style='min-height: 800px;'></div>", unsafe_allow_html=True)

st.write("---")
show_main_v2(sel_curve, s_str, e_str, st.session_state.v2_is_cached)
