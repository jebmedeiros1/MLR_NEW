from dash import html
import dash_bootstrap_components as dbc
from pages.sql import cnxn, cnxn2
from dash import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash import html, dcc
from pages import v4h as u_anomalias

#u_anomalias.a_24h()

# Defina o intervalo de atualização
intervalo_atualizacao = dcc.Interval(
    id='atualizacao-interval',
    interval=15*60*1000,  # 15 minutos em milissegundos
    n_intervals=0
)

def h24(area=None):
    query = """SELECT     dbo.TB_AREA.Area as AREA, COUNT(DISTINCT dbo.TB_Anomalias.TAG) AS Tags, COUNT(DISTINCT dbo.TB_Anomalias.MODELO) AS Modelos
                        FROM        dbo.TB_Anomalias INNER JOIN
                  dbo.TB_MODELO ON dbo.TB_Anomalias.MODELO = dbo.TB_MODELO.ID_MODELO INNER JOIN
                  dbo.TB_AREA ON dbo.TB_MODELO.ID_AREA = dbo.TB_AREA.ID_Area
                    WHERE     (dbo.TB_Anomalias.TIMESTAMP >= DATEADD(hour, -23, GETDATE()))
                    {}
                    GROUP BY dbo.TB_AREA.Area""".format(f"AND AREA in ('{area}')" if area else "")

    df = pd.read_sql(query, cnxn)



    fig = go.Figure()

    barra_Modelos = go.Bar(x=df['AREA'], y=df['Modelos'], name='Modelos', text=df['Modelos'], textposition='auto')
    barra_Tags = go.Bar(x=df['AREA'], y=df['Tags'], name='Tags', text=df['Tags'], textposition='auto')

    # Criação do layout do gráfico
    layout = go.Layout(
        title='Resumo 24 Horas',
        xaxis=dict(title='AREA'),
        #yaxis=dict(title='Contagem')
    )

    # Criação dos dados do gráfico
    data = [barra_Modelos, barra_Tags]

    # Criação da figura do gráfico
    fig = go.Figure(data=data, layout=layout)

    return fig 

def sete_dias(area=None):
    query = """SELECT     dbo.TB_AREA.Area as AREA, COUNT(DISTINCT dbo.TB_Anomalias.TAG) AS Tags, COUNT(DISTINCT dbo.TB_Anomalias.MODELO) AS Modelos
                        FROM        dbo.TB_Anomalias INNER JOIN
                  dbo.TB_MODELO ON dbo.TB_Anomalias.MODELO = dbo.TB_MODELO.ID_MODELO INNER JOIN
                  dbo.TB_AREA ON dbo.TB_MODELO.ID_AREA = dbo.TB_AREA.ID_Area
                    WHERE     (dbo.TB_Anomalias.TIMESTAMP >= DATEADD(day, -7, GETDATE()))
                    {}
                    GROUP BY dbo.TB_AREA.Area""".format(f"AND AREA in ('{area}')" if area else "")

    df = pd.read_sql(query, cnxn)


    fig = go.Figure()

    barra_Modelos = go.Bar(x=df['AREA'], y=df['Modelos'], name='Modelos', text=df['Modelos'], textposition='auto')
    barra_Tags = go.Bar(x=df['AREA'], y=df['Tags'], name='Tags', text=df['Tags'], textposition='auto')

    # Criação do layout do gráfico
    layout = go.Layout(
        title='Resumo 7 dias',
        xaxis=dict(title='AREA'),
        #yaxis=dict(title='Contagem')
    )

    # Criação dos dados do gráfico
    data = [barra_Modelos, barra_Tags]

    # Criação da figura do gráfico
    fig = go.Figure(data=data, layout=layout)

    return fig 

def formatar_delta(value):
    if value >= 0:
        return [html.I(html.Img(src="./assets/face-frown.svg", style=vermelho)),"\t"]
    elif value < 0:
        return [html.I(html.Img(src="./assets/face-smile.svg", style=verde)),"\t"]  # Substitua 'outro-icone' pela classe do seu outro ícone
    else:
        return [html.I(html.Img(src="./assets/face-frown.svg", style=amarelo)),"\t"]
    
