import joblib
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import pyodbc
import configparser

    # Lendo o arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')



server = config['DATABASE']['server']
database = config['DATABASE']['database']
username = config['DATABASE']['username']
password = config['DATABASE']['password']
driver = config['DATABASE']['driver']


connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connect = pyodbc.connect(connection_string)
consulta = f" SELECT MODELO, TAG, max([VALUE]) as MAXIMO FROM [FST].[dbo].[TB_TRAIN] group by modelo, tag"

dm = pd.read_sql(consulta, connect)
dm['TAG']=dm['TAG'].str.strip()

def maximohistorico(tag,modelo):
    _Maxdm = dm[(dm['MODELO'] == modelo) & (dm['TAG'] == str(tag))]
    return _Maxdm['MAXIMO'].iloc[-1]

def gerar_grafico(ativo, Coluna,dias):


    
    
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    cnxn2 = pyodbc.connect(connection_string)

    


    def calcular_percentual(valor):
        if 0 <= valor <= 1:
            return 1
        elif 1 < valor <= 2:
            return 0.50
        elif 2 < valor <= 3:
            return 0.40
        elif 3 < valor <= 4:
            return 0.30
        else:
            return 0.20


    query = "SELECT TAG FROM TB_TAGS where MODELO='"+str(ativo) +"'"
    df = pd.read_sql(query, cnxn)
    df['TAG'] = df['TAG'].str.strip()
    tag_list = df['TAG'].values.tolist()

    Coluna= str(Coluna).strip()

    filename = ativo+Coluna+'.jet'

    # get model from disk
    model = joblib.load("models/"+filename)

    tags_string = ', '.join(f"''{tag}''" for tag in tag_list)

    consulta = f"""SELECT tag, time, value, pctgood 
    FROM OPENQUERY(TESTE_PI, 'SELECT tag, expr, filterexpr, filtersampletype, filtersampleinterval, timestep, time, calcbasis, value, pctgood 
    FROM piarchive..piavg 
    WHERE time BETWEEN CAST(''-{dias}d'' AS DATETIME) AND CAST(''*'' AS DATETIME) 
    AND timestep = CAST(''5m'' AS TIME) 
    AND tag IN ({tags_string})') AS piavg
    """

    da = pd.read_sql(consulta, cnxn)
    da['time'] = da['time'].str[0:16]
    da = da.dropna(subset=['value'], axis=0)
    tag_list2 = da['tag'].values.tolist()
    da = pd.pivot_table(data=da, index='time', columns='tag', values='value')
    
   
    try:
        X = da.drop(Coluna, axis=1)
        y = da[Coluna]
        tag_list2 = list(set(tag_list2))
        if all(item in tag_list2 for item in tag_list):


            predictions = model.predict(X)

            residuals = y - predictions
            try:
                p_residuals = np.abs(residuals)/predictions
            except:
                p_residuals=0

            threshold =  calcular_percentual(predictions.max())
            # Aqui nós verificamos duas condições:
            # 1. Se o valor real (y) é maior que maximohistorico.
            # 2. Se o valor percentual residual (p_residuals) é maior que o threshold.
            # Se qualquer uma das condições for verdadeira, anomalia será 1, caso contrário, será 0.
            anomalies = np.where((y > maximohistorico(Coluna,ativo)) | (p_residuals > threshold), 1, 0)
            #anomalies = np.where(p_residuals > threshold, 1, 0)

            da['Anomalia'] = anomalies
            da[Coluna+'Prev'] = predictions
            da['data']=da.index
            da['data'] = pd.to_datetime(da['data'])
            da=da.sort_values(by='data')
            yreal=y
            y_min = min(yreal.min(), predictions.min())
            y_max = max(yreal.max(), predictions.max())
            if y_min>0:
                delta = (y_max/y_min)
            else:
                delta =y_max*0.1
                
            y_min = y_min-delta
            y_max = y_max*1.1 
            
            if y_min<y_max:
                y_min = yreal.min()
                y_max =yreal.max()
            else:
                y_max = yreal.min()
                y_min =yreal.max()
                
            #print(yreal.min(),yreal.max())
            try:
                consulta = f"SELECT tag, Valor fROM TB_CUTOVER Where Modelo='{ativo}'"
                dc = pd.read_sql(consulta, cnxn)
                cutover=dc['tag'].iloc[-1].strip()
                cutvalue =  dc['Valor'].iloc[-1]
                da.loc[da[cutover] < cutvalue, 'Anomalia'] = 0

            except:
                a=1

            


            fig = go.Figure()
            
            
            # Adding traces for real values and predicted values
            fig.add_trace(go.Scatter(x=da['data'], y=yreal, name='Valores reais', mode='lines', connectgaps=False,yaxis='y'))
            fig.add_trace(go.Scatter(x=da['data'], y=predictions, name='Valores previstos', mode='lines', connectgaps=False,yaxis='y'))
            
            
            
            
            try:
                query = "SELECT TIMESTAMP, COMENTARIO FROM TB_COMENTARIO where MODELO='"+str(ativo) +"' AND  TAG= '"+str(Coluna)+ "' AND TIMESTAMP >= DATEADD(DAY, -"+ str(dias) +", GETDATE())"
                df2 = pd.read_sql(query, cnxn)

                
                fig.add_trace(go.Scatter(
                        x=df2['TIMESTAMP'],
                        y=yreal,
                        mode='markers',
                        marker=dict(size=12, color='purple'),
                        hovertext=df2['COMENTARIO'],
                        #hoverinfo='text+x+y',
                        showlegend=False,
                        connectgaps=False,yaxis='y'
                ))


            except:
                 a=2
            #Adding bar chart for anomalies
        #Adding markers for anomalies when the last 6 records are all 1
            #if anomalies[-6:] == [1]*6:
            fig.add_trace(go.Bar(
                x=da['data'], 
                y=da['Anomalia'], 
                name='Anomalias',
                yaxis='y2',
                opacity=0.5,
                marker=dict(color='green')
                ))

            #Setting layout of the figure
            fig.update_layout(#title= Coluna +' - Real versus Previsto', 
                            #xaxis_title='Data', 
                            #yaxis_title='Valor',
                            yaxis=dict(side='left',range=[y_min, y_max]),  # Primary y-axis
                            yaxis2=dict(side='right', overlaying='y', range=[0, 4],showticklabels=False, showgrid=False),  # Secondary y-axis
                            legend=dict(
                                    orientation='h',
                                    x=0.5,
                                    y=-0.3,
                                    xanchor='center',
                                    yanchor='bottom'
                                    ),margin=dict(
                                    l=0,
                                    r=0,
                                    b=0, # ajuste o valor de acordo com o tamanho da legenda
                                    t=0,
                                    pad=0
                                ),
                                
                            width=1000)
        else:
            da['data']=da.index
            yreal=y
            if y_min<y_max:
                y_min = yreal.min()
                y_max =yreal.max()
            else:
                y_max = yreal.min()
                y_min =yreal.max()

            fig = go.Figure()
            
            
            # Adding traces for real values and predicted values
            fig.add_trace(go.Scatter(x=da['data'], y=yreal, name='Valores reais', mode='lines', connectgaps=False,yaxis='y'))
            fig.update_layout(
                            yaxis=dict(side='left',range=[y_min, y_max]),  # Primary y-axis
                            legend=dict(
                                    orientation='h',
                                    x=0.5,
                                    y=-0.3,
                                    xanchor='center',
                                    yanchor='bottom'
                                    ),margin=dict(
                                    l=0,
                                    r=0,
                                    b=0, # ajuste o valor de acordo com o tamanho da legenda
                                    t=0,
                                    pad=0
                                ),
                                
                            width=1000)

    except:
        da = pd.read_sql(consulta, cnxn)
        da['time'] = da['time'].str[0:16]
        da['vazio']=0
        yreal=da['vazio']
        da['data']=da.index
        fig = go.Figure()
            # Adding traces for real values and predicted values x=da['time'], y=yreal, name='Sem Valores', mode='lines', connectgaps=False,yaxis='y', color='red'
        fig.add_trace(go.Scatter())
        fig.update_layout(
                        yaxis=dict(side='left'),  # Primary y-axis
                        legend=dict(
                                orientation='h',
                                x=0.5,
                                y=-0.3,
                                xanchor='center',
                                yanchor='bottom'
                                ),margin=dict(
                                l=0,
                                r=0,
                                b=0, # ajuste o valor de acordo com o tamanho da legenda
                                t=0,
                                pad=0
                            ),
                            
                        width=1000)
    

    return fig


