# importações

import joblib
import pandas as pd
from xgboost import *
import joblib
import pyodbc
import os


def treinar_modelo(ativo,perfil):

    driver = 'ODBC Driver 18 for SQL Server'
    server = '10.8.100.69' 
    database = 'FST' 
    username = 'Spotfireread' 
    password = 'Consult@'  
    #cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';TrustServerCertificate=Yes' )

    query = "SELECT distinct TAG FROM TB_TAGS where MONITORADA='S' AND MODELO='"+str(ativo) +"'"
    df = pd.read_sql(query, cnxn)
    df[df.columns] = df.apply(lambda x: x.str.strip())
    tag_list = df.to_dict('records')
    tag_list=df['TAG'].tolist()

    #df = listar valores do sql com perfil =  ao numero e modelo = id_modelo
    query = "SELECT [TAG] ,[TIMESTAMP] ,[VALUE] FROM TB_TRAIN where MODELO='"+str(ativo) +"' and PERFIL =" +str(perfil)
    df_dados = pd.read_sql(query, cnxn)
    df_dados['TAG'] = df_dados["TAG"].str.strip()
    df_dados = pd.pivot_table(data=df_dados, index='TIMESTAMP', columns='TAG', values='VALUE')
    df_dados = df_dados.dropna()


    for Coluna in tag_list:
        X = df_dados.drop(Coluna , axis=1)
        y = df_dados[Coluna]


        # Treino do Modelo 

        model = XGBRegressor(base_score=0.5, booster='gbtree', colsample_bylevel=1,
                colsample_bynode=1, colsample_bytree=1, enable_categorical=False,
                gamma=0, importance_type=None,
                interaction_constraints='', learning_rate=0.300000012,
                max_delta_step=0, max_depth=6, min_child_weight=1,
                monotone_constraints='()', n_estimators=100, n_jobs=16,
                num_parallel_tree=1,  random_state=0, reg_alpha=0,
                reg_lambda=1, scale_pos_weight=1, subsample=1, tree_method='exact',
                validate_parameters=1, verbosity=None)
        model.fit(X, y)

        # save the model to disk
        
        # Caminho do arquivo atual
        caminho_atual = os.getcwd()

        # Caminho da pasta "models"
        caminho_models = os.path.join(caminho_atual, 'models')
        
        filename = caminho_models+  '/'+ ativo+Coluna+'.jet'
        joblib.dump(model, filename)


    cursor = cnxn.cursor() 
    str1="UPDATE TB_MODELO SET ATIVO = 1 WHERE ID_MODELO ='"+ativo+"'"
    cursor.execute(str1)
    cnxn.commit()
   
    return model

