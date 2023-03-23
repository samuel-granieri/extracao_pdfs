import camelot as camelot
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from ast import literal_eval
import numpy as np
#import time
import sys
import os
import re

#pd.options.display.max_columns = None
pd.options.mode.chained_assignment = None

#Hora inicio
#start_time = time.perf_counter()

# Abrir windows explorer para selecionar pasta.
root = tk.Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()

i = 0
  
# Método para limpar cada dataframe
def clean_dataframe(new_df):
    
    # Gerar cabeçalho
    new_header = new_df.iloc[0]
    new_df = new_df[1:]
    new_df.columns = new_header
    new_df.reset_index(drop=True, inplace=True)
    
    #Delete first column
    new_df = new_df.iloc[:,1:]

    lista_areas = ['CARNE', 'ESTOCAGEM', 'LEITE', 'MEL', 'NÃO COMESTÍVEL', 'OVOS', 'PESCADO']

    for i in range(0, len(new_df)):
        if new_df.at[i, 'País'] == '' and new_df.at[i, 'Área'] != '' and new_df.at[i, 'Área'] not in lista_areas:
            new_df.at[i, 'País'] = new_df.at[i, 'Área']
            new_df.at[i, 'Área'] = ''
            

    #Preencher colunas
    new_df['País'] = new_df['País'].replace('', np.nan).ffill().bfill()
        
    new_df['Área'] = new_df['Área'].replace('', np.nan).ffill().bfill()
    
    new_df['S.I.F.'] = new_df['S.I.F.'].replace('', np.nan).ffill().bfill()
    
    new_df['UF'] = new_df['UF'].replace('', np.nan).ffill().bfill()
    
    new_df['Município'] = new_df['Município'].replace('', np.nan).ffill().bfill()

    #Deletar linhas vazias
    new_df = new_df.replace('', np.nan)
    new_df = new_df.dropna(axis=0, how='all', subset=['Estabelecimento', 'S.I.F.', 'UF', 'Município', 'Produto'])
    new_df.reset_index(drop=True, inplace=True)
    new_df = new_df.replace(np.nan,'')
    
    #Ajustar coluna Estabelecimento e Produto
    for i in range(0, len(new_df)):
        
        if i+1 < len(new_df):
            if new_df.at[i, 'S.I.F.'] == new_df.at[i+1, 'S.I.F.']:  
                new_df.loc[i+1, 'Estabelecimento'] = new_df.loc[i, 'Estabelecimento'] + ' ' + new_df.loc[i+1, 'Estabelecimento']
                new_df.loc[i+1, 'Produto'] = new_df.loc[i, 'Produto'] + ' ' + new_df.loc[i+1, 'Produto']
                
                
    for i in range(len(new_df)-1, 0, -1):
        if i-1 > 0:
            if new_df.at[i, 'S.I.F.'] == new_df.at[i-1, 'S.I.F.']:
                new_df.loc[i-1, 'Estabelecimento'] = new_df.loc[i, 'Estabelecimento']
                new_df.loc[i-1, 'Produto'] = new_df.loc[i, 'Produto'] 
    
            
    #Remover colunas vazias
    if '' in new_df.columns.values:
        del new_df['']
        
    
    #Renomear colunas
    new_df.columns = ['País', 'Área', 'Estabelecimento', 'SIF', 'UF', 'Município', 'Produto', 'Dt Validade', 'Dt. Suspensão']
    
    #Completar colunas
    new_df['Estabelecimento'] = new_df['Estabelecimento'].replace('', np.nan).ffill().bfill()
    new_df['Produto'] = new_df['Produto'].replace('', np.nan).ffill().bfill()
    
    #Remover espaços
    new_df['Estabelecimento'] =new_df['Estabelecimento'].apply(lambda x: x.strip().replace('  ',' '))
    new_df['Produto'] =new_df['Produto'].apply(lambda x: x.strip().replace('  ',' '))
    new_df['SIF'] =new_df['SIF'].apply(lambda x: x.strip().replace('  ',' '))
    
    #Remover duplicados(estocagem)
    new_df = new_df.drop_duplicates(keep='first', subset=['País', 'Área', 'Estabelecimento', 'SIF', 'UF', 'Município', 'Produto'])
    new_df.reset_index(drop=True, inplace=True)
    
    
    #Verificar produtos na lista
    lista_produtos = [
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (BOVÍDEO) (DHC)',
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (EQUÍDEO) (DHC)',
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (PESCADO) (DHC)',
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (SUÍDEO) (DHC)',
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (AVES) (DHC)',
        'PRODUTOS COMPOSTOS POR DIFERENTES CATEGORIAS DE PRODUTOS CÁRNEOS, ACRESCIDOS OU NÃO DE INGREDIENTES (DHC)',
        'MATÉRIA PRIMA PARA RAÇÃO ANIMAL OU PARA MORDEDORES / BRINQUEDOS PARA ANIMAIS DE COMPANHIA',
        'COMPOSTO DE PRODUTOS DAS ABELHAS COM ADIÇÃO DE INGREDIENTES NÃO APÍCOLAS (EM VOLUME)',
        'COMPOSTO DE PRODUTOS DAS ABELHAS COM ADIÇÃO DE INGREDIENTES NÃO APICOLAS (EM MASSA)',
        'PEIXE EM CONSERVA (ao natural, em óleos comestíveis, em azeite, molhos diversos)',
        'MORDEDORES/BRINQUEDOS PARA ANIMAIS DE COMPANHIA (''PET CHEWS'', ''PET TOYS'')',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (BOVÍDEO) (DHC)',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (EQUÍDEO) (DHC)',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (PESCADO) (DHC)',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (SUÍDEO) (DHC)',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (AVES) (DHC)',
        'MISTURA LÁCTEA DE CONCENTRADOS PROTEICOS DE LEITE E SORO DE LEITE EM PÓ',
        'PRODUTOS SUBMETIDOS AO TRATAMENTO TÉRMICO - PASTEURIZAÇÃO (OVOS) (DHC)',
        'PRODUTOS SUBMETIDOS AO TRATAMENTO TÉRMICO – DESIDRATAÇÃO (OVOS) (DHC)',
        'PRODUTOS CARNEOS TEMOPROCESSADOS CONSERVADOS A TEMPERATURA AMBIENTE',
        'CARNE MECANICAMENTE SEPARADA DE PEIXE TEMPERADA MOLDADA CONGELADA',
        'PRODUTOS PROCESSADOS TERMICAMENTE - ESTERILIZAÇÃO COMERCIAL (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (BOVÍDEO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (EQUÍDEO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (PESCADO) (DHC)',
        'CORTES TEMPERADOS EMPANADOS COZIDOS E CONGELADOS DE FRANGO (*)',
        'CORTES TEMPERADOS, COZIDOS, ASSADOS E CONGELADOS DE FRANGO (*)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (SUÍDEO) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (BOVÍDEO) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (COELHOS) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (PESCADO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (AVES) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (OVOS) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (EQUÍDEO) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (SUÍDEO) (DHC)',
        'COMPOSTOS APÍCOLAS COM ADIÇÃO DE INGREDIENTES NÃO APÍCOLAS',
        'COMPOSTOS DE PRODUTOS DAS ABELHAS (EM VOLUME) (MEL) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (AVES) (DHC)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (OVOS) (DHC)',
        'ALIMENTO A BASE DE LEITE CONCENTRADO COM GORDURA VEGETAL',
        'COMPOSTOS DE PRODUTOS DAS ABELHAS (EM MASSA) (MEL) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (BOVÍDEO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (PESCADO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (EQUÍDEO) (DHC)',
        'CARNE DE ANIMAIS DE CAÇA CRIADOS EM CATIVEIRO (CODORNA)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (SUÍDEO) (DHC)',
        'PRODUTO À BASE DE QUEIJO PROCESSADO E GORDURA VEGETAL',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (AVES) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO COCÇÃO (DHC)',
        'MATÉRIA PRIMA PARA FINS OPOTERÁPICOS E LABORATORIAIS',
        'PRODUTOS A BASE DE CARNE(HAMBURGER,QUIBE,ALMONDEGA)',
        'PRODUTOS NÃO SUBMETIDOS A TRATAMENTO TÉRMICO (DHC)',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (BOVÍDEO) (DHC)',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (EQUÍDEO) (DHC)',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (PESCADO) (DHC)',
        'COMPOSTOS À BASE DE EXTRATO DE CARNE BOVINA EM PÓ',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (COELHOS) (DHC)',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (SUÍDEO) (DHC)',
        'PRATO PRONTO A BASE DE MOLUSCO BIVALVE CONGELADO',
        'PRODUTOS LÁCTEOS PARCIALMENTE DESIDRATADOS (DHC)',
        'QUEIJOS DE MISTURA DE LEITES(VACA, CABRA,OVELHA)',
        'CARNE MECANICAMENTE SEPARADA CONGELADA DE PEIXE',
        'CARNE MECANICAMENTE SEPARADA CONGELADA DE SUINO',
        'COMP.ALIMENTARES A BASE DE MANTEIGA E MARGARINA',
        'LEITE PASTEURIZADO ENVASADO PARA CONSUMO DIRETO',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (BOVÍDEO) (DHC)',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (PESCADO) (DHC)',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (EQUÍDEO) (DHC)',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (AVES) (DHC)',
        'PEIXE CONGELADO (inteiro, eviscerado, pedaços)',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (SUÍDEO) (DHC)',
        'PRODUTOS SUBMETIDOS A TRATAMENTO TÉRMICO (DHC)',
        'CARNE MANUALMENTE SEPARADA CONGELADA DE PEIXE',
        'DERIVADOS DA PRÓPOLIS (EM VOLUME) (MEL) (DHC)',
        'PEIXE FRESCO (inteiro, eviscerado, em postas)',
        'COMPOSTO DE PRODUTOS DAS ABELHAS (EM VOLUME)',
        'DERIVADOS DA PRÓPOLIS (EM MASSA) (MEL) (DHC)',
        'ESTOCAGEM DE PRODUTOS DE ORIGEM ANIMAL (DHC)',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (AVES) (DHC)',
        'COMPOSTO DE PRODUTOS DAS ABELHAS (EM MASSA)',
        'CONCENTRADO PROTEICO DE SORO DE LEITE EM PO',
        'OVO INTEGRAL PASTEURIZADO CONGELADO COM SAL',
        'OVO INTEGRAL PASTEURIZADO RESFRIADO COM SAL',
        'PRODUTOS A BASE DE CARNE DE ANIMAIS DE CAÇA',
        'ALIMENTO A BASE DE LEITE E GORDURA VEGETAL',
        'DESPOJOS COMESTIVEIS DE BUBALINO IN NATURA',
        'GEMA DE OVO PASTEURIZADO RESFRIADO COM SAL',
        'GORDURA ANIDRA DE LEITE (BUTTER OIL) (DHC)',
        'MATÉRIA PRIMA PARA RAÇÃO ANIMAL (PET FOOD)',
        'PREPARADO LACTEO PARA ALIMENTAÇÃO INFANTIL',
        'PRODUTOS A BASE DE CARNE BOVINA(HAMBURGER)',
        'PRODUTOS LACTEOS PARCIALMENTE DESIDRATADOS',
        'HIDROLIZADO DE PROTEINAS DE SORO DE LEITE',
        'MOLDADO COZIDO CONGELADO A BASE DE SURIMI',
        'QUEIJOS DE BAIXA UMIDADE (LEITE DE CABRA)',
        'QUEIJOS DE ALTA UMIDADE (LEITE DE CABRA)',
        'ENVOLTÓRIO NATURAL SALGADO DE BOVINO (*)',
        'PRATO PRONTO CONGELADO A BASE DE PESCADO',
        'PRODUTOS LACTEOS PARA ALIMENTAÇÃO ANIMAL',
        'PRODUTOS COM ADIÇÃO DE INIBIDORES (DHC)',
        'ENVOLTÓRIO NATURAL SALGADO DE SUÍNO (*)',
        'WWWSORO DE LEITE EM PO(LANÇAREM 355010)',
        'DERIVADOS DE PÓLEN APÍCOLA (MEL) (DHC)',
        'GEMA PASTEURIZADA CONGELADA COM AÇÚCAR',
        'PRODUTOS COZIDOS E DEFUMADOS DE SUÍNOS',
        'CARNE MECANICAMENTE SEPARADA, DE AVES',
        'LEITE FERMENTADO TRATADO TERMICAMENTE',
        'OVO INTEGRAL PASTEURIZADO DESIDRATADO',
        'PRODUTOS INSTANTÂNEOS A BASE DE LEITE',
        'PRODUTOS PROCESSADOS DE CARNE DE AVES',
        'PRODUTOS SUBMETIDOS À HIDRÓLISE (DHC)',
        'SUBPRODUTOS NÃO COMESTIVEIS DE SUINOS',
        'CONCENTRADO EM PÓ DE CALCIO DO LEITE',
        'FARINHA DE PROTEINA ISOLADA DE SUINO',
        'MEL DE ABELHAS INDÍGENAS (MEL) (DHC)',
        'PRODUTOS A BASE DE QUEIJO PROCESSADO',
        'PRODUTOS EM NATUREZA (BOVÍDEO) (DHC)',
        'PRODUTOS EM NATUREZA (COELHOS) (DHC)',
        'PRODUTOS EM NATUREZA (EQUÍDEO) (DHC)',
        'PRODUTOS EM NATUREZA (PESCADO) (DHC)',
        'PRODUTOS INDUSTRIALIZADOS DE BOVINOS',
        'PRODUTOS LÁCTEOS ESTERILIZADOS (DHC)',
        'PRODUTOS LÁCTEOS PASTEURIZADOS (DHC)',
        'PRODUTOS NÃO COMESTÍVEIS-SUBPRODUTOS',
        'CREME DE LEITE CHANTILLY/ CHANTILLY',
        'CARNE MECANICAMENTE SEPARADA DE AVE',
        'CLARA DE OVO PASTEURIZADA RESFRIADA',
        'ENV. NAT. SALGADO DE BOVINO(TRIPAS)',
        'FARINHA DE CARNE E OSSOS DE BOVINOS',
        'GELÉIA REAL LIOFILIZADA (MEL) (DHC)',
        'GEMA PASTEURIZADA CONGELADA COM SAL',
        'MIÚDOS COZIDOS CONGELADOS DE BOVINO',
        'MIÚDOS COZIDOS RESFRIADOS DE BOVINO',
        'OVO INTEGRAL PASTEURIZADO CONGELADO',
        'OVO INTEGRAL PASTEURIZADO RESFRIADO',
        'PRODUTOS EM NATUREZA (SUÍDEO) (DHC)',
        'PRODUTOS INDUSTRIALIZADOS DE SUINOS',
        'PROTEÍNA HIDROLISADA DE LEITE EM PÓ',
        'QUEIJO CREMOSO C/OUTROS INGREIDENT.',
        'RESÍDUO DE PROCESSAMENTO DE PESCADO',
        'SORO DE LEITE CONCENTRADO RESFRIADO',
        'SORO DE LEITE EM PO DESMINERALIZADO',
        'SUBPRODUTOS NÃO COMESTIVEIS DE AVES',
        'CARNE CONGELADA DE BOVINO SEM OSSO',
        'CARNE COZIDA E CONGELADA DE BOVINO',
        'CARNE COZIDA E CONGELADA DE SUÍNOS',
        'CARNE RESFRIADA DE BOVINO SEM OSSO',
        'FARINHA DE CARNE E OSSOS DE SUÍNOS',
        'MASSA DE QUEIJO PRONTA PARA FONDUE',
        'PRODUTOS EM NATUREZA (OVINO) (DHC)',
        'PRODUTOS LÁCTEOS FERMENTADOS (DHC)',
        'PRODUTOS PRONTOS A BASE DE PESCADO',
        'CARNE DE BOVINO IN NATURA-MPP/IND',
        'ALBUMINA PASTEURIZADA DESIDRATADA',
        'CARNE COZIDA E CONGELADA DE OVINO',
        'DERIVADOS DA PRÓPOLIS (EM VOLUME)',
        'MANTEIGA DE PRIM. QUALIDADE S/SAL',
        'PRODUTOS CÁRNEOS INDUSTRIALIZADOS',
        'PRODUTOS EM NATUREZA (AVES) (DHC)',
        'PRODUTOS EM NATUREZA (OVOS) (DHC)',
        'PRODUTOS INDUSTRIALIZADOS DE AVES',
        'CARNE COZIDA E CONGELADA DE AVES',
        'DERIVADOS DA PRÓPOLIS (EM MASSA)',
        'ENV. NAT. SALG. DE SUINO (TRIPA)',
        'ESTOCAGEM DE PESCADO E DERIVADOS',
        'MISTURA DE LEITE EM PÓ E GLICOSE',
        'MOLUSCO BIVALVE COZIDO CONGELADO',
        'PRODUTOS A BASE DE CARNE DE AVES',
        'PRODUTOS LÁCTEOS PROTEICOS (DHC)',
        'QUEIJO COM LEITE DE CABRA E VACA',
        'CARNE CONGELADA DE SUINO C/OSSO',
        'CARNE CONGELADA DE SUINO S/OSSO',
        'CORTES CONGELADOS DE AVE (PERU)',
        'ESTOCAGEM DE CARNES E DERIVADOS',
        'GEMA DE OVO DESIDRATADA COM SAL',
        'MIUDO COZIDO CONGELADO DE SUINO',
        'PERMEADO DE SORO DE LEITE EM PÓ',
        'PRODUTOS A BASE DE CARNE BOVINA',
        'PRODUTOS LÁCTEOS FUNDIDOS (DHC)',
        'PRODUTOS PROTEICOS CONCENTRADOS',
        'CLARA PASTEURIZADA DESIDRATADA',
        'COMPOSTOS GORDUROSOS DE SUÍNOS',
        'ESTOCAGEM DE LEITE E DERIVADOS',
        'LEITE ESTERILIZADO AROMATIZADO',
        'LEITE PASTEURIZADO AROMATIZADO',
        'MISTURAS E PREPARAÇÕES ALIMENT',
        'PRODUTOS A BASE DE CARNE OVINA',
        'PRODUTOS A BASE DE CARNE SUINA',
        'PRODUTOS LACTEOS PASTEURIZADOS',
        'QUEIJO PROCESSADO PASTEURIZADO',
        'SORO FETAL DE BOVINO CONGELADO',
        'SUBPRODUTO GODUROSOS DE BOVINO',
        'PROTEINA CONCENTRADA DE LEITE',
        'CAMARAO SEM CABECAO CONGELADO',
        'CARNE CONGELADA DE AVE (PERU)',
        'CARNE FRESCA DE BOVINO S/OSSO',
        'GEMA PASTEURIZADA DESIDRATADA',
        'MANTEIGA PRIMEIRA QUAL. C/SAL',
        'MIUDOS SALGADOS DE SUINOS (*)',
        'PÓLEN DESIDRATADO (MEL) (DHC)',
        'PRODUTOS CARNEOS DESIDRATADOS',
        'PRODUTOS LÁCTEOS CONCENTRADOS',
        'CAMARAO DESCASCADO CONGELADO',
        'CARNE FRESCA DE AVE (FRANGO)',
        'CARNE TEMPERDA DE AVES(PERÚ)',
        'CARTILAGEM CONGELADA DE AVES',
        'CLARA PASTEURIZADA CONGELADA',
        'COLÁGENO HIDROLISADO LÍQUIDO',
        'CRUSTÁCEO DEFUMADO CONGELADO',
        'CRUSTÁCEO EMPANADO CONGELADO',
        'ESPETINHO DE CARNE DE BOVINO',
        'ESTOCAGEM DE MEL E DERIVADOS',
        'ESTOMAGO CONGELADO DE BOVINO',
        'LEITE CONCENTRADO INDUSTRIAL',
        'MISTURAS APÍCOLAS E VEGETAIS',
        'MOLUSCO CEFALÓPODE CONGELADO',
        'PRODUTOS LÁCTEOS EM PÓ (DHC)',
        'PRODUTOS LACTEOS FERMENTADOS',
        'QUEIJO CREMOSO(CREAM CHEESE)',
        'QUEIJO FRESCAL ULTRAFILTRADO',
        'QUEIJO TIPO PROVOLONE FRESCO',
        'QUEIJOS ULTRAFILTRADOS (DHC)',
        'MIÚDOS DE EQUIDEO IN NATURA',
        'CARNE DE BOVINO "IN NATURA"',
        'CERA DE ABELHAS (MEL) (DHC)',
        'COAGULANTE DE ORIGEM BOVINA',
        'CREME DE LEITE ESTERILIZADO',
        'CREME DE LEITE PASTEURIZADO',
        'ESPETINHO DE CARNE DE SUINO',
        'FARINHA DE CASCOS E CHIFRES',
        'FARINHA DE PENAS E VISCERAS',
        'FARINHA DE VÍSCERAS DE AVES',
        'GEMA PASTEURIZADA CONGELADA',
        'GEMA PASTEURIZADA RESFRIADA',
        'MIÚDO SALGADO SECO DE PEIXE',
        'MIÚDOS CONGELADOS DE BOVINO',
        'MIÚDOS RESFRIADOS DE BOVINO',
        'PRODUTOS DEFUMADOS DE SUINO',
        'PRODUTOS LÁCTEOS CRUS (DHC)',
        'QUEIJOS NÃO MATURADOS (DHC)',
        'CARNE DE EQUIDEO IN NATURA',
        'MIÚDOS DE BOVINO IN NATURA',
        'CARNE FRESCA DE AVE (PERU)',
        'CAUDA DE LAGOSTA CONGELADA',
        'COAGULANTE DE ORIGEM SUÍNA',
        'CRUSTÁCEO COZIDO CONGELADO',
        'CULTURA LACTEA LIOFILIZADA',
        'DERIVADOS DO PÓLEN APÍCOLA',
        'GORDURA CONGELADA DE SUINO',
        'GORDURA CONGELADA DE SUÍNO',
        'MIUDOS CONGELADOS DE SUINO',
        'MIUDOS SALGADOS DE BOVINOS',
        'MOLUSCO UNIVALVE CONGELADO',
        'PEIXE EVISCERADO CONGELADO',
        'PRODUTOS EM NATUREZA (DHC)',
        'PRODUTOS LACTEOS PROTEICOS',
        'PRODUTOS LÁCTEOS UHT (DHC)',
        'CARCAÇA DE AVES IN NATURA',
        'MIÚDOS DE OVINO IN NATURA',
        'MIÚDOS DE SUINO IN NATURA',
        'CARNE DE AVES LIOFILIZADA',
        'CARNE DESIDRATADA DE AVES',
        'CARNE TEMPERADA DE BOVINO',
        'CORTES TEMPERADOS DE AVES',
        'CREME DE LEITE EM AEROSOL',
        'ESPETINHO DE CARNE DE AVE',
        'GORDURA BOVINA COMESTIVEL',
        'MISTURAS LACTEAS COM CAFE',
        'MOLUSCO BIVALVE CONGELADO',
        'MOLUSCO CEFALÓPODE FRESCO',
        'OVO INTEGRAL PASTEURIZADO',
        'PEIXE CONGELADO EM POSTAS',
        'PEIXE TEMPERADO CONGELADO',
        'PÓLEN APÍCOLA DESIDRATADO',
        'PRATOS PRONTOS CONGELADOS',
        'PRODUTOS A BASE DE QUEIJO',
        'PRODUTOS CARNEOS DE SUINO',
        'PRODUTOS COZIDOS DE SUINO',
        'PRODUTOS DE ORIGEM ANIMAL',
        'PRODUTOS LACTEOS FUNDIDOS',
        'QUEIJO DE LEITE DE OVELHA',
        'TENDÃO BOVINO DESIDRATADO',
        'CARNE DE OVINO IN NATURA',
        'CARNE DE SUINO IN NATURA',
        'MIÚDOS DE AVES IN NATURA',
        'CARNE DE ANIMAIS DE CAÇA',
        'CARNE TEMPERADA DE SUÍNO',
        'COALHO  DE ORIGEM BOVINA',
        'COTA HILTON CARNE BOVINA',
        'FARINHA DE CARNE E OSSOS',
        'FARINHA DE PELE DE SUÍNO',
        'GORDURA DE PORCO EM RAMA',
        'GORDURA SUINA COMESTIVEL',
        'MIÚDO CONGELADO DE PEIXE',
        'MIÚDOS SALGADOS DE SUÍNO',
        'OVO INTEGRAL DESIDRATADO',
        'PEIXE DEFUMADO CONGELADO',
        'PEIXE EMPANADO CONGELADO',
        'PETISCOS DE QUEIJO (DHC)',
        'PRODUTOS A BASE DE CARNE',
        'PRODUTOS CÁRNEOS PRONTOS',
        'QUEIJO DE LEITE DE CABRA',
        'QUEIJO DE MASSA SEMIDURA',
        'QUEIJO MIMOLETE COMISSIE',
        'QUEIJOS DE MÉDIA UMIDADE',
        'SOBREMESAS LÁCTEAS (DHC)',
        'SÓLIDOS DE ORIGEM LÁCTEA',
        'CARNE DE AVES IN NATURA',
        'CARNE CONGELADA DE AVES',
        'CARNE RESFRIADA DE AVES',
        'CARNE SALGADA DE BOVINO',
        'CARNE TEMPERADA DE AVES',
        'FARINHA DE CARNE E OSSO',
        'FARINHA DE PELE DE AVES',
        'FILE DE PEIXE CONGELADO',
        'GELATINAS (PELE BOVINA)',
        'GELÉIA REAL (MEL) (DHC)',
        'GELEIA REAL LIOFILIZADA',
        'GELÉIA REAL LIOFILIZADA',
        'GORDURA ANIDRA DE LEITE',
        'MOLUSCO UNIVALVE FRESCO',
        'OUTROS PRODUTOS CARNEOS',
        'OUTROS PRODUTOS LACTEOS',
        'PEIXE EVISCERADO FRESCO',
        'PEIXE INTEIRO CONGELADO',
        'PELE CONGELADA DE PEIXE',
        'PELE CONGELADA DE SUÍNO',
        'PELE DE PEIXE CONGELADA',
        'PRODUTOS COZIDOS DE AVE',
        'PRODUTOS SUINOS COZIDOS',
        'QUEIJOS CURADOS RALADOS',
        'QUEIJOS DE ALTA UMIDADE',
        'QUEIJOS MATURADOS (DHC)',
        'SUBPRODUTOS COMESTÍVEIS',
        'CAMARAO FRESCO INTEIRO',
        'CARNE SALGADA DE SUINO',
        'CRUSTÁCEO SALGADO SECO',
        'EXTRATO DE CARNE EM PÓ',
        'FARINHAS LÁCTEAS (DHC)',
        'LEITE EM PO MODIFICADO',
        'PEIXE COZIDO CONGELADO',
        'PEIXE COZIDO RESFRIADO',
        'PELE CONGELADA DE AVES',
        'PELE SUINA DESIDRATADA',
        'PRODUTOS LÁCTEOS EM PÓ',
        'QUEIJO MINAS (FRESCAL)',
        'QUEIJO TIPO GORGONZOLA',
        'APITOXINA (MEL) (DHC)',
        'CARNE DE RÃ CONGELADA',
        'CARNE DE RÃ RESFRIADA',
        'CARNE MOIDA CONGELADA',
        'CASEINATO DE POTÁSSIO',
        'CRUSTÁCEO DESIDRATADO',
        'DERIVADOS DA PRÓPOLIS',
        'ESPETINHO DE LINGUIÇA',
        'LEITE CRU REFRIGERADO',
        'LEITE EM PO DESNATADO',
        'LEITE UHT AROMATIZADO',
        'LEITE UHT COM ADIÇÕES',
        'MIÚDO DE PEIXE FRESCO',
        'MIÚDO DE RÃ CONGELADO',
        'OVO LÍQUIDO CONGELADO',
        'PRODUTOS LACTEOS CRUS',
        'QUEIJO MINAS (PADRAO)',
        'QUEIJO PROCESSADO UHT',
        'QUEIJO TIPO PROVOLONE',
        'QUEIJOS MOFADOS (DHC)',
        'QUEIJOS NAO MATURADOS',
        'QUEIJOS RALADOS (DHC)',
        'SALSICHAS EM CONSERVA',
        'CARNE BOVINA SALGADA',
        'CARNE SUINA DEFUMADA',
        'ENVOLTORIOS NATURAIS',
        'FILE DE PEIXE FRESCO',
        'LEITE CONDENSADO UHT',
        'LEITE DE CABRA EM PÓ',
        'LEITE EM PO INTEGRAL',
        'LINGUICAS (FRESCAIS)',
        'MISTURA LÁCTEA (DHC)',
        'MISTURA LACTEA EM PO',
        'MOLHOS LÁCTEOS (DHC)',
        'MOLUSCO BIVALVE VIVO',
        'PEIXE FRESCO INTEIRO',
        'PELE DE RÃ RESFRIADA',
        'PRODUTOS LACTEOS UHT',
        'PRÓPOLIS (MEL) (DHC)',
        'QUEIJO DE MASSA DURA',
        'QUEIJO DE MASSA MOLE',
        'QUEIJO TIPO EMMENTAL',
        'SUBPRODUTOS DIVERSOS',
        'CASEINATO DE CALCIO',
        'CONSERVAS ENLATADAS',
        'CRUSTÁCEO CONGELADO',
        'EXTRATO DE PROPOLIS',
        'EXTRATO DE PRÓPOLIS',
        'GELATINA COMESTIVEL',
        'MIÚDO DE PEIXE SECO',
        'PREPARADOS DE CARNE',
        'QUEIJO GRANA PADANO',
        'QUEIJO PASTEURIZADO',
        'QUEIJO TIPO COTTAGE',
        'QUEIJO TIPO GRUYERE',
        'SORO DE LEITE EM PO',
        'CASEINATO DE SODIO',
        'CREME DE INDUSTRIA',
        'CREME DE LEITE UHT',
        'EPOA PESCADO (DHC)',
        'FARINHA DE PESCADO',
        'FIBRAS DE COLÁGENO',
        'LEITE ESTERILIZADO',
        'PELE DE RÃ SALGADA',
        'QUEIJO TIPO ESTEPE',
        'QUEIJO TIPO GRANNA',
        'SANGUE E DERIVADOS',
        'QUEIJOS SEMIDUROS',
        'BEBIDA LACTEA UHT',
        'CAMARAO CONGELADO',
        'CLARA DESIDRATADA',
        'CONSERVAS DE OVOS',
        'CRUSTÁCEO SALGADO',
        'EMBUTIDOS COZIDOS',
        'FARINHA DE SANGUE',
        'FORMULAS INFANTIS',
        'GELATINA DE PEIXE',
        'LEITE AROMATIZADO',
        'LEITE CONCENTRADO',
        'LINGUICAS DE AVES',
        'MISTURAS APÍCOLAS',
        'ÓLEO ÁCIDO DE AVE',
        'PEIXE EM CONSERVA',
        'PERMEADOS (LEITE)',
        'PÓLEN (MEL) (DHC)',
        'QUEIJO PROCESSADO',
        'QUEIJO TIPO GOUDA',
        'QUEIJOS MATURADOS',
        'REQUEIJAO CREMOSO',
        'REQUEIJÃO CREMOSO',
        'SALSICHAS DE AVES',
        'SOBREMESA LÁCTEA',
        'BILE CONCENTRADA',
        'CASEINATOS (DHC)',
        'COALHO DE OVINOS',
        'COALHO DE VITELO',
        'COMPOSTO APÍCOLA',
        'CRUSTÁCEO FRESCO',
        'EPOA CARNE (DHC)',
        'EPOA LEITE (DHC)',
        'EXTRATO DE CARNE',
        'FARINHA DE CARNE',
        'FARINHA DE PEIXE',
        'FARINHA DE PENAS',
        'FONDUE DE QUEIJO',
        'FRANGO CONGELADO',
        'FRANGO RESFRIADO',
        'GEMA DESIDRATADA',
        'LEITE CONDENSADO',
        'LEITE FERMENTADO',
        'LEITE GELIFICADO',
        'MARGARINAS (DHC)',
        'OVOS DESIDRATADO',
        'PÓS NUTRICIONAIS',
        'PRODUTOS LACTEOS',
        'QUEIJO BOTERKAAS',
        'QUEIJO DE COALHO',
        'QUEIJO MUSSARELA',
        'QUEIJO PROVOLONE',
        'QUEIJO TIPO EDAM',
        'SOBREMESA LACTEA',
        'COMPOSTO LACTEO',
        'CREME DE RICOTA',
        'EPOA OVOS (DHC)',
        'FARINHA DE OSSO',
        'LEITE EVAPORADO',
        'MANTEIGAS (DHC)',
        'PEIXE CONGELADO',
        'PERMEADOS (DHC)',
        'QUEIJO DO REINO',
        'QUEIJO EMMENTAL',
        'QUEIJO PARMESÃO',
        'QUEIJOS MOFADOS',
        'OVOS IN NATURA',
        'MISTURA LÁCTEA',
        'MIÚDOS DE AVES',
        'ALBUMINA EM PÓ',
        'CARNES PICADAS',
        'CASEÍNAS (DHC)',
        'CERA DE ABELHA',
        'CREME DE LEITE',
        'EPOA MEL (DHC)',
        'FARINHA LACTEA',
        'LEITELHO (DHC)',
        'LEITELHO EM PO',
        'MASSA COALHADA',
        'Mel (a granel)',
        'MEL DE ABELHAS',
        'MISTURA LACTEA',
        'PEIXE DEFUMADO',
        'PRATOS PRONTOS',
        'PROPOLIS BRUTA',
        'PUDIM DE LEITE',
        'QUEIJO CREMOSO',
        'QUEIJO FUNDIDO',
        'QUEIJOS MACIOS',
        'ALCOOL DE MEL',
        'BEBIDA LACTEA',
        'BEEF IN POUCH',
        'DOCE DE LEITE',
        'GORDURA DE LÃ',
        'LACTOSE (DHC)',
        'LACTOSE EM PÓ',
        'ÓLEO DE PEIXE',
        'PEPSINA SUÍNA',
        'PÓS ESPECIAIS',
        'QUEIJO FRESCO',
        'QUEIJO RALADO',
        'RICOTA FRESCA',
        'MOLHO LÁCTEO',
        'GRAXA BRANCA',
        'MOLHO LACTEO',
        'PEIXE FRESCO',
        'PRODUTOS UHT',
        'QUEIJO MINAS',
        'QUEIJO PRATO',
        'RICOTA (DHC)',
        'BANHA COMUM',
        'COURO SUINO',
        'GELEIA REAL',
        'JERKED BEEF',
        'LEITE EM PO',
        'OLEO DE AVE',
        'SEBO BOVINO',
        'BEEF JERKY',
        'BUTTER OIL',
        'GEMA EM PÓ',
        'APITOXINA',
        'CASEINATO',
        'GELATINAS',
        'LEITE UHT',
        'MARGARINA',
        'MEL (DHC)',
        'MEL EM PÓ',
        'OVO EM PÓ',
        'REQUEIJAO',
        'SALSICHAS',
        'MANTEIGA',
        'CASEINAS',
        'IOGURTES',
        'LEITELHO',
        'PROPOLIS',
        'PRÓPOLIS',
        'PURURUCA',
        'TORRESMO',
        'CHARQUE',
        'LACTOSE',
        'PET TOY',
        'QUEIJOS',
        'COALHO',
        'RICOTA',
        'TASAJO',
        'POLEN',
        'SEBO',
        'MEL'

    ]
    
    
    new_df['Produto'] = new_df['Produto'].replace('  ', '')
    
    
    for idx in range(0, len(new_df)):
        
        for produto in lista_produtos:
            
            # se produto entrou
            if produto in new_df.at[idx,'Produto']:
            
                #lê a lista ao contrario
                for j in range(len(lista_produtos)-1, 0, -1):
                    
                    produto_inverso = lista_produtos[j]

                    #verifica se existe algum produto "menor" que se encaixa dentro do maior e remove o menor da lista original
                    if produto_inverso in produto and len(produto_inverso) < len(produto):
                        lista_produtos.remove(produto_inverso)
                        
            
                str_produto = new_df.at[idx,'Produto']
                str_produto = str_produto.replace(produto, '#' + produto)
                new_df.loc[idx,'Produto'] = str_produto
                
                
    def checa_produto(p):
        if p[1] == '#':
            p = p[2: ]
        elif p[0] == '#':
            p = p[1: ]
        
        return p.replace('##','#')

            
            
    #Limpar primeiro caractere da coluna Produto
    new_df['Produto'] =  new_df['Produto'].apply(lambda x: checa_produto(x))
    
    
    #Remover duplicados
    new_df = new_df.drop_duplicates(keep='first', subset=['País', 'Área', 'Estabelecimento', 'SIF', 'UF', 'Município', 'Produto'])
    new_df.reset_index(drop=True, inplace=True)

    #Expandir coluna Produto
    new_df['Produto'] = new_df['Produto'].str.split('#')
    new_df =new_df.explode('Produto')
    new_df.reset_index(drop=True, inplace=True)
    
    
    #Deletar linhas vazias
    new_df = new_df.replace('', np.nan)
    new_df = new_df.dropna(axis=0, how='all', subset=['Produto'])
    new_df.reset_index(drop=True, inplace=True)
    new_df = new_df.replace(np.nan,'')
    
    #print(new_df)
    #new_df.to_csv(r'C:\Users\Luciana Brochmann\OneDrive - ABIEC\Área de Trabalho\Nova pasta\teste.csv', sep='|', encoding='utf-8-sig')
    #sys.exit()
    

    return new_df


