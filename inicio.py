
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL, Input, Output
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash
import pyodbc
from pages import topline, sidebar, dados, treinamento, dashboard, home
from pages import v4h as u_anomalias
from pages.unificado import gerar_grafico
from pages.dados_treino import gerar_dados, gerar_dados1
import pandas as pd
from app import app
import plotly.graph_objs as go
import asyncio
import threading
from pages.train_model import treinar_modelo
from pages.home import update_tabela_resumo, tabela_resumo
import os
import json
import cryptography.fernet as cripto
import datetime
import logging
import configparser

#============================== LIcenciamento ==============================

#============================== Configurações iniciais ==============================
df_final=pd.DataFrame()
df_pontos=pd.DataFrame()
tam=1


#============================== conexão banco ==============================
config = configparser.ConfigParser()
config.read('config.ini')



server = config['DATABASE']['server']
database = config['DATABASE']['database']
username = config['DATABASE']['username']
password = config['DATABASE']['password']
driver = config['DATABASE']['driver']

cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cnxn2 = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)


logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#============================== Definição estilos  ==============================
estilo_menu_fechado_={'text-align': 'center', 'font-size': '200%', 'padding-top':"55px", 'background-color':'#2780e3'} #estilo primiero icone menu fechado
estilo_menu_fechado={'text-align': 'center', 'font-size': '200%', 'padding-top':"25px", 'background-color':'#2780e3'}  #estilo  menu fechado
bt_aberto_estilo={'text-align': 'left', 'vertical-align': 'middle', }   #estilo  menu aberto
linha_menu = {'text-align': 'left','padding-top':"55px",'font-size': '120%',}
menu_icon = {"color":"white","textAlign":"center", "fontSize":45,"margin":"auto",'vertical-align': 'middle','width':"60px"}


#=============================Autenticação==============================

query = "SELECT count([ID_MODELO]) AS QTD  FROM [FST].[dbo].[TB_MODELO]"
da = pd.read_sql(query, cnxn)
QTD_MODEL=da['QTD'].iloc[0]

# Carregue a chave Fernet
key = 'azyrTiby3A9mq3C3NVB0v2mqczrgW-LSK8MPnyRK9tU='

# Carregue o arquivo criptografado
with open("license.json", "rb") as f:
    encrypted_license = f.read()

# Descriptografe o arquivo
decrypted_license = cripto.Fernet(key).decrypt(encrypted_license)

# Converta o arquivo descriptografado em um dicionário
license = json.loads(decrypted_license.decode())

# Verifique se a licença está válida


if datetime.datetime.strptime(license["expiration_date"],'%Y-%m-%d') < datetime.datetime.today():
    # A licença está expirada
    app.layout = html.Div([
        #html.H1("Licença expirada"),
        #html.P("A sua licença expirou em {}. Por favor, entre em contato com o suporte para obter uma nova licença.".format(license["expiration_date"])),
    ])
elif QTD_MODEL >= license["max_items"]:
    # A quantidade de itens excedeu o limite
    app.layout = html.Div([
        #html.H1("Limite de itens excedido"),
        #html.P("A quantidade de itens excedeu o limite permitido de {}. Por favor, entre em contato com o suporte para obter uma licença com um limite maior.".format(license["max_items"])),
    ])
else:
    # A aplicação pode ser executada
    #u_anomalias.a_24h()
    app.layout = dbc.Container(fluid=True, children=[
    dcc.Interval(id='interval-component', interval=1*60*60*1000*12, n_intervals=0),  # Verificação a cada hora    
    dcc.Location(id='url', refresh=True),
    dbc.Row(topline.layout, style={'padding':'0'}),
    dbc.Row([
        html.Div(sidebar.menu_layout,id='menu-col', style={'width': '5%',"padding": "0", 'background-color':'#2780e3'}),
        html.Div(id='page-content', style={'width': '95%','padding-left':'10px'}),
    ]),dcc.Store(id='df_final_store', data=df_final.to_dict(), storage_type='session'),
])




# =========  Layout Prinicipal =========== #
@app.callback(Output('interval-component', 'n_intervals'),
              [Input('interval-component', 'n_intervals')])
