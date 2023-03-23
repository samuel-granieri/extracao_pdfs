#from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import re
import requests
import pandas as pd
import io
import camelot
import sys
import tkinter as tk
from tkinter import filedialog
import numpy as np
import PyPDF2


#pd.set_option('display.max_rows',1000)
#pd.set_option('display.max_columns',1000)

pd.options.mode.chained_assignment = None


#Adicione as URLs de extração:

url_carne = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\CARNE.pdf'
url_estocagem = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\ESTOCAGEM.pdf'
url_nao_comestivel = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\CARNE.pdf'
url_leite = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\NÃO COMESTÍVEL.pdf'
url_mel = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\MEL.pdf'
url_ovos = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\OVOS.pdf'
url_pescado = r'C:\Users\SamuelMartins\ABIEC\Fontes BI - Documentos\Estabelecimentos\PESCADO.pdf'


#Metodo para auxiliar na criação das colunas
   
def etl_dataframe(df):        
    
    #Ajustar logradouro
    list_caracteres = [';', '/']
    
    def replace_list_caracteres(x):
        for item in list_caracteres:
            if item in x:
                x = x.replace(item, '')
            else:
                x
        return x
            
    df[2] = df[2].apply(lambda x: replace_list_caracteres(x))
    
    #Ajustar coluna UF
    df[0] = df[0].apply(str)
    df['UF'] = df[0].apply(lambda x: x.replace('UF :', '') if 'UF :' in x else np.nan).ffill().bfill()
    df[0] = df[0].apply(lambda x: 'UF :' if 'UF :' in x else x)
    
        
    #Ajustar coluna Área
    df['Área'] = df[0].apply(lambda x: x.replace('Área :', '') if 'Área :' in x else np.nan).ffill().bfill()
    df[0] = df[0].apply(lambda x: 'Área :' if 'Área :' in x else x)
    
    #Ajustar coluna Categoria
    df['Categoria'] = df[0].apply(lambda x: x.replace('Categoria :', '') if 'Categoria :' in x else np.nan).ffill().bfill()
    df[0] = df[0].apply(lambda x: 'Categoria :' if 'Categoria :' in x else x)
    
    #Ajustar coluna Classe
    df['Classe'] = df[0].apply(lambda x: x.replace('Classe :', '') if 'Classe :' in x else np.nan).ffill().bfill()
    df[0] = df[0].apply(lambda x: 'Classe :' if 'Classe :' in x else x)
    
    #Ajustar coluna Municipio
    df['Município'] = df[2].replace('',np.nan).ffill().bfill()
    df[2] = df['Município']
    del df['Município']

    #Filtrar df
    list_filter = ['UF :', 'Área :', 'Categoria :', 'Classe :']        
    
    df['Excluir'] = df[0].apply(lambda x: 'Sim' if x in list_filter else 'Não')
    df = df[df['Excluir'].isin(['Não'])]
        
    df['Excluir'] = df[0].apply(lambda x: 'Sim' if 'Total de Estabelecimentos' in x else 'Não')
    df = df[df['Excluir'].isin(['Não'])]
    del df['Excluir']

    
    numbers = ['0','1','2','3','4','5','6','7','8','9']
    
    def identifica_sif(x):
        sif =''
    
        if 'Processo nº' in x:
            i = x.find('º')
            s = x[i+1:i+22]
            x = x.replace(s,'')
            
        for item in x[-4:]:
            if item in numbers:
                sif = sif + item               
                    
        return sif
    
    #Separar coluna SIF
    df['SIF'] = df[0].apply(lambda x: identifica_sif(x))
    df['SIF'] = df['SIF'].replace('',np.nan).ffill()

    
    #Ajustar coluna Razao Social
    df[0] = df[0].replace('nan',np.nan).ffill()
    
    #reset index
    df.reset_index(drop=True, inplace=True)
    
    #Ajustar logradouro e razao social
    i=0
    while i < len(df):
        
        if i + 1 < len(df):

            #Logradouro
            if df.at[i, 'SIF'] == df.at[i+1, 'SIF']:
                df.loc[i, 1] = df.at[i, 1] + ' ' + df.at[i+1, 1]
                df.loc[i+1, 1] = df.at[i, 1]
            #Razao social   
            if df.at[i, 'SIF'] == df.at[i+1, 'SIF']:
                df.loc[i, 0] = df.at[i, 0] + ' ' + df.at[i+1, 0]
                df.loc[i+1, 0] = df.at[i, 0]
            
            i = i + 1
        else:
            break

    #Renomear colunas
    df.columns = ['Razão Social', 'Logradouro', 'Município', 'UF', 'Área', 'Categoria', 'Classe', 'SIF']
    
    #ajustar ordem sif
    df.insert(0, 'SIF', df.pop('SIF'))
    
    #remover duplicados
    df = df.drop_duplicates(keep='first', subset=['SIF', 'Razão Social', 'Logradouro', 'Município', 'UF', 'Área', 'Categoria', 'Classe'])
    
    #Remover numero SIF da razao social
    def ajustar_razao_social(x):
        for item in df['SIF']:
            item = str(item)         
            if item in x:
                x = x.replace(item,'')                
        return x
        
    
    df['Razão Social'] = df['Razão Social'].apply(lambda x: ajustar_razao_social(x))
    
    #Ajustar caracteres SIF
    def ajustar_sif(x):
        if len(x) == 1:
            x = '000' + x
        elif len(x) == 2:
            x = '00' + x
        elif len(x) == 3:
            x = '0' + x
        return x
        
    
    df['SIF'] = df['SIF'].apply(lambda x: ajustar_sif(x))

    return df
    
