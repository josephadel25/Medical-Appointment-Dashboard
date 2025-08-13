from dash import dcc, html, Input, Output, State, Dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv('data/KaggleV2-May-2016.csv')
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
df['appointment_weekday'] = df['AppointmentDay'].dt.day_name()
df['delaydays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # Header
    html.Header([
        html.H1("Medical Appointment Dashboard", style={
            'margin': '20px',
            'textAlign': 'center',
            'background-color': '#000000',
            'color': '#0E46A3'
        })
    ]),
    # Show Filter Button
    dbc.Button(
        html.H5("Show Filter", style={
            'textAlign': 'left',
            'color': '#0E46A3',
            'padding': '10px'
        }),
        id="filter-toggle",
        color="dark",
        className="h-100 w-100",
        style={"backgroundColor": "#222222", "color": "#0E46A3", "border-raduis": "none"}
    ),
    # Body of Filter Button
    dbc.Collapse(
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    # Gender Dropdown Filter
                    dbc.Col([
                        html.Label("Gender", style={"color": "#0E46A3"}),
                        dcc.Dropdown(
                            options=[
                                {"label": "Male", "value": "M"},
                                {"label": "Female", "value": "F"},
                            ],
                            value=df['Gender'].unique().tolist(),
                            placeholder="Select Gender",
                            id="gender-filter",
                            style={
                                "backgroundColor": "#000000",
                                "color": "#0E46A3",
                                "border": "1px solid #0E46A3"
                            },
                        ),
                    ], md=4),
                    # Age Slider Filter
                    dbc.Col([
                        html.Label("Age Range", style={"color": "#0E46A3"}),
                        dcc.RangeSlider(
                            min=0,
                            max=100,
                            step=1,
                            value=[0, 100],
                            marks={0: '0', 20: '20', 40: '40', 60: '60', 80: '80', 100: '100'},
                            id="age-filter"
                        )
                    ], md=4),
                    # Neighborhood Dropdown Filter 
                    dbc.Col([
                        html.Label("Neighborhood", style={"color": "#0E46A3"}),
                        dcc.Dropdown(
                            options=[{"label": n, "value": n} for n in df['Neighbourhood'].unique()],
                            placeholder="Select Neighborhood",
                            id="neighborhood-filter",
                            value=df['Neighbourhood'].unique().tolist(),
                            style={
                                "backgroundColor": "#000000",
                                "color": "#0E46A3",
                                "border": "1px solid #0E46A3"
                            },
                        ),
                    ], md=4),
                ])
            ]),
            style={"backgroundColor": "#222222", "color": "#0E46A3", "border": "none"}
        ),
        id="filter-collapse",
        is_open=False
    ),

    # KPI Row
        dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Total Appointments", style={"color": "#0E46A3"}),
                    html.H2(id="total-appointments", style={"color": "#FFFFFF"})
                ]),
                style={"backgroundColor": "#222222"}
            ),
            md=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("No-shows", style={"color": "#0E46A3"}),
                    html.H2(id="total-noshow", style={"color": "#FFFFFF"})
                ]),
                style={"backgroundColor": "#222222"}
            ),
            md=4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Shows", style={"color": "#0E46A3"}),
                    html.H2(id="total-show", style={"color": "#FFFFFF"})
                ]),
                style={"backgroundColor": "#222222"}
            ),
            md=4
        ),
    ], style={"marginTop": "20px"}),


    # Graphs Row
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='noshow-show-plot', style={'margin-top': '10px', 'height': '400px'}),
            md=6
        ),
        dbc.Col(
            dcc.Graph(id='gender-graph', style={'margin-top': '10px', 'height': '400px'}),
            md=6
        ),
    ]),
    dbc.Row(dcc.Graph(id='neighbourhood-filter', style={'margin-top': '10px', 'height': '400px'})),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='weekday-filter', style={'margin-top': '10px', 'height': '400px'}),
            md=6
        ),
        dbc.Col(
            dcc.Graph(id='Chronic-filter', style={'margin-top': '10px', 'height': '400px'}),
            md=6
        )
    ]),
    dbc.Row(dcc.Graph(id='age-graph', style={'margin-top': '10px', 'height': '400px'})),
], fluid=True)


