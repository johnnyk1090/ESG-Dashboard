import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import plotly.express as px

# Load data
df = pd.read_csv('./global-data-on-sustainable-energy.csv')

# Define colors
colors = {
    'background': '#000000',  # Background color
    'text': '#FFFFFF',  # Text color
    'dropdown_bg': '#FF0000',  # Red background color for dropdowns
    'dropdown_text': '#000000'  # Black text color for dropdown options
}

app = Dash(__name__)

app.layout = html.Div(style={'backgroundColor': colors['background'], 'height': '100vh', 'width': '100vw'}, children=[
    
    html.Div([
        html.H1("Access to electricity per country and year", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        
        html.Div([
            dcc.Dropdown(
                id='year-dropdown-bar',
                options=[
                    {'label': str(year), 'value': year} for year in df['Year'].unique()
                ],
                value=df['Year'].min(),
                style={'color': colors['dropdown_text'], 'backgroundColor': colors['dropdown_bg'], 'width': '100%'}  # Ensure dropdown spans full width
            ),         
            
            dcc.Graph(id='barplot_fig_1', style={'width': '100%', 'height': '50vh', 'display': 'inline-block'}),
            dcc.Graph(id='barplot_fig_2', style={'width': '100%', 'height': '50vh', 'display': 'inline-block'})
        ], style={'textAlign': 'center', 'padding': '10px'}),
    ], style={'backgroundColor': colors['background']}),  # Ensure this div has black background
    
    html.Div([
        html.H1("Electricity resources per country and year", style={
            'textAlign': 'center',
            'color': colors['text'],
            'backgroundColor': colors['background']  # Setting black background explicitly
        }),
        
        dcc.Graph(id='electricity-resources', style={'width': '100%', 'height': '70vh'}),
        
        dcc.Slider(
            id='year-slider-scatter',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].max(),
            marks={str(year): str(year) for year in df['Year'].unique()},
            step=None
        )
    ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': colors['background']}),

    html.Div([
        dcc.Markdown("""
            ## Geo Plot of CO2 Emissions, GDP and Renewable Electricity Generating Capacity per capita
        """, style={
            'textAlign': 'center',
            'color': colors['text'],
            'backgroundColor': colors['background']  # Setting black background explicitly
        }),
        
        dcc.Dropdown(
            id='year-dropdown-geo',
            options=[
                {'label': str(year), 'value': year} for year in df['Year'].unique()
            ],
            value=df['Year'].min(),
            style={'color': colors['dropdown_text'], 'backgroundColor': colors['dropdown_bg'], 'width': '100%'}
        ),
        dcc.Graph(id='geo-plot', style={'width': '100%', 'height': '70vh'})
    ], style={'textAlign': 'center', 'paddingTop': '20px', 'backgroundColor': colors['background']})
])

@app.callback(
    [Output('barplot_fig_1', 'figure'),
     Output('barplot_fig_2', 'figure')],
    [Input('year-dropdown-bar', 'value')]
)
def update_figures(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    
    fig1 = px.bar(filtered_df, x='Entity', y='Access to electricity (% of population)', color='Entity')
    fig1.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    fig2 = px.bar(filtered_df, x='Entity', y='Access to clean fuels for cooking', color='Entity')
    fig2.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    return fig1, fig2

@app.callback(
    Output('electricity-resources', 'figure'),
    [Input('year-slider-scatter', 'value')]
)
def update_graph(year_value):
    dff = df[df['Year'] == year_value]

    fig = go.Figure()

    for entity in dff['Entity'].unique():
        entity_data = dff[dff['Entity'] == entity]
        fig.add_trace(go.Scatter3d(
            x=entity_data['Electricity from fossil fuels (TWh)'],
            y=entity_data['Electricity from renewables (TWh)'],
            z=[entity] * len(entity_data),  # Use Entity for z-axis text
            mode='markers',
            marker=dict(
                size=12,
                color=px.colors.qualitative.Alphabet[entity_data.index[0] % len(px.colors.qualitative.Alphabet)],  # Use a categorical color scheme
                opacity=0.8
            ),
            text=entity_data['Entity'],
            name=entity
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Electricity from fossil fuels (TWh)'),  # Provide axis titles
            yaxis=dict(title='Electricity from renewables (TWh)'),
            zaxis=dict(title='Entity')  # Use 'Entity' as the z-axis title
        ),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        height=700,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05,
            bgcolor=colors['background'],
            font=dict(color=colors['text'], size=10)  # Smaller font size for the legend
        ),
        margin=dict(l=0, r=0, b=0, t=0)  # Adjust margins to better fit the legend
    )

    return fig

@app.callback(
    Output('geo-plot', 'figure'),
    [Input('year-dropdown-geo', 'value')]
)
def update_figure(selected_year):
    filtered_df = df[df['Year'] == selected_year].copy()
    filtered_df['Value_co2_emissions_kt_by_country'].fillna(0, inplace=True)
    
    fig = px.scatter_geo(filtered_df,
                         lat='Latitude',
                         lon='Longitude',
                         hover_name='Entity',
                         size='Value_co2_emissions_kt_by_country',
                         color='gdp_per_capita',
                         projection='natural earth',
                         title=f'CO2 Emissions in {selected_year}')
    
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)