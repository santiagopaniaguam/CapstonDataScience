# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                # 
                                  dcc.Dropdown(id='site-dropdown',
    options=[
        {'label': 'All Sites', 'value': 'ALL'},
        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
    ],
    value='ALL',
    placeholder="Select a Launch Site",
    searchable=True
                                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        100: '100'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Count successful and failed launches across all sites
        success_count = spacex_df['class'].sum()
        failure_count = len(spacex_df) - success_count
        
        labels = ['Successful Launches', 'Failed Launches']
        values = [success_count, failure_count]
    else:
        # Filter data for the selected site and count successful and failed launches
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df['class'].sum()
        failure_count = len(filtered_df) - success_count
        
        labels = ['Successful Launches', 'Failed Launches']
        values = [success_count, failure_count]

    pie_chart_figure = {
        'data': [
            dict(
                labels=labels,
                values=values,
                type='pie',
                hole=.3,
            )
        ],
        'layout': dict(title=f'Launch Successes by {selected_site}')
    }
    
    return pie_chart_figure
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_plot(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if selected_site == 'ALL':
        scatter_data = filtered_df
    else:
        scatter_data = filtered_df[filtered_df['Launch Site'] == selected_site]
        
    unique_categories = scatter_data['Booster Version Category'].unique()
    colorscale_dict = {category: go.colors.DEFAULT_PLOTLY_COLORS[i % len(go.colors.DEFAULT_PLOTLY_COLORS)]
                       for i, category in enumerate(unique_categories)}

    scatter_chart_figure = go.Figure(data=[
        dict(
            x=scatter_data['Payload Mass (kg)'],
            y=scatter_data['class'],
            mode='markers',
            marker=dict(
                color=[colorscale_dict[category] for category in scatter_data['Booster Version Category']],
                size=10,
                opacity=0.7
            ),
            text=scatter_data['Booster Version Category'],
            hoverinfo='text',  # Show Booster Version on hover
            name=''
        )
    ])
    
    scatter_chart_figure.update_layout(
        title=f'Success Payload Scatter Plot for {selected_site}',
        xaxis={'title': 'Payload Mass (kg)'},
        yaxis={'title': 'Success'}
    )       
    
    return scatter_chart_figure


# Run the app
if __name__ == '__main__':
    app.run()
