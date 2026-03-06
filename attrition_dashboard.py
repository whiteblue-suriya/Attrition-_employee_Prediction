import dash
from dash import dcc, html, Input, Output, callback, dash_table, dependencies
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pickle
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseConnection

# Apply custom CSS for better design
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Custom CSS for background and styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Employee Attrition Prediction</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .container-fluid {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 20px;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                color: white;
            }
            .card-header {
                background: rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                color: white;
                font-weight: 600;
                border-radius: 15px 15px 0 0 !important;
            }
            .card-body {
                background: transparent;
            }
            .form-label {
                color: white !important;
                font-weight: 500;
            }
            .form-control, .Select-control {
                background: rgba(255, 255, 255, 0.1) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border-radius: 10px;
            }
            .form-control:focus, .Select-control:focus {
                background: rgba(255, 255, 255, 0.15) !important;
                border-color: #00d4ff !important;
                box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
            }
            .Select-placeholder, .Select-value-label {
                color: white !important;
            }
            .Select-arrow {
                border-color: white !important;
            }
            h1 {
                color: white !important;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                font-weight: 700;
            }
            h3, h4 {
                color: white !important;
            }
            .btn-primary {
                background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
                border: none;
                border-radius: 10px;
                font-weight: 600;
                padding: 12px 30px;
                box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
            }
            .btn-primary:hover {
                background: linear-gradient(135deg, #00a3cc 0%, #007799 100%);
                box-shadow: 0 6px 20px rgba(0, 212, 255, 0.6);
                transform: translateY(-2px);
            }
            .alert-info {
                background: rgba(0, 212, 255, 0.2);
                border: 1px solid rgba(0, 212, 255, 0.3);
                color: white;
            }
            .slider-mark {
                color: white !important;
            }
            .rc-slider-label {
                color: white !important;
            }
            .table {
                color: white !important;
            }
            .table thead th {
                background: rgba(255, 255, 255, 0.1) !important;
                color: white !important;
                border-bottom: 2px solid rgba(0, 212, 255, 0.5) !important;
            }
            .table td {
                background: rgba(255, 255, 255, 0.05) !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
            }
            .js-irs-0 .irs--round .irs-bar {
                background: #00d4ff;
            }
            .irs--round .irs-handle {
                border-color: #00d4ff;
            }
            .css-1nm2diw-Dropdown {
                background: rgba(255, 255, 255, 0.1) !important;
            }
            .dropdown-menu {
                background: rgba(26, 26, 46, 0.95) !important;
            }
            .dropdown-item {
                color: white !important;
            }
            .dropdown-item:hover {
                background: rgba(0, 212, 255, 0.2) !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

db = DatabaseConnection()


class AttritionPredictor:
    def __init__(self):
        self.loaded = False
        self.load_model()
    
    def load_model(self):
        try:
            with open('models/attrition_model.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_columns = model_data['feature_columns']
            self.categorical_columns = model_data['categorical_columns']
            self.model_name = model_data['model_name']
            
            self.loaded = True
            print(f"Model loaded successfully: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.loaded = False
    
    def predict(self, employee_data):
        if not self.loaded:
            return None
        
        features = pd.DataFrame([employee_data])
        
        for col in self.categorical_columns:
            if col in features.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                try:
                    features[col + '_encoded'] = le.transform(features[col].astype(str))
                except:
                    features[col + '_encoded'] = 0
        
        feature_cols = self.feature_columns.copy()
        for col in self.categorical_columns:
            feature_cols.append(col + '_encoded')
        
        X = features[feature_cols].fillna(0)
        
        try:
            probability = self.model.predict_proba(X)[0][1]
        except:
            probability = 0.5
        
        prediction = 'Yes' if probability >= 0.5 else 'No'
        
        if probability >= 0.7:
            risk_level = 'Critical'
            risk_color = '#ff4757'
        elif probability >= 0.5:
            risk_level = 'High'
            risk_color = '#ffa502'
        elif probability >= 0.3:
            risk_level = 'Medium'
            risk_color = '#7bed9f'
        else:
            risk_level = 'Low'
            risk_color = '#2ed573'
        
        return {
            'prediction': prediction,
            'probability': probability,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'confidence': abs(probability - 0.5) * 2 * 100
        }


predictor = AttritionPredictor()


def create_empty_gauge():
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 0,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Attrition Risk %", 'font': {'size': 20, 'color': 'white'}},
        number = {'font': {'size': 30, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': 'white', 'tickfont': {'color': 'white'}},
            'bar': {'color': 'gray'},
            'bgcolor': 'rgba(255,255,255,0.1)',
            'borderwidth': 2,
            'bordercolor': 'rgba(255,255,255,0.2)',
            'steps': [
                {'range': [0, 30], 'color': "#2ed573"},
                {'range': [30, 50], 'color': "#ffa502"},
                {'range': [50, 70], 'color': "#ff6348"},
                {'range': [70, 100], 'color': "#ff4757"}
            ]
        }
    ))
    fig.update_layout(
        height=350, 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=80, b=20)
    )
    return fig


def create_empty_bar():
    fig = go.Figure()
    fig.update_layout(
        title={'text': "Employee Metrics", 'font': {'size': 20, 'color': 'white'}},
        xaxis_title="Score",
        yaxis_title="Metric",
        xaxis={'tickcolor': 'white', 'titlefont': {'color': 'white'}, 'gridcolor': 'rgba(255,255,255,0.1)'},
        yaxis={'tickcolor': 'white', 'titlefont': {'color': 'white'}, 'gridcolor': 'rgba(255,255,255,0.1)'},
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=80, b=20)
    )
    return fig


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Employee Attrition Prediction", className="text-center mb-4"),
                html.P("Predict and prevent employee turnover with AI", className="text-center", style={'color': 'rgba(255,255,255,0.7)'})
            ])
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Employee Information", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Employee ID"),
                            dbc.Input(id="employee_id", type="text", placeholder="e.g., EMP001", 
                                    style={'textTransform': 'uppercase'})
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Employee Name"),
                            dbc.Input(id="employee_name", type="text", placeholder="e.g., John Sharma")
                        ], width=8),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Age"),
                            dbc.Input(id="age", type="number", value=30, min=18, max=65, placeholder="Enter age")
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Monthly Income (INR)"),
                            dbc.Input(id="monthly_income", type="number", value=4000000, min=100000, 
                                    placeholder="Enter monthly salary in INR"),
                            html.Small("e.g., 400000 = 4 Lakhs", style={'color': 'rgba(255,255,255,0.5)'})
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Gender"),
                            dcc.Dropdown(id="gender", options=[
                                {'label': 'Male', 'value': 'Male'},
                                {'label': 'Female', 'value': 'Female'}
                            ], value='Male', clearable=False, style={'color': 'black'})
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Marital Status"),
                            dcc.Dropdown(id="marital_status", options=[
                                {'label': 'Single', 'value': 'Single'},
                                {'label': 'Married', 'value': 'Married'},
                                {'label': 'Divorced', 'value': 'Divorced'}
                            ], value='Single', clearable=False, style={'color': 'black'})
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Education Level"),
                            dcc.Dropdown(id="education_level", options=[
                                {'label': 'High School', 'value': 'High School'},
                                {'label': 'Bachelor', 'value': 'Bachelor'},
                                {'label': 'Master', 'value': 'Master'},
                                {'label': 'PhD', 'value': 'PhD'}
                            ], value='Bachelor', clearable=False, style={'color': 'black'})
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Department"),
                            dcc.Dropdown(id="department", options=[
                                {'label': 'Engineering', 'value': 'Engineering'},
                                {'label': 'Sales', 'value': 'Sales'},
                                {'label': 'Marketing', 'value': 'Marketing'},
                                {'label': 'HR', 'value': 'HR'}
                            ], value='Engineering', clearable=False, style={'color': 'black'})
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Job Role"),
                            dbc.Input(id="job_role", type="text", value="Developer", placeholder="e.g., Developer, Manager")
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Years at Company"),
                            dbc.Input(id="years_at_company", type="number", value=3, min=0, placeholder="Years")
                        ], width=6),
                    ]),
                ])
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Job & Performance Metrics", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Job Satisfaction (1-5)"),
                            dcc.Slider(id="job_satisfaction", min=1, max=5, step=1, 
                                      marks={1: '1 (Low)', 2: '2', 3: '3', 4: '4', 5: '5 (High)'},
                                      value=3,
                                      tooltip={"placement": "bottom", "always_visible": True})
                        ], width=12),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Work-Life Balance (1-5)"),
                            dcc.Slider(id="work_life_balance", min=1, max=5, step=1,
                                      marks={1: '1 (Poor)', 2: '2', 3: '3', 4: '4', 5: '5 (Excellent)'},
                                      value=3,
                                      tooltip={"placement": "bottom", "always_visible": True})
                        ], width=12),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Environment Satisfaction (1-5)"),
                            dcc.Slider(id="environment_satisfaction", min=1, max=5, step=1,
                                      marks={1: '1 (Low)', 2: '2', 3: '3', 4: '4', 5: '5 (High)'},
                                      value=3,
                                      tooltip={"placement": "bottom", "always_visible": True})
                        ], width=12),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Performance Rating (1-5)"),
                            dcc.Slider(id="performance_rating", min=1, max=5, step=1,
                                      marks={1: '1 (Low)', 2: '2', 3: '3', 4: '4', 5: '5 (High)'},
                                      value=3,
                                      tooltip={"placement": "bottom", "always_visible": True})
                        ], width=12),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Overtime"),
                            dcc.Dropdown(id="overtime", options=[
                                {'label': 'Yes', 'value': 'Yes'},
                                {'label': 'No', 'value': 'No'}
                            ], value='No', clearable=False, style={'color': 'black'})
                        ], width=6),
                        dbc.Col([
                            dbc.Label("Business Travel"),
                            dcc.Dropdown(id="business_travel", options=[
                                {'label': 'Non-Travel', 'value': 'Non-Travel'},
                                {'label': 'Rarely', 'value': 'Rarely'},
                                {'label': 'Frequently', 'value': 'Frequently'}
                            ], value='Rarely', clearable=False, style={'color': 'black'})
                        ], width=6),
                    ]),
                ])
            ])
        ], width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-chart-line me-2"),
                "Predict Attrition Risk"
            ], id="predict-btn", color="primary", size="lg", className="w-100")
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Prediction Result"),
                dbc.CardBody([
                    html.Div(id="prediction-output")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="risk-gauge", figure=create_empty_gauge())
        ], width=6),
        dbc.Col([
            dcc.Graph(id="factor-analysis", figure=create_empty_bar())
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Prediction Result", className="mt-4 mb-3", style={'color': 'white'}),
            dash_table.DataTable(
                id='prediction-table',
                columns=[
                    {'name': 'Employee ID', 'id': 'employee_id'},
                    {'name': 'Employee Name', 'id': 'employee_name'},
                    {'name': 'Department', 'id': 'department'},
                    {'name': 'Job Role', 'id': 'job_role'},
                    {'name': 'Attrition Risk', 'id': 'attrition_prediction'},
                    {'name': 'Risk Probability', 'id': 'risk_probability'},
                    {'name': 'Risk Level', 'id': 'risk_level'}
                ],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px', 'color': 'white'},
                style_header={'backgroundColor': 'rgba(255,255,255,0.1)', 'fontWeight': 'bold', 'color': 'white'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{risk_level} = "Critical"'},
                        'backgroundColor': 'rgba(255, 71, 87, 0.5)',
                        'color': 'white',
                    },
                    {
                        'if': {'filter_query': '{risk_level} = "High"'},
                        'backgroundColor': 'rgba(255, 165, 2, 0.5)',
                        'color': 'white',
                    },
                    {
                        'if': {'filter_query': '{risk_level} = "Medium"'},
                        'backgroundColor': 'rgba(123, 237, 159, 0.5)',
                        'color': 'white',
                    },
                    {
                        'if': {'filter_query': '{risk_level} = "Low"'},
                        'backgroundColor': 'rgba(46, 213, 115, 0.5)',
                        'color': 'white',
                    }
                ]
            )
        ], width=12)
    ])
], fluid=True)