def check_license(n):
    if datetime.datetime.strptime(license["expiration_date"],'%Y-%m-%d') < datetime.datetime.today():
        # A licença está expirada
        app.layout = html.Div([
            #html.H1("Licença expirada"),
            #html.P("A sua licença expirou em {}. Por favor, entre em contato com o suporte para obter uma nova licença.".format(license["expiration_date"])),
        ])
    elif QTD_MODEL >= license["max_items"]:
        # A quantidade de itens excedeu o limite
        app.layout = html.Div([
            #html.H1("Limite de itens excedido"),
            #html.P("A quantidade de itens excedeu o limite permitido de {}. Por favor, entre em contato com o suporte para obter uma licença com um limite maior.".format(license["max_items"])),
    ])
   
    return n

#=============================== callbacks ==========================
@app.callback(Output('body-fase2', 'children'),
              [Input('salvar_dados', 'n_clicks')],
              [State('tabelaF', 'data'),
               State('dp_equip_dados', 'value')])
def trigger_background_task(bt_salvar, dados, id_modelo):
    if not bt_salvar:
        raise dash.exceptions.PreventUpdate

    t = threading.Thread(target=background_task, args=(dados, id_modelo))
    t.start()
    global perfil_dados
    perfil_dados = 1
    return perfil_dados
def background_task(dados, id_modelo):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def train_data_async():
        df = pd.DataFrame.from_dict(dados)
        cursor2 = cnxn2.cursor()
        cursor2.execute("DELETE FROM TB_TRAIN WHERE MODELO = ?", id_modelo)

        df_unpivot = pd.melt(df, id_vars='data', value_vars=df.columns)
        #df_unpivot.to_csv('teste.csv')

        #for row in df_unpivot.itertuples():
        #    cursor2.execute("INSERT INTO TB_TRAIN (TAG, TIMESTAMP, VALUE, PERFIL, MODELO) VALUES (?, ?, ?, ?, ?)",
        #                   row.variable, pd.to_datetime(row.data, format='%Y-%m-%d %H:%M:%S'), row.value, 0, id_modelo)

        insert_data = [(row.variable, pd.to_datetime(row.data, format='%Y-%m-%d %H:%M:%S'), row.value, 0, id_modelo) 
               for row in df_unpivot.itertuples()]
        cursor2.executemany("INSERT INTO TB_TRAIN (TAG, TIMESTAMP, VALUE, PERFIL, MODELO) VALUES (?, ?, ?, ?, ?)", insert_data)


        cnxn2.commit()
        cursor2.execute("UPDATE [dbo].[TB_TRAIN] SET [PERFIL] = 1 WHERE  [MODELO] = ?",id_modelo)
        cnxn2.commit()
        cursor2.close()
        perfil_dados = 2
        return perfil_dados

    loop.run_until_complete(train_data_async())

@app.callback(
    Output('bt_abrir_menu', 'children'),
    Output('menu-col', 'style'), 
    Output('page-content', 'style'),
    Output('navegador','children'),
    Input('bt_abrir_menu', 'n_clicks'),
    State('bt_abrir_menu', 'children'),
    
)
def toggle_menu(n_clicks, bt_sinal, ):
    global tam
    global menu2
    if not n_clicks:
        raise PreventUpdate
    if tam==2:
        tam = 1
        menu2= [
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/home.svg",style=menu_icon)), "\t"], href="/home", active=True, style=estilo_menu_fechado_)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/lupa.svg",style=menu_icon)), "\t"], href="/dashboard", active=True, style=estilo_menu_fechado_)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/gear.svg", style=menu_icon)), "\t"], id='modelos_button', active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/dbc.svg",style=menu_icon)), "\t"], href="/dados", active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/chip.svg",style=menu_icon)), "\t"], href="/treinamento", active=True, style=estilo_menu_fechado)),
            dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/user.svg",style=menu_icon)), "\t"], id='login_button', active=True, style=estilo_menu_fechado)),
                        ] 
        return ">>>",{'width': '5%', "padding": "0",'background-color':'#2780e3',}, {'width': '95%', "padding-left": "10px",},menu2

    else:
        tam = 2
        menu2= [dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/home.svg",style=menu_icon)), "\t INÍCIO"], href="/home", active=True,style=linha_menu, className=bt_aberto_estilo)),
                dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/lupa.svg",style=menu_icon)), "\t DASHBOARD"], href="/dashboard", active=True,style=linha_menu, className=bt_aberto_estilo)),
                    dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/gear.svg",style=menu_icon)), "\t CRIAR MODELOS"], id='modelos_button', active=True,style=linha_menu,className=bt_aberto_estilo)),
                    dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/dbc.svg",style=menu_icon)), "\t DADOS MESTRE"], href="/dados", active=True,style=linha_menu,className=bt_aberto_estilo)),
                    dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/chip.svg",style=menu_icon)), "\t TREINAR MODELOS"], href="/treinamento", active=True,style=linha_menu,className=bt_aberto_estilo)),
                    dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/user.svg",style=menu_icon)), "\t LOGIN"], id='login_button', active=True, style=linha_menu, className=bt_aberto_estilo)),

                    ]
        return "<<<", {'width': '13%',"padding": "0",'background-color':'#2780e3'}, {'width': '87%', "padding-left": "10px",},menu2

