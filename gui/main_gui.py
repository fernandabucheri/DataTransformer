import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps


class GUIClass:
    def __init__(self, root, etl):
        self.root = root
        self.etl = etl  # Armazenar a instância de ETLClass
        
        self.root.geometry("705x907")
        self.root.title("Data Transformer")
        
        # Variáveis
        self.file_extension_var = tk.StringVar()
        self.separator_var = tk.StringVar()
        self.column_types = {}
        self.skip_rows_flag = tk.BooleanVar()
        self.skip_rows_flag.set(False)
        self.skip_rows = tk.StringVar()
        self.exclude_rows_flag = tk.BooleanVar()
        self.exclude_rows_flag.set(False)
        self.exclude_rows = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Título - Imagem
        img = Image.open('assets/logo.png')
        img = ImageTk.PhotoImage(img)
        image_label = ttk.Label(self.root, image=img, justify='center')
        image_label.image = img
        image_label.grid(row=0, column=0, columnspan=2, padx=(100, 20), pady=(20, 20))
        
        # Seleção de extensão de arquivo
        file_extension_label = ttk.Label(self.root, text="Selecione a extensão do arquivo:", font=("Helvetica", 12))
        file_extension_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        file_extension_combobox = ttk.Combobox(self.root, textvariable=self.file_extension_var, values=["xlsx", "csv", "txt"], state="readonly", font=("Helvetica", 12))
        file_extension_combobox.grid(row=1, column=1, sticky="w", padx=10, pady=20)
        file_extension_combobox.bind("<<ComboboxSelected>>", self.show_separator_entry)
        
        # Opção de pular linhas
        skip_rows_checkbutton = ttk.Checkbutton(self.root, text="Deseja pular linhas?", variable=self.skip_rows_flag, command=self.show_skip_rows_entry)
        skip_rows_checkbutton.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        # Opção de excluir linhas finais
        exclude_rows_checkbutton = ttk.Checkbutton(self.root, text="Deseja excluir linhas finais?", variable=self.exclude_rows_flag, command=self.show_exclude_rows_entry)
        exclude_rows_checkbutton.grid(row=5, column=0, sticky="w", padx=10, pady=5)
        
        # Botão para carregar arquivo
        load_button = ttk.Button(self.root, text="Carregar Arquivo", command=self.load_file, style="AccentButton")
        load_button.grid(row=7, column=0, columnspan=2, pady=20)
        
    def show_separator_entry(self, event):
        # Deleta os campos referentes ao separador (se houver)
        try: 
            self.separator_entry.destroy()
            self.separator_label.destroy()
        except:
            pass
        
        # Caso o tipo de arquivo necessite dos campos referentes ao separador, eles são criados
        if self.file_extension_var.get() in ["csv", "txt"]:
            self.separator_label = ttk.Label(self.root, text="Insira o separador:")
            self.separator_label.grid(row=2, column=0, sticky="w", padx=10, pady=(20, 5))
            
            self.separator_entry = ttk.Entry(self.root, textvariable=self.separator_var)
            self.separator_entry.grid(row=2, column=1, sticky="w", padx=10, pady=(20, 5))
           
    
    def show_skip_rows_entry(self):
        if self.skip_rows_flag.get():
            # Entrada para as linhas a serem puladas
            self.skip_rows_label = ttk.Label(self.root, text="Digite as linhas que deseja pular, começando em 0,\nseparando por vírgula (Ex: 0,1,2):")
            self.skip_rows_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
            
            self.skip_rows_entry = ttk.Entry(self.root, textvariable=self.skip_rows)
            self.skip_rows_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        else:
            try: 
                self.skip_rows_label.destroy()
                self.skip_rows_entry.destroy()
            except:
                pass
    
    def show_exclude_rows_entry(self):
        if self.exclude_rows_flag.get():
            # Entrada para a quantidade de linhas finais a serem excluídas
            self.exclude_rows_label = ttk.Label(self.root, text="Digite a quantidade de linhas finais que deseja pular (Ex: 1):")
            self.exclude_rows_label.grid(row=6, column=0, sticky="w", padx=10, pady=5)
            
            self.exclude_rows_entry = ttk.Entry(self.root, textvariable=self.exclude_rows)
            self.exclude_rows_entry.grid(row=6, column=1, sticky="w", padx=10, pady=5)
        else:
            try: 
                self.exclude_rows_label.destroy()
                self.exclude_rows_entry.destroy()
            except:
                pass
    
    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Arquivos suportados", "*.xlsx *.csv *.txt")])
        self.etl.extract_data()
        

    def display_columns(self):
        # Criar um frame para as colunas
        columns_frame = ttk.LabelFrame(self.root, text="Selecione o tipo")
        columns_frame.grid(row=8, column=0, pady=10, padx=10, sticky="we")
        
        canvas = tk.Canvas(columns_frame)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(columns_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 1))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        # Exibir colunas e suas comboboxes
        for idx, column in enumerate(self.etl.dataframe.columns):
            label = ttk.Label(inner_frame, text=column)
            label.grid(row=idx, column=0, sticky="w", padx=(10, 20), pady=5)
            combobox = ttk.Combobox(inner_frame, values=["Texto", 
                                                         "Inteiro", 
                                                         "Decimal", 
                                                         "Data"], state="readonly")
            combobox.grid(row=idx, column=1, sticky="w", padx=10, pady=5)
            self.column_types[column] = combobox
        
        inner_frame.update_idletasks()
        
        # Atualizar o tamanho do canvas
        canvas.config(scrollregion=canvas.bbox("all"))
    
        # Botão para transformar dados
        transform_button = ttk.Button(self.root, text="Transformar Dados", command=self.etl.transform_data, style="AccentButton")
        transform_button.grid(row=9, column=0, columnspan=2, pady=30)
