from dash import html
import dash_bootstrap_components as dbc
from pages import modal_modelos
import os



# ========= Layout ========= #

estilo_menu_fechado_={'text-align': 'center', 'font-size': '200%', 'padding-top':"55px", 'background-color':'#2780e3'} #estilo primiero icone menu fechado
estilo_menu_fechado={'text-align': 'center', 'font-size': '200%', 'padding-top':"25px", 'background-color':'#2780e3'}  #estilo  menu fechado

menu_icon = { "color":"white","textAlign":"center", "fontSize":45,"margin":"auto","width":"60px",}


menu_layout = dbc.Container([
    modal_modelos.layout,
dbc.Row([
    dbc.Col([
        dbc.Nav([
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/home.svg",style=menu_icon)), "\t"], href="/home", active=True, style=estilo_menu_fechado_)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/lupa.svg",style=menu_icon)), "\t"], href="/dashboard", active=True, style=estilo_menu_fechado_)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/gear.svg", style=menu_icon)), "\t"], id='modelos_button', active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/dbc.svg",style=menu_icon)), "\t"], href="/dados", active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/chip.svg",style=menu_icon)), "\t"], href="/treinamento", active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/user.svg",style=menu_icon)), "\t"], id='login_button', active=True, style=estilo_menu_fechado)),
        ], vertical="lg", pills=True, fill=True, id="navegador"),
        dbc.Row([
            dbc.Col(dbc.Button(">>>", id="bt_abrir_menu", n_clicks=0), width="auto")
        ], justify="center", style={'margin-top': '10px'})
    ])
])

    ], style={'height': '100vh', 'padding': '0px', 'position':'sticky', 'top': 0, 'background-color': 'None'})
