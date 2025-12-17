
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
import plotly.graph_objs as go

from pages.sql import df_area
from datetime import datetime, timedelta


card_dados=[]
fig=go.Figure()
df_final= pd.DataFrame()

# Define o componente DataTable
table = dash_table.DataTable(
    id='tabelaX')
table2 = dash_table.DataTable(#df_final.to_dict('records'), [{"name": i, "id": i} for i in df_final.columns],
    id='tabelaF')
table3 = dash_table.DataTable(#df_final.to_dict('records'), [{"name": i, "id": i} for i in df_final.columns],
    id='tabelaTG')

#lasso_selector = LassoSelector(fig, onselect=None)


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
                                        #options=[{'label': Area, 'value': ID_Area} for ID_Area, Area in area_dic.items()],
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
                                html.Legend("Período de Análise", style={"margin-top": "10px"}),
                                dcc.DatePickerRange(
                            month_format='Do MMM, YY',
                            end_date_placeholder_text='Data...',
                            start_date=datetime.today()- timedelta(days=180),
                            end_date=datetime.today() ,
                            with_portal=True,
                            updatemode='singledate',
                            id='date-picker-config',
                            style={'z-index': '100'}),
                            ], style={'margin-top': '15px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Atualizar", id="atualizar_dados", style={'width': '100%'}, color="dark"),
                                ]),
                            ], style={'margin-top': '15px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Variáveis"),
                                    html.Div(
                                    dbc.Row([
                                    dcc.Dropdown(
                                        id="dropdown-dados",
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
                       ], style={'margin': '10px'})
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Tratamento de Dados")
                                ])
                            ], style={'margin-top': '1px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Excluir", id="excluir_dados", style={'width': '50%'}, color="dark"),
                                    html.Div(id='body-fase')
                                ]),
                            ], style={'margin-top': '15px'})
                        ])
                    ]),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("")
                                ])
                            ], style={'margin-top': '1px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Salvar Perfil", id="salvar_dados", style={'width': '50%'}, color="dark"),
                                    html.Div('',id='body-fase2'),
                                    ]),
                            ], style={'margin-top': '15px'})
                        ])
                    ])
                ])
            ])
        ], sm=12, md=3, lg=3, style={'padding': '0px', 'padding-left':'10px'}),
        #graficos
        dbc.Col([
            dbc.Row(
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(' - Descrição da Tag'),
                                dbc.CardBody([
                                    dcc.Graph(
                                        id='fig_card',
                                        style={'width': 'auto', 'height':680,'padding-bottom': '5px'}
                                    )
                            ])
                        ])
                    ]), id='cards-dado', style={'padding-bottom': '10px'}
                    ),
            dbc.Row(html.Div([html.H4("tabelaX"),table3,table,table2], style={'display':"None"})
                    )
            ], md=9, lg=9, style={'max-height':'95hv','overflow-y': 'auto'}),
    ])

], fluid=True, style={'height': '100hv', 'padding': '0px', 'margin': 0, 'padding-left': 0})