@callback(
    [Output('prediction-output', 'children'),
     Output('risk-gauge', 'figure'),
     Output('factor-analysis', 'figure'),
     Output('prediction-table', 'data')],
    [Input('predict-btn', 'n_clicks')],
    [dependencies.State("employee_id", "value"),
     dependencies.State("employee_name", "value"),
     dependencies.State("age", "value"),
     dependencies.State("monthly_income", "value"),
     dependencies.State("gender", "value"),
     dependencies.State("marital_status", "value"),
     dependencies.State("education_level", "value"),
     dependencies.State("department", "value"),
     dependencies.State("job_role", "value"),
     dependencies.State("years_at_company", "value"),
     dependencies.State("job_satisfaction", "value"),
     dependencies.State("work_life_balance", "value"),
     dependencies.State("environment_satisfaction", "value"),
     dependencies.State("performance_rating", "value"),
     dependencies.State("overtime", "value"),
     dependencies.State("business_travel", "value")]
)
def predict_attrition(n_clicks, emp_id, emp_name, age, income, gender, marital, education, 
                      department, job_role, years, job_sat, work_life, 
                      env_sat, perf_rating, overtime, travel):
    
    # Initialize empty table data
    table_data = []
    
    empty_gauge = create_empty_gauge()
    empty_bar = create_empty_bar()
    
    if n_clicks is None or not predictor.loaded:
        return html.Div([
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "Click 'Predict Attrition Risk' button to see results"
            ], color="info")
        ]), empty_gauge, empty_bar, table_data
    
    # Convert INR to USD for model (divide by 82)
    income_usd = income / 82 if income else 50000
    
    employee_data = {
        'age': age,
        'monthly_income': income_usd,
        'years_at_company': years,
        'years_in_role': min(years, 2),
        'job_satisfaction': job_sat,
        'work_life_balance': work_life,
        'environment_satisfaction': env_sat,
        'relationship_satisfaction': job_sat,
        'performance_rating': perf_rating,
        'distance_from_home': 15,
        'num_companies_worked': 2,
        'total_experience': years + 2,
        'training_times_last_year': 2,
        'gender': gender,
        'marital_status': marital,
        'education_level': education,
        'department': department,
        'job_role': job_role,
        'overtime': overtime,
        'business_travel': travel
    }
    
    result = predictor.predict(employee_data)
    
    if result is None:
        return html.Div([
            dbc.Alert("Model not loaded. Please train the model first.", color="danger")
        ]), empty_gauge, empty_bar, table_data
    
    # Format income in INR
    income_inr = income if income else 0
    formatted_income = f"₹{income_inr:,.0f}"
    
    # Display employee info
    emp_id_display = emp_id if emp_id else "N/A"
    emp_name_display = emp_name if emp_name else "Unknown"
    
    output = html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5(f"Employee ID: {emp_id_display}", style={'color': '#00d4ff', 'margin': 0}),
                    html.H4(emp_name_display, style={'color': 'white', 'margin': 0}),
                ], style={'textAlign': 'center', 'padding': '10px'})
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Prediction", className="card-title", style={'color': 'rgba(255,255,255,0.7)'}),
                        html.H2(result['prediction'], style={'color': result['risk_color'], 'margin': 0})
                    ])
                ], style={'background': 'rgba(255,255,255,0.1)', 'border': f'2px solid {result["risk_color"]}'})
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Risk Probability", className="card-title", style={'color': 'rgba(255,255,255,0.7)'}),
                        html.H2(f"{result['probability']*100:.1f}%", style={'color': 'white', 'margin': 0})
                    ])
                ], style={'background': 'rgba(255,255,255,0.1)'})
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Risk Level", className="card-title", style={'color': 'rgba(255,255,255,0.7)'}),
                        html.H2(result['risk_level'], style={'color': result['risk_color'], 'margin': 0})
                    ])
                ], style={'background': 'rgba(255,255,255,0.1)', 'border': f'2px solid {result["risk_color"]}'})
            ], width=4),
        ]),
        dbc.Row([
            dbc.Col([
                html.P([
                    f"Confidence: {result['confidence']:.1f}%  |  ",
                    f"Monthly Income: {formatted_income}"
                ], style={'color': 'rgba(255,255,255,0.6)', 'textAlign': 'center', 'marginTop': '15px'})
            ])
        ])
    ])
    
    # Create gauge chart
    gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = result['probability'] * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Attrition Risk %", 'font': {'size': 20, 'color': 'white'}},
        number = {'font': {'size': 35, 'color': result['risk_color']}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': 'white', 'tickfont': {'color': 'white'}},
            'bar': {'color': result['risk_color']},
            'bgcolor': 'rgba(255,255,255,0.1)',
            'borderwidth': 2,
            'bordercolor': 'rgba(255,255,255,0.2)',
            'steps': [
                {'range': [0, 30], 'color': "#2ed573"},
                {'range': [30, 50], 'color': "#ffa502"},
                {'range': [50, 70], 'color': "#ff6348"},
                {'range': [70, 100], 'color': "#ff4757"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.8,
                'value': result['probability'] * 100
            }
        }
    ))
    gauge.update_layout(
        height=350, 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    # Create bar chart
    factors = go.Figure(data=[
        go.Bar(
            y=['Job Satisfaction', 'Work-Life Balance', 'Environment', 'Performance'],
            x=[job_sat, work_life, env_sat, perf_rating],
            orientation='h',
            marker_color=[result['risk_color'], '#00d4ff', '#7bed9f', '#ffa502']
        )
    ])
    factors.update_layout(
        title={'text': "Employee Metrics", 'font': {'size': 20, 'color': 'white'}},
        xaxis_title="Score (1-5)",
        xaxis=dict(range=[0, 5], tickcolor='white', titlefont={'color': 'white'}, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(tickcolor='white', titlefont={'color': 'white'}, gridcolor='rgba(255,255,255,0.1)'),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    # Create prediction result table data
    table_data = [{
        'employee_id': emp_id if emp_id else 'N/A',
        'employee_name': emp_name if emp_name else 'Unknown',
        'department': department if department else 'N/A',
        'job_role': job_role if job_role else 'N/A',
        'attrition_prediction': result['prediction'],
        'risk_probability': f"{result['probability']*100:.1f}%",
        'risk_level': result['risk_level']
    }]
    
    return output, gauge, factors, table_data


if __name__ == '__main__':
    print("="*50)
    print("DASHBOARD RUNNING!")
    print("Open your browser and go to: http://localhost:8051")
    print("="*50)
    app.run_server(debug=False, host='127.0.0.1', port=8051)