def tabela_resumo():


    query = f"""SELECT  
        AR.AREA,
        M.DS_MODELO,
        M.MODELO,
        A.TAG,
        ROUND(AVG(A.Delta),2) AS Delta

    
    FROM 
        (SELECT 
            FORMAT(TIMESTAMP, 'yyyy-MM-dd HH') AS DataHora,
            MODELO,
            TAG,
            AVG(Delta) AS Delta
        FROM 
            [FST].[dbo].[TB_Anomalias]
        WHERE 
            TIMESTAMP >= DATEADD(HOUR, -4, GETDATE()) 
        GROUP BY 
            FORMAT(TIMESTAMP, 'yyyy-MM-dd HH'), MODELO, TAG
        ) AS A
    JOIN 
        [FST].[dbo].[TB_MODELO] AS M ON A.MODELO = M.ID_MODELO
    JOIN 
        [FST].[dbo].[TB_AREA] AS AR ON M.ID_AREA = AR.ID_AREA
    GROUP BY  
        A.Modelo, 
        A.TAG,
        M.DS_MODELO,
        M.MODELO,
        AR.AREA

    Having COUNT(A.DataHora)  >= 4
     order by AR.AREA, M.MODELO, A.TAG


    """

                
    #cursor.execute(query)
    da = pd.read_sql(query, cnxn2)
    da['DS_MODELO']=da['DS_MODELO'].str.strip()
    da['MODELO']=da['MODELO'].str.strip()
    da['TAG']=da['TAG'].str.strip()
    da['AREA']=da['AREA'].str.strip()
    #da['EVENTOS']=da['EVENTOS'].str.strip()
    tabela =  da.to_dict('records')
    return tabela

def update_tabela_resumo(area,delta,eventos):
    conditions = []
    area_cond =[]
    if area:
        #area_conditions = "', '".join(area)  # Adicionando suporte para múltiplas áreas
        area_cond.append(f" AND AR.Area in ('{area}')")
    area_where = " ".join(area_cond)

    if delta is not None:
        conditions.append(f" Delta >= {delta}")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = " AND " + where_clause  # Adicionando a cláusula WHERE
    ev1 = eventos

    query = f"""SELECT  
        AR.AREA,
        M.DS_MODELO,
        M.MODELO,
        A.TAG,
        ROUND(AVG(A.Delta),2) AS Delta

    
    FROM 
        (SELECT 
            FORMAT(TIMESTAMP, 'yyyy-MM-dd HH') AS DataHora,
            MODELO,
            TAG,
            AVG(Delta) AS Delta
        FROM 
            [FST].[dbo].[TB_Anomalias]
        WHERE 
            TIMESTAMP >= DATEADD(HOUR, -{ev1}, GETDATE())  {where_clause}
        GROUP BY 
            FORMAT(TIMESTAMP, 'yyyy-MM-dd HH'), MODELO, TAG
        ) AS A
    JOIN 
        [FST].[dbo].[TB_MODELO] AS M ON A.MODELO = M.ID_MODELO
    JOIN 
        [FST].[dbo].[TB_AREA] AS AR ON M.ID_AREA = AR.ID_AREA
    GROUP BY  
        A.Modelo, 
        A.TAG,
        M.DS_MODELO,
        M.MODELO,
        AR.AREA

    Having COUNT(A.DataHora)  >={ev1} {area_where}

    order by AR.AREA, M.MODELO, A.TAG

    """
                
    #cursor.execute(query)
    da = pd.read_sql(query, cnxn2)
    da['DS_MODELO']=da['DS_MODELO'].str.strip()
    da['MODELO']=da['MODELO'].str.strip()
    da['TAG']=da['TAG'].str.strip()
    da['AREA']=da['AREA'].str.strip()
    #da['EVENTOS']=da['EVENTOS'].str.strip()
    dados =  da.to_dict('records')
    
    return dados