# Atualiza as paginas botao side bar
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def render_page_content(pathname):
    if pathname == '/home' or pathname == '/' or pathname == '/MLR/':
        return home.layout
    if pathname == '/dashboard':
        return dashboard.layout
    if pathname == '/dados':
        return dados.layout
    if pathname == '/treinamento':
        return treinamento.layout
    return dbc.Container([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"O caminho '{pathname}' não foi reconhecido..."),
            html.P("Use a NavBar para retornar ao sistema de maneira correta.")
        ])

#Gera os cards dos modelos previsto vs real
@app.callback(
    Output('cards_modelos', 'children'),
    Output('head_graficos','children'),
    Input('btn_h_atualizar', 'n_clicks'),
    Input("dropdown-modelo", "value"),
    State('equip_filter', 'value'),
    State('equip_filter', 'options'),
    Input("dias_analise", "value"),
    prevent_initial_call=False
)
def gerar_cards(n_clicks,selected_options,tag_equip,options_modelo,dias):
    if not n_clicks:
        raise PreventUpdate
    
    label = next(option['label'] for option in options_modelo if option['value'] == tag_equip).strip()
    cards = []

    for index, modelo in enumerate(selected_options):
        query = "SELECT DESCRICAO From TB_TAGS where TAG='" + str(modelo) + "'"
        da = pd.read_sql(query, cnxn)
        descricao = da['DESCRICAO'].iloc[0]
        card = dbc.Col([
            dbc.Card([
                dbc.CardHeader(modelo + '-' + descricao),
                dbc.CardBody([
                    dcc.Graph(
                        id={'type': 'dynamic-graph', 'index': index},
                        figure=gerar_grafico(tag_equip, modelo, dias),
                        style={'width': '100%', 'height': 300, 'padding-bottom': '5px'}
                    )
                ])
            ])
        ])
        cards.append(card)

    query = "SELECT DS_MODELO From TB_MODELO where ID_MODELO='" + str(tag_equip) + "'"
    df = pd.read_sql(query, cnxn)
    Descricao = df['DS_MODELO'].iloc[0]
    return cards, Descricao



#Atualiza os valores dos Modelo no Dropdown - Area atualiza Modelo
@app.callback(
    Output('equip_filter', 'options'),
    Input('areas_filter', 'value'),
    State('equip_filter', 'value'))
def update_equip_options(selected_area, selected_equip):
        if not selected_area:
            raise PreventUpdate


        query = "SELECT ID_MODELO, MODELO From TB_MODELO where ATIVO = 1 and ID_Area="+str(selected_area)
        df = pd.read_sql(query, cnxn)
       
        options = [{'label': row['MODELO'], 'value': row['ID_MODELO']} for index, row in df.iterrows()]
        
        return options

#Atualiza os valores das Tags dos Modelos - Modelo atualiza Tags
@app.callback(
    Output('dropdown-modelo', 'options'),
    Output('checkbox-all-models','value'),
    Output('var_comentario','options'),
    Input('equip_filter', 'value'),
    State('dropdown-modelo', 'value'))
