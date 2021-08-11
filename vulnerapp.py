'''
    DASH BOARD CAUPIAN GALERIE
'''


# ---- Import packages
import os
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots


# --------------------------------------------------------------------------------------------------------
# ---- Preambule


# ---- Import data
df = pd.read_csv('la_results.csv', index_col=0)
hist_n_gal = pd.read_csv('n_galerie.csv', parse_dates = True, index_col = 0)
hist_q_gal = pd.read_csv('q_galerie.csv', parse_dates = True, index_col = 0)

# ---- Get date range
hist_min = min([*hist_n_gal.index, *hist_q_gal.index]).year
hist_max = max([*hist_n_gal.index, *hist_q_gal.index]).year

# ---- Fetch hydraulic conditions
hydraulic_conditions = tuple(df['h_cdt'].unique())
fancy_cdt = ['Conditions Basses Eaux', 'Conditions Médianes' ,'Conditions Hautes Eaux']

# ---- Set indicator names
ind = ['alpha', 'iota_ag', 'iota_fdc', 'iota_ga']
indicator_long_names = ['Rapport de mélange',
                        'Indice de mélange (Ariane Group)',
                        'Indice de mélange (Fief de Candale)',
                        'Indice de mélange (Garage Automobile)']
find = ['$\\alpha$', '$\\iota_{AG}$', '$\\iota_{FDC}$', '$\\iota_{GA}$']
fancy_ind = {k:v for k,v in zip(ind, find)}

# ---- Set web page spaces
sspace, mspace, bspace = [ [html.Br()]*n for n in [1,3,6]]


# --------------------------------------------------------------------------------------------------------
# ---- BUILD NAVIGUATION BAR


# ---- Get Github Source Code
link_github = dcc.Link("Code source", href="https://github.com/pmatran/vulnerapp",
             style = {"margin-top": '16px', "margin-left": "-2px",'color': '#503D36', 'font-style': 'italic','font-size': 18})
# ---- Get G&E Laboratory image
GE_img = html.A(html.Img(src="https://geoenv.ensegid.fr/wp-content/uploads/2017/03/Logo_Georessources__environnement-1.png",
                         height="95px"),
                         href="https://geoenv.ensegid.fr/", style = {"margin-top": '0px'})
title = html.H1('Galerie de Caupian', style={"margin-top": '36px', "margin-left": "400px", 'textAlign': 'center', 'color': '#503D36','font-size': 60})

# ---- Naviguation bar Layout
navbar = html.Div([GE_img, title], style = {'display' : 'flex', 'height' : '110px'})

source_code = html.Div(link_github, style = {'display' : 'flex'})
# --------------------------------------------------------------------------------------------------------
# ---- BUILD LAYOUT CONTENT


# ---- 1|  Historical plot elements

# -- Rolling window
hist_roll = html.Div(
             html.Div([html.Div(html.H5('Données historiques Galerie:',
                                style={'margin-right': '2em', 'font-size': 26, 'font-weight': 'bold', 'text-decoration': 'underline'})),
                       html.Div([html.Label('Fenêtre  (jours) ', style = {'font-size': 22, 'font-style': 'italic'}),
                                 dcc.Input(id = 'rolling-number', 
                                           type = 'number',
                                           value = 30,
                                           placeholder = 'N° jours',
                                           debounce = True,
                                           min = 1, max = 365, step = 1,
                                           minLength = 0, maxLength = 3,
                                           autoComplete='on',
                                           disabled=False,
                                           readOnly=False,
                                           required = False,
                                           style = {'font-size': '18px', 'font-style': 'italic'})],
                                        style = {'display':'block'})],
                       style = {'display':'flex'})
             )

# -- Historical plot
hist_graph = html.Div(
             html.Div([dcc.Graph(id = 'plt_historical', style = {'width': '95%', 'height': '60vh'})],
                      style={"margin-left": "50px"}))

# -- Slider
hist_slider = html.Div( html.Div(dcc.RangeSlider(id='range-slider',
                            marks={int(year) :{'label': str(year), 'style': {'color':'grey', 'font-size':'20px', 'font-weight':'bold'}}  for year in np.arange(hist_min,hist_max)},
                            step=1,                
                            min=hist_min,
                            max=hist_max,
                            value=[hist_min, hist_max],
                            dots=True,             
                            allowCross=False,
                            disabled=False,
                            pushable=1,
                            updatemode='drag',
                            included=True,
                            vertical=False,
                            className='slider',
                            tooltip={'always_visible':False, 'placement':'bottom'})
                                ), style = {'width' : '95%'}
                      )

# ---- 2| Indicators plots