def formatar_desvio(value):
    if value == 1:
        return [html.I(html.Img(src="./assets/face-frown.svg", style=vermelho)),"\t"]
    elif value == 'Normal':
        return [html.I(html.Img(src="./assets/face-frown.svg", style=verde)),"\t"]  # Substitua 'outro-icone' pela classe do seu outro ícone
    elif value == 2:
        return [html.I(html.Img(src="./assets/face-frown.svg", style=amarelo)),"\t"]  # Substitua 'outro-icone' pela classe do seu outro ícone
    else:
        return value

# Dados da tabela
dados = tabela_resumo()



# Formatações
columns = [
    {"name": "Area", "id": "AREA"},
    {"name": "Nome Modelo", "id": "DS_MODELO"},
    {"name": "Modelo", "id": "MODELO"},
    {"name": "TAG", "id": "TAG"},
    #{"name": "Eventos", "id": "Eventos"},
    {"name": "Delta %", "id": "Delta", "type": "Numeric", "presentation": formatar_delta},
    #{"name": "Desvio", "id": "Desvio", "type": "text", "presentation": formatar_desvio}
]

vermelho = { "color":"red","textAlign":"center", "fontSize":30,"margin":"auto", 'width':'40px'}
verde = { "color":"green","textAlign":"center", "fontSize":30,"margin":"auto",'width':'40px'}
amarelo = { "color":" #2e0085","textAlign":"center", "fontSize":30,"margin":"auto",'width':'40px'}

estilo_tabela={'border-style':'solid','width': '100%','overflow-y': 'scroll', 'max-height': '400px'}
estilo_tabela_linha1 ={'border-style':'solid','font-size': '30px', 'background-color': 'lightblue', 'text-align':'center'}
estilo_tabela_linha ={'border':'solid', 'width':'thin', 'font-size': '20px','text-align':'center'}
estilo_botao ={'text-align': 'right', 'font-size': 5, 'padding-top':"20px", 'height':'5px', 'width':'5px'}


layout =  dbc.Row([                  
            dbc.Col([
                html.Div([html.H2("Tags com desvio nas últimas horas", style={"text-align":'center'}),
                       dbc.Row([   
                         dbc.Col([html.Label("Area"),dcc.Dropdown(
                            id='filtro-area',
                            options=[
                                {'label': 'PMAD', 'value': 'PMAD'},
                                {'label': 'Fibras', 'value': 'Fibras'},
                                {'label': 'Recuperação', 'value': 'Recuperação'},
                                {'label': 'Utilidades', 'value': 'Utilidades'},
                                {'label': 'Secagem', 'value': 'Secagem'},
                                {'label': 'Maquinas de Papel', 'value': 'Maquinas de Papel'},
                                # Adicione as opções para cada área desejada
                            ],
                            multi=True,
                            placeholder='Selecione a(s) área(s)',
                            value=[],
                            #style={'margin-bottom': '10px'}
                        )], width=6),
                         dbc.Col([html.Label("Horas"), dbc.Input(type='number', id='N_eventos', placeholder='Eventos', min=1, max=24,value=4)], width=3),
                         dbc.Col([html.Label("Delta"), dcc.Checklist( id='delta_anomalia',options=[{'label': 'Positivo', 'value': '1'}], value=[] )], width=2),
                         dbc.Col(dbc.NavItem(dbc.NavLink([html.I(html.Img(src="./assets/refresh.svg",)), "\t"], id="at_tabela", active=True, style=estilo_botao)), width=1),
                         ])]),
                html.Div([ 
                            dash_table.DataTable(
                                id='tabela-resumo',
                                columns=[{"name": col['name'], "id": col['id']} for col in columns],
                                data=dados,
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                page_size=25,
                                style_table={'margin-top': '10px'},  # Estilo da tabela
                                # Adicione aqui mais opções de estilo conforme necessário
                            )], id='div_table2', style={'margin-top':'10px'})], md=6,lg=6),    

            dbc.Col([
                dbc.Row(
                    dcc.Graph( figure=h24(),
                                style={'width': '100%', 'height':'100%','padding-bottom': '5px'}
                            )),
                dbc.Row(
                    dcc.Graph( figure=sete_dias(),
                                style={'width': '100%', 'height':'100%','padding-bottom': '5px'}
                            )),                          
            ],md=6,lg=6),
])