def update_dropdown_options(selected_equip, selected_dropdown):

    if not selected_equip:
        raise PreventUpdate   
          
    query = "SELECT TAG FROM TB_TAGS where MONITORADA='S' AND MODELO='"+str(selected_equip) +"' order by TAG"
    df = pd.read_sql(query, cnxn)

    options = [{'label': i, 'value': i} for i in df['TAG']]
    todos = []

    return options, todos,options

@app.callback(
    Output('dropdown-modelo', 'value'),
    Input('checkbox-all-models', 'value'),
    State('dropdown-modelo', 'options')
)
def update_dropdown_models(checkbox_value, dropdown_options):
    if 'all' in checkbox_value:
        return [option['value'] for option in dropdown_options]
    else:
        return []

#Abre o Modal de Criar Modelos
@app.callback(
    Output('modal_modelos', "is_open"),
    Input("modelos_button", 'n_clicks'),
    Input('cancel_button', 'n_clicks'),
    State('modal_modelos', "is_open")
)
def toggle_modal_processo(n,n2, is_open):
    if n or n2:
        return not is_open
    return is_open

#Atualiza os valores dos Modelo no Dropdown - Area atualiza Modelo
@app.callback(
    Output('dp_equip_dados', 'options'),
    Input('dp_areas_dados', 'value'),
    State('dp_equip_dados', 'value'))
def update_equip_options(selected_area, selected_equip):
        if not selected_area:
            raise PreventUpdate

        query = "SELECT ID_MODELO, MODELO From TB_MODELO where ID_Area="+str(selected_area)+" order by MODELO"
        df = pd.read_sql(query, cnxn)
       
        options = [{'label': row['MODELO'], 'value': row['ID_MODELO']} for index, row in df.iterrows()]
        
        return options

@app.callback(Output('df_final_store', 'data'),
              Output('dropdown-dados', 'options'),
              [Input('atualizar_dados', 'n_clicks'),
               State("dp_equip_dados", "value"),
               State('date-picker-config', 'start_date'),
               State('date-picker-config', 'end_date'),],
                prevent_initial_call=False
)
def gerar_df(n_clicks,selected_options,dt_ini,dt_fim):
    
    if not n_clicks:
        raise PreventUpdate
    
    #selected_options = '32310P4116'
   

    query = "SELECT TAG FROM TB_TAGS where  MODELO='"+str(selected_options) +"' order by TAG"
    df = pd.read_sql(query, cnxn)

    options = [{'label': i, 'value': i} for i in df['TAG']]


    #equip = '32310P4116'
   
    DF_MODELO = gerar_dados1(selected_options,dt_ini,dt_fim)
    global df_final
    df_final = DF_MODELO.copy()
    
    # Convert Timestamp columns to string representation
    #df_final['data'] = df_final['data'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
    df_final['data'] = df_final['data']
    # Convert DataFrame to JSON serializable format
    df_final_json = df_final.to_json(date_format='iso', orient='split')

    data_1= dt_ini


    
    return df_final_json, options

@app.callback(Output('fig_card', 'figure'),
              Output('excluir_dados', 'n_clicks'),
              Output('tabelaX', 'data'),
              Output('tabelaF', 'data'),
              Output('body-fase','children'),
           
            [Input('excluir_dados', 'n_clicks'),
             Input('fig_card','selectedData'),
             Input('dropdown-dados', 'value')],
             State('df_final_store', 'data'),
             State('atualizar_dados','n_clicks'))