# -- Dropdown
dropdown =  html.Div([
            html.Div(html.H5('Indicateur de vulnérabilité :',
                     style={'margin-right': '2em', 'font-size': 26, 'font-weight': 'bold', 'text-decoration': 'underline'})),
            html.Div(dcc.Dropdown(id='input-indicator',
                                  options = [{'label': k, 'value': v} for k,v in zip(indicator_long_names, ind)],
                                  placeholder="Selectionner un indicateur",
                                  clearable = True,
                                  style={'width':'80%', 'padding':'3px', 'font-size': '22px', 'text-align-last' : 'center'}),
                            style={'display':'flex'})])

# -- Empty plots areas
plots = html.Div([  html.Div([dcc.Graph(id='plt_dh', style={'width': '100vh', 'height': '72vh'}),
                              dcc.Graph(id='plt_lc', style={'width': '100vh', 'height': '72vh'}),
                              *sspace]),
                    html.Div([dcc.Graph(id='plt_mc', style={'width': '100vh', 'height': '72vh'}),
                              dcc.Graph(id='plt_hc', style={'width': '100vh', 'height': '72vh'})])],
                    style={'width' : '90%', 'height' : '80%', 'display' : 'flex'})



# --------------------------------------------------------------------------------------------------------
# ---- CRETAE DASH APPLICATION

# ---- Create application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# ---- Build dash app layout
app.layout = html.Div([navbar, source_code, *mspace, dropdown, *sspace, plots, *bspace, hist_roll, hist_graph, hist_slider, *mspace])


# ---- Indicators callbacks
@app.callback( [Output(component_id='plt_dh', component_property='figure'),
                Output(component_id='plt_lc', component_property='figure'),
                Output(component_id='plt_mc', component_property='figure'),
                Output(component_id='plt_hc', component_property='figure')],
               [Input(component_id='input-indicator', component_property='value')],
               prevent_initial_call=True)


def update_graphs(indicator):

    ''' Function returning all graph for a given indicator'''
    graphs = []

    ''' Plot predictions over on median condition versus dh (river level - galery level) '''
    # ---- Subset Data by query
    df_ss = df.query(f"indicator == '{indicator}' & h_cdt == 'mc'")
    x = df_ss['h_riv'] - df_ss['n_gal']

    # ---- Build prediction line
    trace1 = go.Scatter(name="Prédiction",
                        x = x,
                        y = df_ss['value'],
                        mode='lines',
                        line=dict(color='green', width = 1.5, dash = 'solid'),
                        showlegend=False,
                        hovertemplate ='%{y:.2f}%')

    # ---- Build 84% confidence prediction line
    trace2 = go.Scatter(name="Prédiction (84%)",
                        x=x,
                        y=df_ss['value_90'],
                        fill = 'tonexty',
                        fillcolor = 'wheat',
                        mode='lines',
                        line=dict(color='orange', width = 1.5, dash = 'solid'),
                        showlegend=False,
                        hovertemplate ='%{y:.2f}%')

    #---- Build invisible trace for adding second x-axis reprsenting simulated flow rate 
    shadow_trace = go.Scatter(x = df_ss['q_pred'],
                              y = df_ss['value'],
                              mode='lines',
                              xaxis = 'x2',
                              opacity = 0,
                              showlegend=False,
                              hoverinfo='skip',
                              visible = True)

    # ---- Build layout
    layout = go.Layout( xaxis_title = 'Niveaux rivière - Niveaux galerie (m)',
                        xaxis = dict(showgrid = True),
                        yaxis =dict(title = 'Indicateur', range=[0,100], showgrid = True),
                        title = '<b>{}</b>'.format('Conditions Générales'),
                        font = dict(size=16),
                        hovermode="x unified",
                        hoverlabel=dict(font=dict(size=16)),
                        template = 'simple_white',
                        xaxis2 = dict(title = 'Débits (m3/h)',
                                          titlefont = dict(size = 16),
                                          side = 'top',
                                          overlaying= 'x'),
                        shapes=[dict(type="rect", 
                                     xref="x", yref="y",
                                     x0=0, y0=0,
                                     x1=x.min(), y1=100,
                                     fillcolor='#6495ED', opacity=0.1,
                                     line_width=0, layer="below"),
                                dict(type="rect",
                                     xref="x", yref="y",
                                     x0=0, y0=0,
                                     x1=x.max(), y1=100,
                                     fillcolor='#FF7F50', opacity=0.1,
                                     line_width=0, layer="below")])

    # ---- Build figure
    fig = go.Figure(data=[trace1, trace2, shadow_trace], layout = layout)
    fig.add_vline(x=0, line_width=1.5, line_color="black", opacity = 1)

    # ---- Convert into dcc graph & store it
    graphs.append(fig)


    ''' Plot predictions over all hydraulic conditions '''
    # ---- Iterate over hydraulic condition
    for icdt, h_cdt in enumerate(hydraulic_conditions,start=1):

        # ---- Subset Data by query
        df_ss = df.query(f"indicator == '{indicator}' & h_cdt == '{h_cdt}'")

        # ---- Build prediction line
        trace1 = go.Scatter(name="Prédiction",
                            x = df_ss['n_gal'],
                            y = df_ss['value'],
                            mode='lines',
                            line=dict(color='green', width = 1.5, dash = 'solid'),
                            showlegend=False,
                            hovertemplate ='%{y:.2f}%')

        # ---- Build 84% confidence prediction line
        trace2 = go.Scatter(name="Prédiction (84%)",
                            x=df_ss['n_gal'],
                            y=df_ss['value_90'],
                            fill = 'tonexty',
                            fillcolor = 'wheat',
                            mode='lines',
                            line=dict(color='orange', width = 1.5, dash = 'solid'),
                            showlegend=False,
                            hovertemplate ='%{y:.2f}%')

        #---- Build invisible trace for adding second x-axis reprsenting simulated flow rate 
        shadow_trace = go.Scatter(x = df_ss['q_pred'],
                                  y = df_ss['value'],
                                  mode='lines',
                                  xaxis = 'x2',
                                  opacity = 0,
                                  showlegend=False,
                                  hoverinfo='skip',
                                  visible = True)

        # ---- Build layout
        layout = go.Layout( xaxis = dict(title = 'Niveaux galerie (mNGF)',
                                         titlefont = dict(size = 16),
                                         showgrid = True),
                            yaxis =dict(title = 'Indicateur',
                                        range=[0,100],
                                        titlefont = dict(size = 16),
                                        showgrid = True),
                            title = '<b>{}</b>'.format(fancy_cdt[icdt-1]),
                            font = dict(size=16),
                            hovermode="x unified",
                            hoverlabel=dict(font=dict(size=16)),
                            template = 'simple_white',
                            xaxis2 = dict(title = 'Débits (m3/h)',
                                          titlefont = dict(size = 16),
                                          side = 'top',
                                          overlaying= 'x',
                                          autorange="reversed"))

        # ---- Build figure
        fig = go.Figure(data=[trace1, trace2, shadow_trace], layout = layout)

        # ---- Convert into dcc graph & store it
        graphs.append(fig)

    # ---- Return all figures
    return graphs





