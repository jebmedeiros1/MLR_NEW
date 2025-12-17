import joblib
import pandas as pd
import numpy as np
import pyodbc
import datetime as dt
import schedule
import time
import configparser
import json
import cryptography.fernet as cripto
import logging

logging.basicConfig(filename='app2.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lendo o arquivo de configuração
config = configparser.ConfigParser()
config.read('config2.ini')

# Lendo o arquivo de configuração
parameters = configparser.ConfigParser()
parameters.read('parameters.ini')


server = config['DATABASE']['server']
database = config['DATABASE']['database']
username = config['DATABASE']['username']
password = config['DATABASE']['password']
driver = config['DATABASE']['driver']

# Conexão com o banco de dados
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
        return 0.

def maximohistorico(tag,modelo):
    consulta = f" SELECT max([VALUE]) as Maximo FROM [FST].[dbo].[TB_TRAIN] where  tag = '{tag}' and modelo = '{modelo}'  group by tag, modelo"
    dm = pd.read_sql(consulta, cnxn)
    return dm['Maximo'].iloc[-1]

def main():

        # Conexão com o banco de dados
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    cnxn2 = pyodbc.connect(connection_string)

    query = """ SELECT TAG, MODELO FROM TB_TAGS where MONITORADA='S' and modelo in( SELECT ID_MODELO 
                FROM TB_MODELO 
                where ATIVO =1) """
    df = pd.read_sql(query, cnxn)
    df['TAG'] = df['TAG'].str.strip()
    df['MODELO'] = df['MODELO'].str.strip()
    tag_list = df['TAG'].values.tolist()

    anomalias = []

    for index, row in df.iterrows():
        tag = row['TAG']
        modelo = row['MODELO']
        arquivo=modelo+tag
        print(modelo)
        try:
            model = joblib.load("models/" + arquivo + '.jet')
            query = "SELECT TAG FROM TB_TAGS where MODELO='"+str(modelo) +"'"
            da = pd.read_sql(query, cnxn)
            da['TAG'] = da['TAG'].str.strip()
            tag_list = da['TAG'].values.tolist()
            tags_string = ', '.join(f"''{tag_1}''" for tag_1 in tag_list)

            consulta = f"""SELECT tag, time, value, pctgood 
            FROM OPENQUERY(TESTE_PI, 'SELECT tag, expr, filterexpr, filtersampletype, filtersampleinterval, timestep, time, calcbasis, value, pctgood 
            FROM piarchive..piavg 
            WHERE time BETWEEN CAST(''-2h'' AS DATETIME) AND CAST(''*'' AS DATETIME) 
            AND timestep = CAST(''1h'' AS TIME) 
            AND tag IN ({tags_string})') AS piavg
            """
            
            #print(f"{tag} - {consulta}")

            df_pi = pd.read_sql(consulta, cnxn)
            df_pi = df_pi.dropna(subset=['value'], axis=0)
            tag_list2 = df_pi['tag'].values.tolist()
            tag_list2 = list(set(tag_list2))
            anomalias_df= pd.DataFrame()
            #anomalias_temp=pd.DataFrame()
            if all(item in tag_list2 for item in tag_list):
                df_pi['time'] = df_pi['time'].str[0:16]
                df_pi = df_pi.dropna(subset=['value'], axis=0)
                df_pi = pd.pivot_table(data=df_pi, index='time', columns='tag', values='value')
                df_pi
                X = df_pi.drop(tag, axis=1)
                y = df_pi[tag]

                predictions = model.predict(X)
                #threshold =int(parameters['PARAMETERS']['desvio'])/100
                residuals = y - predictions
                p_residuals = np.abs(residuals)/predictions
                
                
                #anomalies = np.where(p_residuals > threshold, 1, 0)
                #residuals = y - predictions
                try:
                 p_residuals = np.abs(residuals)/predictions
                except:
                 p_residuals=0

                threshold =  calcular_percentual(predictions.max())
                # Aqui nós verificamos duas condições:
                # 1. Se o valor real (y) é maior que maximohistorico.
                # 2. Se o valor percentual residual (p_residuals) é maior que o threshold.
                # Se qualquer uma das condições for verdadeira, anomalia será 1, caso contrário, será 0.
                #anomalies = np.where((y > maximohistorico(tag,modelo)) | (p_residuals > threshold), 1, 0)
                anomalies = np.where(p_residuals > threshold, 1, 0)

                delta_graf = residuals/predictions


                df_pi['Anomalia'] = anomalies
                df_pi[tag+'Prev'] = predictions
                df_pi['data'] = df_pi.index
                df_pi['data'] = pd.to_datetime(df_pi['data'])
                df_pi = df_pi.sort_values(by='data')
                df_pi['Delta'] = delta_graf*100
                yreal = y
                
                try:
                    consulta = f"SELECT tag, Valor fROM TB_CUTOVER Where Modelo='{modelo}'"
                    dc = pd.read_sql(consulta, cnxn)
                    cutover=dc['tag'].iloc[-1].strip()
                    cutvalue =  dc['Valor'].iloc[-1]
                    df_pi.loc[df_pi[cutover] < cutvalue, 'Anomalia'] = 0
                    #print(cutover)
                    #print(cutvalue)
                except:
                    a=1
                # Filtrar apenas registros com anomalia igual a 1
                if df_pi['Anomalia'].any() == 1:
                
                    anomalias_df['data'] = df_pi.loc[df_pi['Anomalia'] == 1, 'data'].copy()
                    anomalias_df['MODELO'] = modelo
                    anomalias_df['TAG'] = tag
                    anomalias_df['TIPO'] = 1
                    anomalias_df['Delta'] = df_pi.loc[df_pi['Anomalia'] == 1, 'Delta'].copy()
                    anomalias.append(anomalias_df[['data','MODELO', 'TAG','TIPO','Delta']])
            else:
                anomalias_temp = pd.DataFrame({
                'data': [dt.datetime.today()],
                'MODELO': [modelo],
                'TAG': [tag],
                'TIPO': [2],
                'Delta':[0]
                })
                anomalias.append(anomalias_temp[['data','MODELO', 'TAG','TIPO','Delta']])

            
        except FileNotFoundError:
            # Código para lidar com a falta do arquivo do modelo
            logging.error(f"Arquivo do modelo não encontrado para TAG: {tag}, MODELO: {modelo}")

    # Criar a tabela com registros de anomalias
    try:
        anomalias_table = pd.concat(anomalias)
        nome = pd.DataFrame(anomalias_table)
        cursor = cnxn.cursor()
        query = "Delete FROM TB_anomalias WHERE TIMESTAMP >= DATEADD(hour, -2, GETDATE())"
        cursor.execute(query)
        cnxn.commit()
        
        data = [tuple(row) for row in nome.itertuples(index=False)]
        query = 'INSERT INTO TB_anomalias (TIMESTAMP, MODELO, TAG, TIPO,Delta) VALUES (?, ?, ?,?,?)'
        cursor.executemany(query, data)
        cnxn.commit()
    except:
        anomalias_table=[]


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
if dt.datetime.strptime(license["expiration_date"],'%Y-%m-%d').date() < dt.datetime.today().date():
    # A licença está expirada
    print("Licença expirada"),
    print("A sua licença expirou em {}. Por favor, entre em contato com o suporte para obter uma nova licença.".format(license["expiration_date"])),

elif QTD_MODEL >= license["max_items"]:
    # A quantidade de itens excedeu o limite
        print("A quantidade de itens excedeu o limite permitido de {}. Por favor, entre em contato com o suporte para obter uma licença com um limite maior.".format(license["max_items"])),
else:
    # A aplicação pode ser executada
    main()
    schedule.every( int(config['AGENDA']['tempo'])).hours.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)