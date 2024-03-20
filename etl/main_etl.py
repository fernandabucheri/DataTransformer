# main_etl.py
import pandas as pd 
from tkinter import messagebox
import os
from datetime import datetime


def strip_columns(df):
    df.columns = df.columns.str.strip()
    return df

def strip_data(df):
    for coluna in df.columns:
        try:
            df[coluna] = df[coluna].str.strip()
        except:
            pass
    return df 

def del_unnamed_cols(df):
    for coluna in df.columns:
        # Se o nome da coluna em letras minúsculas começar com "unnamed" e estiver vazia: deleta a coluna
        if coluna.lower().startswith('unnamed') and df[coluna].isna().all():
            df.drop(columns=coluna, inplace=True)
    return df

class ETLClass:
    def __init__(self, gui=None):
        self.gui = gui

    def set_gui(self, gui):
        self.gui = gui
    
    def extract_data(self):
        if self.gui.file_path:
            # Define o número de linhas a serem ignoradas no início do arquivo
            # Se o sinalizador 'skip_rows_flag' estiver desativado (False), define 'skiprows' como 0,
            # caso contrário, converte a string obtida de 'skip_rows' em uma lista de inteiros usando split(',') e map(int, ...),
            # e define 'skiprows' como essa lista
            skiprows = 0 if not self.gui.skip_rows_flag.get() else list(map(int, self.gui.skip_rows.get().split(',')))

            # Define o número de linhas a serem ignoradas no final do arquivo
            # Se o sinalizador 'exclude_rows_flag' estiver desativado (False), define 'skipfooter' como 0,
            # caso contrário, converte a string obtida de 'exclude_rows' em um número inteiro e define 'skipfooter' como esse número
            skipfooter = 0 if not self.gui.exclude_rows_flag.get() else int(self.gui.exclude_rows.get())

            # Verifica a extensão do arquivo carregado
            # Se for um arquivo Excel (extensão 'xlsx'), lê o arquivo usando pd.read_excel(),
            # usando os parâmetros 'skiprows' e 'skipfooter' para ignorar as linhas especificadas
            # Caso contrário, assume que é um arquivo CSV (ou outro tipo de arquivo de texto) e lê o arquivo usando pd.read_csv(),
            # usando o separador especificado em 'separator_var' e os parâmetros 'skiprows' e 'skipfooter'
            self.dataframe = pd.read_excel(self.gui.file_path, skiprows=skiprows, skipfooter=skipfooter) if self.gui.file_extension_var.get() == "xlsx" else pd.read_csv(self.gui.file_path, sep=self.gui.separator_var.get(), skiprows=skiprows, skipfooter=skipfooter, engine='python')

            # Formata
            self.dataframe = strip_columns(self.dataframe)
            self.dataframe = strip_data(self.dataframe)
            self.dataframe = del_unnamed_cols(self.dataframe)
            
            # Mostra as colunas na tela
            self.gui.display_columns()
            
            # Salva as variáveis utilizadas para salvar os arquivos finais
            self.nome_arq = self.gui.file_path.split('/')[-1].split('.')[0]
            self.extensao_arq = self.gui.file_path.split('/')[-1].split('.')[1]
        pass

    def transform_data(self):
        errors = []  # Inicializa uma lista para armazenar erros durante a transformação
        transformed_data = self.dataframe.copy()  # Cria uma cópia do DataFrame original para realizar a transformação sem alterá-lo

        # Loop sobre cada coluna e seu tipo selecionado pelo usuário
        for column, combobox in self.gui.column_types.items():
            column_type = combobox.get()  # Obtém o tipo selecionado para a coluna atual
            try:
                # Tentativa de transformar os dados com base no tipo selecionado
                if column_type == "Texto":
                    transformed_data[column] = transformed_data[column].astype(str)
                elif column_type == "Inteiro":
                    transformed_data[column] = pd.to_numeric(transformed_data[column], errors="coerce", downcast="integer")
                elif column_type == "Decimal":
                    transformed_data[column] = pd.to_numeric(transformed_data[column], errors="coerce", downcast="float")
                elif column_type == "Data":
                    try:
                        # Transforma a data usando format='mixed' para identificar diferentes formatos de datas
                        transformed_data[column] = pd.to_datetime(transformed_data[column], format='mixed').dt.strftime("%d/%m/%Y")
                    except Exception as e: 
                        # Caso de erro, salva no log e utiliza errors="coerce" que permite que valores inválidos sejam convertidos para NaT (Not a Time)    
                        errors.append(f"Erro na coluna {column}: {str(e)}")   
                        transformed_data[column] = pd.to_datetime(transformed_data[column], errors='coerce', format='mixed').dt.strftime("%d/%m/%Y")                            
            except Exception as e:
                # Em caso de erro, adiciona uma mensagem à lista de erros 
                errors.append(f"Erro na coluna {column}: {str(e)}")
        
        # Se houver erros, registra-os no log
        if errors:
            self.write_log(errors)

        # Salva o resultadp
        self.load_data(transformed_data)
        
    def load_data(self, transformed_data):
        try:
            # atualiza a hora no momento em que for gerar o resultado
            data = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            path_result = os.path.join(os.path.expanduser('~'), 'Downloads', f'{self.nome_arq}_transformed_{data}.{self.extensao_arq}')  # Determina o caminho e o nome do arquivo tratado
            
            # Verifica a extensão do arquivo carregado
            # Se for um arquivo Excel (extensão 'xlsx'), salva o resultado final usando pd.to_excel(),
            # Caso contrário, assume que é um arquivo CSV (ou outro tipo de arquivo de texto) e salva o resultado usando pd.to_csv(),
            if self.gui.file_extension_var.get() == "xlsx":
                transformed_data.to_excel(path_result, index=False)
            else: 
                transformed_data.to_csv(path_result, index=False)
                
            # Exibe uma mensagem informando que os dados foram transformados
            messagebox.showinfo("Sucesso", f"Dados Convertidos.") 
        except Exception as e:
            # Exibe uma mensagem informando ao usuário detalhes do erro, caso ocorra
            messagebox.showinfo("Erro", f"Ocorreu o erro : {str(e)}") 
        
        
    # Método para escrever os erros em um arquivo de log
    def write_log(self, errors):
        # atualiza a hora no momento em que for gerar o log
        data = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        log_path = os.path.join(os.path.expanduser('~'), 'Downloads', f'log_{self.nome_arq}_{data}.txt')  # Determina o caminho do arquivo de log
        with open(log_path, 'w') as f:  # Abre o arquivo de log em modo de escrita
            for error in errors:  # Loop sobre cada erro na lista de erros
                f.write(error + '\n')  # Escreve o erro no arquivo de log, seguido de uma quebra de linha
        messagebox.showinfo("Erro", f"Ocorreram erros na transformação. Detalhes foram salvos em {log_path}") # Exibe uma mensagem informando ao usuário onde os detalhes dos erros foram salvos
