import pandas as pd
import mysql.connector
import decimal
import streamlit as st

def bd_phoenix(vw_name):
    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_recife'
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    request_name = f'SELECT * FROM {vw_name}'

    # Script MySql para requests
    cursor.execute(
        request_name
    )
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df

st.set_page_config(layout='wide')

if 'mapa_router' not in st.session_state:

    st.session_state.mapa_router = bd_phoenix('vw_router')

st.title('Conferência de Serviços - Recife')

st.divider()

row0 = st.columns(2)

with row0[0]:

    data_servicos = st.date_input('Data Serviços', value=None ,format='DD/MM/YYYY', key='data_servicos')

if data_servicos:

    df_in = st.session_state.mapa_router[(st.session_state.mapa_router['Data Execucao']==data_servicos) & 
                                         (st.session_state.mapa_router['Tipo de Servico']=='IN')].reset_index(drop=True)
    
    df_reservas_problemas = pd.DataFrame(columns=['Reserva'])

    for reserva in df_in['Reserva'].unique().tolist():

        df_reserva = st.session_state.mapa_router[st.session_state.mapa_router['Reserva']==reserva].reset_index(drop=True)

        if 'OUT' in df_reserva['Tipo de Servico'].unique().tolist():

            data_maxima = df_reserva['Data Execucao'].max()

            df_reserva_ult_dia = df_reserva[df_reserva['Data Execucao']==data_maxima].reset_index(drop=True)

            if (len(df_reserva_ult_dia)==1 and df_reserva_ult_dia.at[0, 'Tipo de Servico']!='OUT') or \
                (len(df_reserva_ult_dia)>1):

                df_reservas_problemas.loc[len(df_reservas_problemas)] = [reserva]

    if len(df_reservas_problemas)>0:

        with row0[1]:

            container_dataframe = st.container()

            container_dataframe.dataframe(df_reservas_problemas, hide_index=True, use_container_width=True)