# Toggle collapse
@app.callback(
    Output("filter-collapse", "is_open"),
    Input("filter-toggle", "n_clicks"),
    State("filter-collapse", "is_open")
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open





# Update KPIs based on filters
@app.callback(
    Output("total-appointments", "children"),
    Output("total-noshow", "children"),
    Output("total-show", "children"),
    Input("gender-filter", "value"),
    Input("neighborhood-filter", "value"),
    Input("age-filter", "value")
)
def update_kpis(gender, neighborhood, age_range):
    filtered_df = df.copy()

    if gender is not None and gender != "":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood is not None and neighborhood != "":
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range is not None and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]

    total_appts = len(filtered_df)
    total_noshow = (filtered_df['No-show'] == "Yes").sum()
    total_show = (filtered_df['No-show'] == "No").sum()

    return f"{total_appts:,}", f"{total_noshow:,}", f"{total_show:,}"





# Update No-show vs Show-up Rates chart
@app.callback(
    Output('noshow-show-plot', 'figure'),
    Input('gender-filter', 'value'),
    Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def update_noshow_rates(gender, neighborhood, age_range):
    filtered_df = df.copy()

    if gender:
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood:
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Age'] >= age_range[0]) &
            (filtered_df['Age'] <= age_range[1])
        ]

    if not filtered_df.empty:
        show_counts = filtered_df['No-show'].value_counts().reset_index()
        show_counts.columns = ['No-show', 'Count']

        fig = px.bar(
            show_counts,
            x='No-show',
            y='Count',
            color='No-show',
            color_discrete_map={'No': '#9AC8CD', 'Yes': '#0E46A3'},
            title='No-show vs Show-up Rates'
        )
        fig.update_traces(textposition='outside')
    else:
        fig = px.bar(x=[], y=[], title='No-show vs Show-up Rates')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig




