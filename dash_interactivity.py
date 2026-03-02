# Import required libraries
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the SpaceX dataset
spacex_df = pd.read_csv('spacex_launch_dash.csv')

# Calculate min and max payload for the range slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Get unique launch sites for dropdown options
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a Launch Site Drop-down Input Component
    html.Div([
        html.Label("Select Launch Site:"),
        dcc.Dropdown(id='site-dropdown',
                    options=dropdown_options,
                    value='ALL',
                    placeholder="Select a Launch Site here",
                    searchable=True
                    ),
    ]),
    
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a Range Slider to Select Payload
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={
                        0: '0 kg',
                        2500: '2500 kg',
                        5000: '5000 kg',
                        7500: '7500 kg',
                        10000: '10000 kg'
                    },
                    value=[min_payload, max_payload]),
    
    html.Br(),
    
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add callback function for success-pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    
    if entered_site == 'ALL':
        # Show total success counts across all sites
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        
        # Map numeric class to descriptive names
        success_counts['outcome'] = success_counts['class'].map({0: 'Failure', 1: 'Success'})
        
        fig = px.pie(
            success_counts, 
            values='count', 
            names='outcome', 
            title='Total Success Launches for All Sites',
            color='outcome',
            color_discrete_map={'Failure': 'red', 'Success': 'green'}
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
        )
        
        return fig
    else:
        # Filter for selected site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        site_outcomes = site_df['class'].value_counts().reset_index()
        site_outcomes.columns = ['class', 'count']
        
        # Map numeric class to descriptive names
        site_outcomes['outcome'] = site_outcomes['class'].map({0: 'Failure', 1: 'Success'})
        
        fig = px.pie(
            site_outcomes, 
            values='count', 
            names='outcome', 
            title=f'Launch Outcomes for {entered_site}',
            color='outcome',
            color_discrete_map={'Failure': 'red', 'Success': 'green'}
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}'
        )
        
        return fig

# TASK 4: Add callback function for success-payload-scatter-chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload range
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask].copy()
    
    # Add descriptive outcome column for better visualization
    filtered_df['outcome'] = filtered_df['class'].map({0: 'Failure', 1: 'Success'})
    
    if entered_site == 'ALL':
        # Show all sites
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            symbol='outcome',  # Different symbols for success/failure
            title='Payload Mass vs. Launch Outcome for All Sites',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
            hover_data=['Launch Site', 'Booster Version Category']
        )
        
        # Update y-axis labels
        fig.update_yaxes(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        )
        
        return fig
    else:
        # Filter for specific site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        fig = px.scatter(
            site_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            symbol='outcome',  # Different symbols for success/failure
            title=f'Payload Mass vs. Launch Outcome for {entered_site}',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
            hover_data=['Booster Version Category']
        )
        
        # Update y-axis labels
        fig.update_yaxes(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['Failure', 'Success']
        )
        
        return fig

# Run the app - UPDATED: use run() instead of run_server()
if __name__ == '__main__':
    app.run(debug=True, port=8050)