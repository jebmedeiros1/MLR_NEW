
from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.sql import df_area
#from dash_bootstrap_components import Input
from datetime import date, timedelta

# ========= Styles ========= #
card_style={'height': '100%',  'margin-bottom': '12px'}

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
                                        id='areas_filter',
                                        options=[{'label': row['AREA'], 'value': row['ID_AREA']} for index, row in df_area.iterrows()],
                                        placeholder='SELECIONE A AREA',
                                        className='dbc'
                                    ),
                                ])
                            ],style={'padding-top':'10px'}),
                             dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='equip_filter',
                                        #options=[],
                                        placeholder='SELECIONE O MODELO',
                                        className='dbc'
                                    ),
                                ])
                            ], style={'padding-top':'10px'}),

                             dbc.Row([
                                dbc.Col([
                                    html.Label("Variáveis"),
                                    html.Div(
                                    dcc.Dropdown(
                                        id="dropdown-modelo",
                                        #options=modelos2,
                                        clearable=False,
                                        style={"width": "100%"},
                                        persistence=True,
                                        persistence_type="session",
                                        multi=True)                       
                                    ),
                                ])
                            ], style={'margin-top': '15px'}),

                             dbc.Row([
                                dbc.Col([
                                    dcc.Checklist(
                                        id='checkbox-all-models',
                                        options=[{'label': 'Selecionar todos', 'value': 'all'}],
                                        value=[]
                                    )
                                ])
                            ], style={'margin-top': '15px'}),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Atualizar", id="btn_h_atualizar", style={'width': '100%'}, color="dark")
                                ])
                            ], style={'margin-top': '15px'}),

                            dbc.Row([
                                dbc.Col([ html.Label("Dias para análise"),
                                    dbc.Input(type='number', id='dias_analise', placeholder='Dias de para análise', min=1, max=180,value=7)
                                ])
                            ], style={'margin-top': '15px'}),
                            
                        ], style={'margin': '10px'})
                    ])
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4("Comentários"),
                                    dbc.Row([
                                        html.Label("Variável"),
                                        html.Div(
                                        dcc.Dropdown(
                                            id="var_comentario",
                                            #options=var_coment,
                                            clearable=True,
                                            style={"width": "100%"},
                                            persistence=True,
                                            persistence_type="session",
                                            multi=False)                       
                                        ),
                                        ], style={'margin-top': '15px'}),
                                    html.Label("Seletor de Data"),
                                    dbc.Row(),
                                    dcc.DatePickerSingle(
                                        id='date-picker-single',
                                        display_format='DD/MM/YYYY',
                                        min_date_allowed=date.today()- timedelta(days=180),  # Data mínima permitida
                                        max_date_allowed=date.today() ,  # Data máxima permitida
                                        date=date.today()  # Define a data padrão como hoje
                                        
                                    ),html.Div(id='dummy-div'),
                                    dbc.Row(html.Label("Insira seu comentário"),),
                                    dbc.Textarea(id="textarea-comentario", placeholder="Digite seu comentário aqui", style={"width": "100%"}),
                                    html.Br(),
                                    dbc.Button("Enviar Comentário", id="botao-enviar", color="primary"),
                                    html.Div(id="output-comentario")
                                ])
                            ], style={'margin-top': '1px'}),
                        ])
                    ])
                ])
            ])], sm=12, md=2, lg=2, style={'padding': '1px', 'padding-left':'10px'}),
        #graficos
        dbc.Col([
            dbc.Row(html.H1(id='head_graficos'),style={'text-align': 'center'}),
            dbc.Row([], id='cards_modelos', style={'padding-bottom': '10px'})
        ], md=10, lg=0, style={'max-height':'95hv','overflow-y': 'auto'}),
    ])

], fluid=True, style={'height': '100hv', 'padding': '0px', 'margin': 0, 'padding-left': 0})

