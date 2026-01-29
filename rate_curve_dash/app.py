import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.graph_objects as go

# Add project root to sys.path to import basic_library
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from basic_library.oracle_db import get_available_curves, get_all_curve_data
from basic_library.tenor_conventions import tenor_name_to_year_fraction

# Initialize Dash app
app = dash.Dash(__name__, title="Rate Curve Viewer")

# Available curve IDs (initial load)
available_curves = get_available_curves()

app.layout = html.Div([
    html.H1("Rate Curve Dash Viewer", style={'textAlign': 'center'}),
    
    # Input Section
    html.Div([
        html.Div([
            html.Label("Curve ID:"),
            dcc.Dropdown(
                id='curve-id-dropdown',
                options=[{'label': c, 'value': c} for c in available_curves],
                value='KRWQ3L' if 'KRWQ3L' in available_curves else (available_curves[0] if available_curves else None),
                placeholder="Select or type curve ID (e.g. KRWQ3L)",
                searchable=True,
                style={'width': '300px'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '20px', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label("Date Range:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                display_format='YYYYMMDD'
            ),
        ], style={'display': 'inline-block', 'marginRight': '20px', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Button('Data Load', id='load-button', n_clicks=0, 
                        style={'marginTop': '25px', 'padding': '5px 20px', 'fontSize': '16px', 'cursor': 'pointer'})
        ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'marginBottom': '20px'}),
    
    # Chart Section
    html.Div([
        dcc.Loading(
            id="loading-chart",
            type="circle",
            children=[
                dcc.Graph(id='curve-chart', style={'height': '600px'})
            ]
        )
    ], style={'marginBottom': '20px'}),
    
    # Control Section (Slider & Playback)
    html.Div([
        html.Div([
            html.Label(id='slider-date-label', style={'fontWeight': 'bold', 'fontSize': '18px', 'marginBottom': '10px', 'display': 'block', 'textAlign': 'center'}),
            dcc.Slider(
                id='date-slider',
                min=0,
                max=0,
                step=1,
                value=0,
                marks={},
                tooltip={"always_visible": True, "placement": "top"}
            ),
        ], style={'width': '100%', 'padding': '0 40px'}),
        
        html.Div([
            html.Button('Play', id='play-button', n_clicks=0, style={'marginRight': '10px'}),
            html.Button('Pause', id='pause-button', n_clicks=0, style={'marginRight': '20px'}),
            html.Label("Speed: ", style={'marginRight': '10px'}),
            dcc.Dropdown(
                id='speed-dropdown',
                options=[
                    {'label': '0.5x', 'value': 0.5},
                    {'label': '1x', 'value': 1.0},
                    {'label': '2x', 'value': 2.0},
                    {'label': '5x', 'value': 5.0},
                    {'label': '10x', 'value': 10.0},
                ],
                value=1.0,
                clearable=False,
                style={'width': '100px', 'display': 'inline-block', 'verticalAlign': 'middle'}
            ),
        ], style={'textAlign': 'center', 'marginTop': '20px'}),
    ], style={'padding': '20px', 'borderTop': '1px solid #ddd'}),
    
    # State storage
    dcc.Store(id='curve-data-store'),  # Stores the loaded dataframe as JSON
    dcc.Store(id='available-dates-store'), # Stores list of dates available in loaded data
    dcc.Store(id='animation-state-store'), # Stores fractional index for smooth playback
    dcc.Interval(id='animation-interval', interval=1000/60, disabled=True), # 60 FPS target
])

# --- Callbacks ---

@callback(
    Output('curve-data-store', 'data'),
    Output('available-dates-store', 'data'),
    Input('load-button', 'n_clicks'),
    State('curve-id-dropdown', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    prevent_initial_call=True
)
def load_data(n_clicks, curve_id, start_date, end_date):
    if not curve_id or not start_date or not end_date:
        return dash.no_update, dash.no_update
    
    # Format dates for Oracle (YYYYMMDD)
    start_dt = start_date.replace('-', '')
    end_dt = end_date.replace('-', '')
    
    df = get_all_curve_data(curve_id, start_dt, end_dt)
    print(f"Loaded {len(df)} rows for {curve_id} from {start_dt} to {end_dt}")
    
    if df.empty:
        print("Dataframe is empty!")
        return None, []
    
    # Convert TDATE to string for serialization
    df['TDATE'] = df['TDATE'].astype(str)
    
    # Calculate Year Fraction for each tenor
    df['YEAR_FRACTION'] = df['TENOR_NAME'].apply(tenor_name_to_year_fraction)
    
    # Sort by TDATE and YEAR_FRACTION
    df = df.sort_values(['TDATE', 'YEAR_FRACTION'])
    
    available_dates = sorted(df['TDATE'].unique().tolist())
    
    return df.to_dict('records'), available_dates

@callback(
    Output('date-slider', 'max'),
    Output('date-slider', 'value'),
    Output('date-slider', 'marks'),
    Input('available-dates-store', 'data')
)
def update_slider_range(available_dates):
    if not available_dates:
        return 0, 0, {}
    
    max_idx = len(available_dates) - 1
    marks = {0: available_dates[0], max_idx: available_dates[-1]} if max_idx > 0 else {0: available_dates[0]}
    
    # Initially set to end date
    return max_idx, max_idx, marks

@callback(
    Output('curve-chart', 'figure'),
    Output('slider-date-label', 'children'),
    Input('date-slider', 'value'),
    Input('available-dates-store', 'data'),
    State('curve-data-store', 'data'),
    State('curve-id-dropdown', 'value')
)
def update_chart(slider_idx, available_dates, stored_data, curve_id):
    if not available_dates or not stored_data or not curve_id:
        return go.Figure(), "No data loaded"
    
    # Ensure slider_idx is within bounds of the CURRENT available_dates
    if slider_idx is None:
        slider_idx = len(available_dates) - 1
    elif slider_idx >= len(available_dates):
        slider_idx = len(available_dates) - 1
        
    selected_date = available_dates[int(slider_idx)]
    df = pd.DataFrame(stored_data)
    
    # Verify the stored data matches the curve_id to prevent bugs 5 & 6
    if not df.empty and df['CURVE_ID'].iloc[0] != curve_id:
        return go.Figure(), "Data mismatch, please reload"
    
    # Filter for the selected date
    day_df = df[df['TDATE'] == selected_date].copy()
    
    if day_df.empty:
        return go.Figure(), f"No data for {selected_date}"
    
    # Create the figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=day_df['YEAR_FRACTION'],
        y=day_df['MID'],
        mode='lines+markers',
        name=f"{curve_id} ({selected_date})",
        text=day_df['TENOR_NAME'],
        hovertemplate="Tenor: %{text}<br>Year Fraction: %{x:.4f}<br>Rate: %{y:.4f}%<extra></extra>"
    ))
    
    # Y-axis range: 0.5% buffer as requested
    # If rates are decimal (e.g. 0.03 for 3%), 0.5% buffer means 0.005
    # If rates are percentage (e.g. 3.0 for 3%), 0.5% buffer means 0.5
    # We detect this by checking the max value.
    is_decimal = df['MID'].max() < 1.0
    buffer = 0.005 if is_decimal else 0.5
    
    y_min = df['MID'].min() - buffer
    y_max = df['MID'].max() + buffer
    
    fig.update_layout(
        title=f"{curve_id} Interest Rate Curve - {selected_date}",
        xaxis_title="Tenor (Year Fraction)",
        yaxis_title="Rate (MID, %)",
        yaxis=dict(range=[y_min, y_max]),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )
    
    # Update X-axis labels to use tenor names
    # Note: This is a bit tricky in Plotly if we want custom spacing. 
    # We use tickvals and ticktext.
    tick_df = day_df.drop_duplicates('TENOR_NAME').sort_values('YEAR_FRACTION')
    fig.update_xaxes(
        tickvals=tick_df['YEAR_FRACTION'],
        ticktext=tick_df['TENOR_NAME']
    )
    
    return fig, f"Date: {selected_date}"

@callback(
    Output('animation-interval', 'disabled'),
    Input('play-button', 'n_clicks'),
    Input('pause-button', 'n_clicks'),
    prevent_initial_call=True
)
def control_playback(play_clicks, pause_clicks):
    triggered_id = ctx.triggered_id
    if triggered_id == 'play-button':
        return False
    else:
        return True

@callback(
    Output('date-slider', 'value', allow_duplicate=True),
    Output('animation-state-store', 'data'),
    Input('animation-interval', 'n_intervals'),
    State('date-slider', 'value'),
    State('date-slider', 'max'),
    State('speed-dropdown', 'value'),
    State('animation-state-store', 'data'),
    prevent_initial_call=True
)
def animate_slider(n_intervals, current_idx, max_idx, speed, state):
    if max_idx <= 0:
        return 0, dash.no_update
        
    if state is None or 'frac_idx' not in state:
        frac_idx = float(current_idx)
    else:
        frac_idx = state['frac_idx']
    
    # Target: 5 seconds for full period at 1x speed.
    # Total frames = 5 seconds * 60 FPS = 300 frames.
    # Increment per frame = max_idx / 300 * speed.
    increment = (max_idx / 300.0) * speed
    
    new_frac_idx = frac_idx + increment
    if new_frac_idx > max_idx:
        new_frac_idx = 0  # Loop back to start
    
    return int(new_frac_idx), {'frac_idx': new_frac_idx}

@callback(
    Output('animation-state-store', 'data', allow_duplicate=True),
    Input('date-slider', 'value'),
    State('animation-interval', 'disabled'),
    prevent_initial_call=True
)
def sync_state_on_manual_slider(slider_value, is_disabled):
    # Only sync if not animating to avoid feedback loops
    if is_disabled:
        return {'frac_idx': float(slider_value)}
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