#Entrada de dados
list_pdfs = [
url_carne,
url_estocagem,
url_nao_comestivel,
url_leite,
url_mel,
url_ovos,
url_pescado
]

list_dfs = []

tables = ''

for item in list_pdfs:
    
    list_tables =[]
    
    #Pegar qtd de paginas
    file_pdf = open(item, 'rb')
    readpdf = PyPDF2.PdfFileReader(file_pdf)
    totalpages = readpdf.numPages
    
    contador = 0
    for page in range(1,totalpages):
    
    
        try:
            tables = camelot.read_pdf(item, 
                                    flavor='stream',
                                    table_areas=['0,515,760,70'],
                                    #columns=['28,42,58,370,615'],
                                    columns=['370, 615'],
                                    row_tol=10,
                                    strip_text=';\n',
                                    split_text=True,
                                    pages=str(page))
                                    
            
        except:
            tables = camelot.read_pdf(item, 
                                    flavor='stream',
                                    columns=['370, 615'],
                                    row_tol=10,
                                    strip_text=';\n',
                                    split_text=True,
                                    pages=str(page))
                                   
    
        df = pd.DataFrame()
        for table in tables:
            df_atual = table.df.copy()
            df_atual[0] = df_atual[0].replace('',np.nan)
            #Checar pagina é valida
            if len(df_atual.index) > 1 and df_atual[0].isnull().all() == False:
                df_atual = etl_dataframe(df_atual)
                list_dfs.append(df_atual)
                contador = contador + 1
                print('Página ' + str(contador) + ' processada com sucesso!\n')
                
            else:
                continue
        
      
    print('Arquivo ' + str(item) + ' processado com sucesso!\n')


df_geral = pd.concat(list_dfs)
#remover duplicados
df_geral = df_geral.drop_duplicates(keep='first', subset=['SIF', 'Razão Social', 'Logradouro', 'Município', 'UF', 'Área', 'Categoria', 'Classe'])
df_geral.to_csv(r'estabelecimentos_sif.csv', sep='|', encoding='utf-8-sig', index=False)
print('\nFinalizado com sucesso!')
