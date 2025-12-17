from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

from pages.sql import df_area


card_dados=[]
fig=go.Figure()
df_final= pd.DataFrame()


# ========= Layout ========= #
layout = dbc.Container([
    html.Hr(),
    dbc.Row([
        # Filtros
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Seleção dos Modelos")
                                ])
                            ], style={'margin-top': '1px'}),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='dp_areas_dados',
                                        options=[{'label': row['AREA'], 'value': row['ID_AREA']} for index, row in df_area.iterrows()],
                                        placeholder='SELECIONE A AREA',
                                        className='dbc'
                                    ),
                                ])
                            ],style={'padding-top':'10px'}),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='dp_equip_dados',
                                        #options=[],
                                        placeholder='SELECIONE O MODELO',
                                        className='dbc'
                                    ),
                                ])
                            ], style={'padding-top':'10px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Perfil"),
                                    html.Div(
                                    dbc.Row([
                                    dcc.Dropdown(
                                        id="dp_perfil",
                                        #options=modelos2,
                                        clearable=False,
                                        style={"width": "100%"},
                                        persistence=True,
                                        persistence_type="session",
                                        multi=False, disabled=False
                                        )])
                                    ),
                                    
                                ])
                            ], style={'margin-top': '15px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Treinar", id="treinar_modelo", style={'width': '100%'}, color="dark"),
                                    html.Div(id='body_modelo')
                                ]),
                            ], style={'margin-top': '15px'}),
                       ], style={'margin': '10px'})
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Ajuste Cutover")
                                ])
                            ], style={'margin-top': '1px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Tag"),
                                    html.Div(
                                    dbc.Row([
                                    dcc.Dropdown(
                                        id="dropdown_cutover",
                                        #options=modelos2,
                                        clearable=False,
                                        style={"width": "100%"},
                                        persistence=True,
                                        persistence_type="session",
                                        multi=False)                       
                                    ])
                                    ),
                                    
                                ])
                            ], style={'margin-top': '15px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(type='number', id='cutover', placeholder='Valor de corte'),
                                ])]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Cutover", id="btn_cutover", style={'width': '100%'}, color="dark"),
                                    html.Div(id='output-status')
                                ]),
                            ], style={'margin-top': '15px'}),
                       ], style={'margin': '10px'})
                    ]),
                ])
            ,])
            
        ], sm=12, md=4, lg=3, style={'padding': '0px', 'padding-left':'10px'}),
        #graficos
        dbc.Col([
            dbc.Row(
                    dbc.Col([dbc.Row(id='cards_treinos', style={'padding-bottom': '10px'})]), id='cards-dado', style={'padding-bottom': '10px'}
                    ),
            #dbc.Row(html.Div([html.H4("tabelaX"),table3,table,table2]))
            ], md=8, lg=9, style={'max-height':'95hv','overflow-y': 'auto'}),
    ])

], fluid=True, style={'height': '100hv', 'padding': '0px', 'margin': 0, 'padding-left': 0}),



