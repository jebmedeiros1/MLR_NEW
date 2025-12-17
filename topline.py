from dash import html
import dash_bootstrap_components as dbc
from globals import *
import getpass
from pages.sql import cnxn
'-------------------------'



'--------------------------'
card_icon = {
    "color":"white",
    "textAlign":"center",
    "fontSize":30,
    "margin":"auto",
    "width":'40px'
}


def anomalias():
    cursor = cnxn.cursor()
    query = "SELECT count(distinct(TAG)) FROM TB_anomalias WHERE TIMESTAMP >= DATEADD(hour, -23, GETDATE())"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def total_tags():
    cursor = cnxn.cursor()
    query = "SELECT count(distinct(TAG)) FROM TB_TAGS WHERE MONITORADA = 'S'"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def total_MODELOS():
    cursor = cnxn.cursor()
    query = "SELECT count(distinct(MODELO)) FROM TB_MODELO"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def MODELOS_ativos():
    cursor = cnxn.cursor()
    query = "SELECT count(distinct(MODELO)) FROM TB_MODELO WHERE ATIVO=1"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]


usuario = getpass.getuser()
alertas = anomalias()
n_tags=total_tags()
n_modelos=total_MODELOS()
a_modelos = MODELOS_ativos()
# =========  Layout  =========== #
layout = dbc.Col([
            dbc.Row([
                dbc.Col([dbc.Button("Atualizar", id="update_anomalias", style={'width': '100%'}, color="Blue"),]),
                dbc.Col([
                    dbc.CardGroup([
                        dbc.Card(
                            html.Div(html.Img(src="./assets/desktop.svg", style=card_icon)),
                            color='green', 
                            style={'maxWidth':50, 'height':60, 'margin-left':'-10px'}
                        ),                    
                        dbc.Card([
                            html.Div(style={'display': 'flex', 'flex-wrap': 'nowrap'}, 
                                children=[
                                    html.Legend(f"{a_modelos}/{n_modelos} - Modelos em monitoramento",style={'margin-left':'-10px'}) 
                                ])], style={'padding-left':'20px','padding-top':'10px'})
                    ])
                ], md=3),
                dbc.Col([
                    dbc.CardGroup([
                        dbc.Card(
                            html.Div(html.Img(src="./assets/exclamation.svg", style=card_icon)),
                            color='danger', 
                            style={'maxWidth':50, 'height':60, 'margin-left':'-10px'}
                        ),                    
                        dbc.Card([
                            html.Div(style={'display': 'flex', 'flex-wrap': 'nowrap'}, 
                                children=[
                                    html.Legend(f"{alertas}/{n_tags} - Tags com anomalia últimas 24h",style={'margin-left':'-10px'}) 
                                ])], style={'padding-left':'20px','padding-top':'10px'})
                    ])
                ], md=4),
                dbc.Col([html.Legend(f"Usuário: {usuario}",style={'text-align': 'right','padding-top':'10px'})])
    ], style={'margin':'10px'}),

#--------------
],style={'background-color': '#ADD8E6','padding':'0'})

# =========  Callbacks  =========== #
