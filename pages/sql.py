import pyodbc
import pandas as pd
import configparser

server = '10.8.100.69' 
database = 'FST' 
username = 'Spotfireread' 
password = 'Consult@'  
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
cnxn2 = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

# Areas

global df_area
query = "SELECT ID_AREA, AREA From TB_AREA"
df_area = pd.read_sql(query, cnxn)