def atualiza_tabela(bt_excluir,dados_selecionados,tag_modelo,df_final_data,bt_atualizar):
    global df_pontos
    global df_final
    global fig 
    global fase

    fase=ctx.triggered_id if not None else 'No clicks yet'

    tabelaF = df_final.to_dict('records')

    if not bt_atualizar: # garantir Dados carregados
            raise PreventUpdate
    
    if fase == "fig_card":
         raise PreventUpdate
    
    if dados_selecionados is not None:
        if len(dados_selecionados)>=1:
            
            #if bt_excluir is None:
            #        raise PreventUpdate     

            if bt_excluir == 1:
                x = [point['x'] for point in dados_selecionados['points']]
                y = [point['y'] for point in dados_selecionados['points']]
                x = [date + " 00:00" if len(date) == 10 else date for date in x]
                df_pontos = pd.DataFrame({'x': x, 'y': y})
                #df_pontos['x'] = pd.to_datetime(df_pontos['x'], format='%Y-%m-%d %H:%M')

                df_final = df_final.loc[~df_final['data'].isin(df_pontos['x'])]
                novo_data = df_pontos.to_dict('records')
                tabelaF = df_final.to_dict('records')

                tag_modelo= tag_modelo.strip()
                
                fig =go.Figure(
                    [go.Scatter(
                        x=df_final['data'],
                        y=df_final[tag_modelo], 
                        name='Valores reais', 
                        mode='markers', 
                        connectgaps=False)
                        ],
                layout=go.Layout(
                legend=dict(orientation='h',x=0.5, y=-0.3, xanchor='center',yanchor='bottom'),
                margin=dict(l=0, r=0, b=0, t=0, pad=0),
                #width='auto',
                dragmode='select')
                            ) 
                
                fase=ctx.triggered_id if not None else 'No clicks yet'
                dados_selecionados.clear()

                return fig,None, novo_data, tabelaF, fase


    if tag_modelo:
                tag_modelo= tag_modelo.strip()
                
                fig =go.Figure(
                            [go.Scatter(
                                    x=df_final['data'],
                                    y=df_final[tag_modelo], 
                                    name='Valores reais', 
                                    mode='markers', 
                                    connectgaps=False)
                                ],
                layout=go.Layout(
                legend=dict(orientation='h',x=0.5, y=-0.3, xanchor='center',yanchor='bottom'),
                margin=dict(l=0, r=0, b=0, t=0, pad=0),
                #width='auto',
                dragmode='select')
                                ) 
                

                   

    
                return fig,dash.no_update,None, tabelaF, fase
    
@app.callback(
    Output('dp_perfil', 'options'),
    Output('dropdown_cutover', 'options'),
    Input('dp_equip_dados', 'value')
            )
def update_perfil_options(equipamento):

   #if ctx.triggered_id == "dp_equip_dados":


        query = "SELECT distinct [PERFIL] From [TB_TRAIN] where PERFIL <> 0 and MODELO='"+str(equipamento) +"'"
        df = pd.read_sql(query, cnxn)
       
        options = [{'label': row['PERFIL'], 'value': row['PERFIL']} for index, row in df.iterrows()]

        query = "SELECT TAG FROM TB_TAGS where MONITORADA='S' AND MODELO='"+str(equipamento) +"'"
        df = pd.read_sql(query, cnxn)

        options2 = [{'label': i, 'value': i} for i in df['TAG']]
        
        return options,options2

@app.callback(Output('body_modelo','children'),
              Output('cards_treinos','children'),
              Input('treinar_modelo','n_clicks'),
              State('dp_equip_dados','value'),
              State('dp_perfil','value'),
              )
def treinar(bt_treinar, ativo,perfil):
     
    if bt_treinar is None:
       raise PreventUpdate   
    
    modelo = treinar_modelo(ativo,perfil)
    tb = "ok"
    
    return tb,"FINALIZADO"

@app.callback(
    Output('output-status', 'children'),
    [Input('btn_cutover', 'n_clicks')],
    [State('dp_equip_dados', 'value'),
     State('dropdown_cutover', 'value'),  
     State('cutover', 'value')]
)
def inserir_atualizar_callback(n_clicks, modelo, tag, valor):
    if n_clicks is None:
       raise PreventUpdate  
    if n_clicks > 0:
        # Chamada da função de inserir/atualizar
        inserir_atualizar_valor(modelo, tag, valor)
        return 'Valores inseridos/atualizados com sucesso!'
    else:
        return ''