# Update Age box Plot
@app.callback(
    Output('gender-graph', 'figure'),
    Input('gender-filter', 'value'),
    Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def update_age_plot(gender, neighborhood, age_range):
    filtered_df = df.copy()

    if gender is not None and gender != "":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood is not None and neighborhood != "":
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range is not None and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
    else:
        filtered_df = filtered_df[(filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 100)]

    if not filtered_df.empty:
        fig = px.box(
            filtered_df,
            x='No-show',
            y='Age',
            color='No-show',
            color_discrete_map={'No': '#9AC8CD', 'Yes': '#0E46A3'},
            title='Age Distribution by No-show Status'
        )
    else:
        fig = go.Figure()
        fig.update_layout(title='No data available for selected filters')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig





# Update appointments by day of the week chart
@app.callback(
        Output('weekday-filter' , 'figure'),
        Input('gender-filter', 'value'),
        Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def distripution_dayweek(gender , neighborhood , age_range):
    filtered_df = df.copy()

    if gender is not None and gender != "":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood is not None and neighborhood != "":
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range is not None and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
    else:
        filtered_df = filtered_df[(filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 100)]
    
    if not filtered_df.empty:
        grouped = (filtered_df.groupby(['appointment_weekday']).size().reset_index(name='Count'))
        fig = px.bar(
            grouped,
            x='appointment_weekday',
            y='Count',
            category_orders={'appointment_weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']},
            title='appointments by day of the week',
            color='Count',
            color_continuous_scale=[
                (0, "#1E0342"),  
                (0.5, "#0E46A3"), 
                (1, "#9AC8CD")   
            ])
    else:
        fig = px.bar(x=[], y=[], title='appointments by day of the week')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig





# Update No-show by Neighborhood chart
@app.callback(
    Output('neighbourhood-filter' , 'figure'),
    Input('gender-filter', 'value'),
    Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def neighbourhood_noshow(gender , neighborhood , age_range):
    filtered_df = df.copy()
    
    if gender is not None and gender != "":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood is not None and neighborhood != "":
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range is not None and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
    else:
        filtered_df = filtered_df[(filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 100)]
    
    if not filtered_df.empty:
        grouped = filtered_df.groupby(['Neighbourhood', 'No-show']).size().reset_index(name='Count')
        grouped['Neighbourhood'] =grouped['Neighbourhood'].apply(lambda x : x.split()[0][:5]) 
        fig = px.bar(
            grouped,
            x='Neighbourhood',
            y='Count',
            color='No-show',
            barmode='group',
            color_discrete_map={
                "No": "#9AC8CD",
                "Yes": "#0E46A3"
            },
            title='No-show Count by Gender'
        )
    else:
        fig = px.bar(x=[], y=[], title='No-show Count by Gender')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig





# Update Chronic Conditions chart
@app.callback(
    Output('Chronic-filter', 'figure'),
    Input('gender-filter', 'value'),
    Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def chronic_noshow(gender, neighborhood, age_range):
    filtered_df = df.copy()

    if gender is not None and gender != "":
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood is not None and neighborhood != "":
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range is not None and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
    else:
        filtered_df = filtered_df[(filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 100)]

    if not filtered_df.empty:
        conditions = ['Hipertension', 'Diabetes', 'Alcoholism', 'Handcap']

        # Melt into long format
        df_long = filtered_df.melt(
            id_vars=['No-show'],
            value_vars=conditions,
            var_name='Condition',
            value_name='HasCondition'
        )
        df_conditions = (df_long[df_long['HasCondition'] == 1].groupby(['Condition', 'No-show']).size().reset_index(name='Count'))

        fig = px.bar(
            df_conditions,
            x='Condition',
            y='Count',
            color='No-show',
            barmode='group',
            color_discrete_map={
                "No": "#9AC8CD",
                "Yes": "#0E46A3"
            },
            title='Impact of Chronic Conditions on Attendance'
        )
    else:
        fig = px.bar(x=[], y=[], title='Impact of Chronic Conditions on Attendance')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig




# Update Age Impact on Attendance chart
@app.callback(
    Output('age-graph', 'figure'),
    Input('gender-filter', 'value'),
    Input('neighborhood-filter', 'value'),
    Input('age-filter', 'value')
)
def age_impact_on_attendance(gender, neighborhood, age_range):
    filtered_df = df.copy()

    if gender:
        filtered_df = filtered_df[filtered_df['Gender'] == gender]
    if neighborhood:
        filtered_df = filtered_df[filtered_df['Neighbourhood'] == neighborhood]
    if age_range and isinstance(age_range, (list, tuple)) and len(age_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['Age'] >= age_range[0]) &
            (filtered_df['Age'] <= age_range[1])
        ]

    if not filtered_df.empty:
        fig = px.histogram(
            filtered_df,
            x="Age",
            color="No-show",
            barmode="group",
            nbins=20,
            template="simple_white",
            color_discrete_map={
                "No": "#9AC8CD",
                "Yes": "#0E46A3"
            },
            title="Age Impact on Attendance",
            labels={
                "Age": "Patient Age (years)",
                "No-show": "Attendance Status",
                "count": "Number of Appointments"
            },
        )
        fig.update_layout(
            font_family="Rockwell",
            legend=dict(orientation="h", title="", y=1.1, x=1, xanchor="right", yanchor="bottom")
        )
    else:
        fig = px.histogram(x=[], title='No data for selected filters')

    fig.update_layout(
        paper_bgcolor='#222222',
        plot_bgcolor='#222222',
        font_color='#0E46A3'
    )

    return fig




if __name__ == "__main__":
    app.run(debug=True)