# Leitura e tratamento de dados
all_tables = []
for file_item in os.listdir(folder_selected):
    f  = str(folder_selected) + '/' + str(file_item)
        
    # Checar se arquivo é válido
    if os.path.isfile(f):
        # Fazer leitura de cada PDF
        tables = camelot.read_pdf(f,
                        flavor='stream',
                        table_areas=['0, 510, 840, 30'],
                        columns=['4,30,62,230,268,299,408,629,649,759'],
                        #split_text=True,
                        strip_text="\n'",
                        pages='1-end'
                        #row_tol=10
                        )
        
        #camelot.plot(tables[1], kind='grid').show()
        #tb = tables[0].df.copy()
        #print(tb)
        #tk.mainloop()
        
        #sys.exit()
        
        lst_final = []
        
        num_tables = 0
        
        
        #produto = file_item[9:].replace('.pdf','')
        
        for table in tables:
            temp = table.df.copy()
            if len(temp) > 1:
                df = clean_dataframe(temp)
                num_tables = num_tables + 1
                lst_final.append(df)
                df_final = pd.concat(lst_final)
                #df_final = df_final.drop_duplicates(keep='first', subset=['País', 'Área', 'Estabelecimento', 'SIF', 'UF', 'Município', 'Produto'])
                print('Página ' + str(num_tables) + ' lida.')
                
                #output = r'C:\Users\Luciana Brochmann\ABIEC\Fontes BI - Documentos\Habilitação por área\saida/' + str(file_item).replace('.pdf','.csv')
                output = r'C:\Users\LucianaBrochmann\OneDrive - ABIEC\Documentos - Fontes BI\Habilitação por área\saida/' + str(file_item).replace('.pdf','.csv')
                df_final.to_csv(output, sep='|', encoding='utf-8-sig')
                 
        print('\nArquivo ' + file_item.replace('.pdf','') + ' processado!' )
            
            
            
        


print('\nArquivos extraídos com sucesso!')
#Hora fim
#end_time = time.perf_counter()
#resut = end_time - start_time
#print(str(resut))                    

        
      



        
        