def inserir_atualizar_valor(modelo, tag, valor):
    # Cria a string de conexão

    # Conecta ao banco de dados
    #conn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()

    # Verifica se a tag já existe na tabela
    cursor.execute("SELECT * FROM TB_CUTOVER WHERE modelo = ? and tag=?", modelo,tag)
    row = cursor.fetchone()

    if row:
        # Atualiza o valor da tag existente
        cursor.execute("UPDATE TB_CUTOVER SET valor=? WHERE modelo = ? and tag=?", valor, modelo , tag)
    else:
        # Insere uma nova tag na tabela
        cursor.execute("INSERT INTO TB_CUTOVER (modelo, tag, valor) VALUES (?, ?, ? )", modelo, tag, valor)

    # Confirma as alterações no banco de dados
    cnxn.commit()

    # Fecha a conexão
    #cursor.close()
    #cnxn.close()

@app.callback(
    Output('tabela-resumo', 'data',allow_duplicate=True),
    Input('filtro-area', 'value'),
    Input('delta_anomalia', 'value'),
    Input('N_eventos', 'value'),prevent_initial_call=True

)
def update_table(areas,delta,eventos):
    area = "', '".join(areas) if areas else None
    if "1" in delta:
        delta =1
    else:
        delta =-999999
    return update_tabela_resumo(area,delta,eventos)


@app.callback(
    Output('url', 'pathname'),
    Input('update_anomalias', 'n_clicks')
)
def execute_and_refresh(n_clicks):
    if not n_clicks:
        raise PreventUpdate   
        #return dash.no_update, dash.no_update

    # Execute seu código aqui.
    u_anomalias.a_24h()
    # Redefinindo a URL para a mesma força o refresh da página.
    return '/'


#=======================================================================
@app.callback(Output('output-comentario', 'children'),
              Input('botao-enviar','n_clicks'),
              State('var_comentario','value'),
              State('date-picker-single','date'),
              State('textarea-comentario','value'),
              State('equip_filter', 'value'))


def Excluir(btn,tag,data,comentario,modelo):
        
    if not btn:
        raise PreventUpdate
    

    cursor = cnxn.cursor() 
    
    
    if tag != None:
        hora = datetime.datetime.now()
        hora = hora.strftime('%H:00:00')
        data += " "+hora
        #if modelo == "Modelo encontrado": 
        cursor.execute("INSERT INTO TB_COMENTARIO (TAG, TIMESTAMP, MODELO, COMENTARIO) VALUES (?, ?, ?, ? )", tag, data, modelo, comentario)
        cnxn.commit()
        aviso= "Comentario inserido"

    else:
        aviso = "erro"

    return aviso



@app.callback(
    Output({'type': 'dynamic-graph', 'index': 1}, 'relayoutData'),
    [Input({'type': 'dynamic-graph', 'index': 0}, 'relayoutData')],
    prevent_initial_call=True
)
def synchronize_zoom(relayoutData):
    # Verifica se os dados de relayoutData foram recebidos
    if not relayoutData:
        return dash.no_update

    # Exemplo de dados de relayoutData para testar a sincronização
    trigger_data = {
        'xaxis.range[0]': '2023-11-10 00:48:39.2299', 
        'xaxis.range[1]': '2023-11-10 02:30:35.2229'
    }

    # Verifica se a mudança é relacionada ao zoom no eixo x
    if 'xaxis.range[0]' in trigger_data and 'xaxis.range[1]' in trigger_data:
        xaxis_range = [trigger_data['xaxis.range[0]'], trigger_data['xaxis.range[1]']]
        #print(f"Atualizando zoom para gráfico com index 1: {xaxis_range}")
        return {'xaxis.range': xaxis_range}
    
    return dash.no_update


@app.callback(
    Output('date-picker-single', 'date'),
    Input('dummy-div', 'children')
)
def update_date(_):
    return datetime.date.today()

@app.callback(
     Output('tabela-resumo', 'data',allow_duplicate=True),
     Output('filtro-area', 'value'),
     Input('at_tabela', 'n_clicks'),
     prevent_initial_call=True
)
def tabelainicial(clicou):
   return tabela_resumo(),[]



# =========  Inicialização  =========== #




if __name__ == '__main__':
    app.run(debug=False,host="0.0.0.0", port=8081 )
    #app.run_server(debug = True, port=443, host="127.0.0.1") 