# ---- Historical callacks
@app.callback(  Output(component_id='plt_historical', component_property='figure'),
               [Input(component_id='range-slider', component_property='value'),
                Input(component_id='rolling-number', component_property='value')])


def update_historical_graph(drange, rolling_number):

    # ---- Subset data by date range and rolling window
    dmin, dmax = [str(date) for date in drange]
    n = hist_n_gal[dmin:dmax].rolling(str(rolling_number) + 'D').mean()
    q = hist_q_gal[dmin:dmax].rolling(str(rolling_number) + 'D').mean()

    # ---- Build figure with secondary axis
    hist_fig = make_subplots(specs=[[{"secondary_y": True}]])


    # ---- Build galery stage trace
    n_trace = go.Scatter(name="Niveaux",
                     x = n.index,
                     y = n['n'],
                     mode='lines',
                     line=dict(color='green', width = 2, dash = 'solid'),
                     showlegend=True,
                     hovertemplate = '%{y:.2f} mNGF')

    # ---- Build galerie flow rate trace
    q_trace = go.Scatter(name="Debits",
                     x = q.index,
                     y = q['q'],
                     mode='lines',
                     line=dict(color='blue', width = 2, dash = 'solid'),
                     showlegend=True,
                     hovertemplate = '%{y:.2f} m3/h')

    layout = go.Layout( xaxis = dict(title = '', titlefont = dict(size = 18), tickfont=dict(size = 16)),
                        yaxis = dict(title = 'Niveaux galerie (mNGF)', titlefont = dict(size = 18), tickfont=dict(size = 16)),
                        yaxis2 = dict(title = 'Debits galerie (m3/h)', titlefont = dict(size = 18), tickfont=dict(size = 16)),
                        legend_font= dict(size = 22),
                        hoverlabel=dict(font=dict(size=16)),
                        hovermode="x unified",
                        template = 'simple_white')

    # ---- Add traces to the figure
    hist_fig.add_trace(n_trace, secondary_y=False)
    hist_fig.add_trace(q_trace, secondary_y=True)

    # ---- Update layout
    hist_fig.update_layout(layout)

    # ---- Return figure
    return hist_fig




# ---- Run application
if __name__ == "__main__":
    app.run_server(debug=True)























