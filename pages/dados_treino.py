import pyodbc
import pandas as pd



def gerar_dados(ativo,dt_ini,dt_fim):

    '''with open("tags/"+ativo, 'r') as f:
        tag_list = [line.strip() for line in f]'''

    server = '10.8.100.69' 
    database = 'FST' 
    username = 'Spotfireread' 
    password = 'Consult@'  
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    query = "SELECT TAG FROM TB_TAGS where MODELO='"+str(ativo) +"'"
    df = pd.read_sql(query, cnxn)
    df['TAG'] = df['TAG'].str.strip()
    tag_list = df['TAG'].values.tolist()


    tags_string = ', '.join(f"''{tag}''" for tag in tag_list)

    consulta = f"""SELECT tag, time, value, pctgood 
    FROM OPENQUERY(TESTE_PI, 'SELECT tag, expr, filterexpr, filtersampletype, filtersampleinterval, timestep, time, calcbasis, value, pctgood 
    FROM piarchive..piavg 
    WHERE time BETWEEN CAST(''-7d'' AS DATETIME) AND CAST(''*'' AS DATETIME) 
    AND timestep = CAST(''1h'' AS TIME) 
    AND tag IN ({tags_string})') AS piavg
    """

    da = pd.read_sql(consulta, cnxn)
    da['time'] = da['time'].str[0:16]
    da = da.dropna(subset=['value'], axis=0)
    da = pd.pivot_table(data=da, index='time', columns='tag', values='value')
    da['data']=da.index
    da = da.dropna()
    return da

def gerar_dados1(ativo,dt_ini,dt_fim):

    '''with open("tags/"+ativo, 'r') as f:
        tag_list = [line.strip() for line in f]'''

    server = '10.8.100.69' 
    database = 'FST' 
    username = 'Spotfireread' 
    password = 'Consult@'  
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    query = "SELECT TAG FROM TB_TAGS where MODELO='"+str(ativo) +"'"
    df = pd.read_sql(query, cnxn)
    df['TAG'] = df['TAG'].str.strip()
    tag_list = df['TAG'].values.tolist()


    tags_string = ', '.join(f"''{tag}''" for tag in tag_list)

    consulta = f"""SELECT tag, time, value, pctgood 
    FROM OPENQUERY(TESTE_PI, 'SELECT tag, expr, filterexpr, filtersampletype, filtersampleinterval, timestep, time, calcbasis, value, pctgood 
    FROM piarchive..piavg 
    WHERE time BETWEEN CAST(''{dt_ini}'' AS DATETIME) AND CAST(''{dt_fim}'' AS DATETIME) 
    AND timestep = CAST(''1h'' AS TIME) 
    AND tag IN ({tags_string})') AS piavg
    """

    da = pd.read_sql(consulta, cnxn)
    da['time'] = da['time'].str[0:16]
    da = da.dropna(subset=['value'], axis=0)
    da = pd.pivot_table(data=da, index='time', columns='tag', values='value')
    da['data']=da.index
    da = da.dropna()
    return da
