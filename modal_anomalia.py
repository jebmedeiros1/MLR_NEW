

from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from pages.dashboard import df_area
from dash import dash_table
import pandas as pd
from app import app
from pages.sql import cnxn
from dash.exceptions import PreventUpdate

col_centered_style={'display': 'flex', 'justify-content': 'center'}
existe_modelo=""
dados=[]
# ========= Layout ========= #
layout = dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Adicione Um Modelo")),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([
                        # Empresa
                        dbc.Label('Area', html_for='area_matriz'),
                        dcc.Dropdown(id='area_matriz', clearable=False, className='dbc',
                            options=[{'label': row['AREA'], 'value': row['ID_AREA']} for index, row in df_area.iterrows()]),
                        ]),
                    dbc.Col([
                        #Tag do equipamento
                        dbc.Label('Tag do Equipamento', html_for='modelo_matriz'),     
                        dbc.Input(id="input_modelo", placeholder="Nome do Modelo...", type="text")
                            ])     
                               
                        ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Descrição", html_for='input_desc'),
                        dbc.Textarea(id="input_desc", placeholder="Escreva aqui observações sobre o modelo...", style={'height': '80%'})], sm=12, md=8),
                    dbc.Col([
                        html.Br(),
                        html.Div(id='existe-modelo'),
                        html.Div(id='existe-modelo2'),
                        html.Button('Verificar', id='verificar_modelo', className='btn btn-primary mt-3',style={'height': '40%'})], sm=12, md=4)
                 ]),
                dbc.Row(html.Br()),
                dbc.Row([
                      dbc.Col([
                        html.Div([
                            dash_table.DataTable(
                                id='tabela_tags',
                                columns = [{"name": i, "id": i} for i in ['TAG', 'DESCRICAO', 'MODELO']],
                                editable=True,
                                #data=dados,
                                filter_action="native",
                                sort_action="native",
                                sort_mode="single",
                                page_size=50,
                                page_current=0
                            ),
                            html.Button('Adicionar Linha', id='add-row', className='btn btn-primary mt-3')
                        ], id='div_table'),
                    ]),
                    
                ]),
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="cancel_button", color="danger"),
                dbc.Button("Salvar", id="save_button", color="success"),
            ]),
        ], id="modal_modelos", size="lg", is_open=False)

# ====== Callbacks ======= #


    
@app.callback(
    Output('existe-modelo', 'children'),
    Output('tabela_tags','columns'),
    Output('tabela_tags','data'),
    Input('verificar_modelo', 'n_clicks'),
    Input('add-row', 'n_clicks'),
    State('input_modelo', 'value'),
    State('tabela_tags', 'data'))
def ex_modelo(n_clicks, n_linha, input_value,tabela):

    fase=ctx.triggered_id if not None else 'No clicks yet'

    if fase == 'add-row':
        new_row = {c['id']: '' for c in [{"name": i, "id": i} for i in ['TAG', 'DESCRICAO', 'MONITORADA']]}
        tabela.append({})
        columns = [{"name": i, "id": i} for i in ['TAG', 'DESCRICAO','MONITORADA']]
        return None, columns, tabela

    if not n_clicks:
        raise PreventUpdate

    cursor = cnxn.cursor()
    query = f"SELECT ID_MODELO From TB_MODELO where MODELO='{input_value}'"
    df = pd.read_sql(query, cnxn)

    if not df.empty:
        global dados
        existe_modelo = df['ID_MODELO'].iloc[-1]
        #tag1=existe_modelo.str
        #existe_modelo = 'AD0A0BEF-26F9-409D-85DF-D69BEB893751'
        query2 =f"SELECT [TAG], [DESCRICAO], [MONITORADA] From TB_TAGS where MODELO='{existe_modelo}'"
        da = pd.read_sql(query2, cnxn)
        da['TAG']=da['TAG'].str.strip()
        da['DESCRICAO']=da['DESCRICAO'].str.strip()
        da['MONITORADA']=da['MONITORADA'].str.strip()
        data =  da.to_dict('records')
        aviso = 'Modelo encontrado'
        global id_modelo 
        id_modelo = existe_modelo
    else:
        aviso = "Nome de modelo disponível"
        data =[{'TAG': '','DESCRICAO': '', 'MONITORADA': ''}]
        id_modelo = None
    # columns for the table

    columns = [{"name": i, "id": i} for i in ['TAG', 'DESCRICAO','MONITORADA']]

    return aviso, columns, data



@app.callback(Output('existe-modelo2', 'children'),
              Input('save_button','n_clicks'),
              State('tabela_tags', 'data'),
              State('area_matriz','value'),
              State('input_modelo','value'),
              State('input_desc', 'value'))

def tags_tabela(btn, dados,area,tag,ds_modelo):
        if not btn:
            raise PreventUpdate

        cursor = cnxn.cursor() 
        
        
        if id_modelo != None:
            
            cursor.execute("DELETE FROM TB_TAGS where MODELO='"+ id_modelo+ "'")
            df = pd.DataFrame(dados)
            for linha in df.itertuples(index=False):
                cursor.execute("INSERT INTO TB_TAGS (TAG,MODELO,MONITORADA, DESCRICAO) values(?,?,?,?)", (linha.TAG, id_modelo, linha.MONITORADA,  linha.DESCRICAO))
                cnxn.commit()
            return "Modelo alterado com sucesso"
            
            cursor.close()
        else:

            df = pd.DataFrame(dados)

            cursor.execute("INSERT INTO TB_MODELO (ID_MODELO, ID_AREA, MODELO, DS_MODELO) VALUES (newid(),?, ?, ?)", (area, tag, ds_modelo))
            #cnxn.commit()
            cursor.execute("SELECT ID_MODELO from TB_MODELO where  ID_AREA = ? and MODELO = ? and DS_MODELO = ?", (area, tag, ds_modelo))
            row = cursor.fetchone()
            if row:
                idmodelo = row.ID_MODELO
                aviso=idmodelo
                cursor.execute("DELETE FROM TB_TAGS where MODELO='"+ idmodelo+ "'")
                for linha in df.itertuples(index=False):
                    cursor.execute("INSERT INTO TB_TAGS (TAG,MODELO,MONITORADA, DESCRICAO) values(?,?,?,?)", (linha.TAG, idmodelo, linha.MONITORADA,  linha.DESCRICAO))
                    cnxn.commit()
                return "Modelo criado com sucesso"
            
            cursor.close()

            return aviso

