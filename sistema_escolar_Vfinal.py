from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import os


# BANCO DE DADOS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "sistema_escola.db")


def conectar():
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Erro de Conexão", str(e))
        raise


def criar_tabelas():
    try:
        conn = conectar()
        cur = conn.cursor()

        # Criar tabela alunos com todas as colunas
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos_temp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            nota_final REAL DEFAULT 0,
            media REAL DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Copiar dados da tabela antiga 
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alunos'")
        if cur.fetchone():
            cur.execute("PRAGMA table_info(alunos)")
            colunas = [row[1] for row in cur.fetchall()]
            
            if "nota_final" not in colunas or "media" not in colunas:
                # Migrar dados
                colunas_comuns = [c for c in colunas if c not in ['nota_final', 'media']]
                cols = ", ".join(colunas_comuns)
                cur.execute(f"INSERT INTO alunos_temp ({cols}) SELECT {cols} FROM alunos")
                cur.execute("DROP TABLE alunos")
                cur.execute("ALTER TABLE alunos_temp RENAME TO alunos")
                print("Migração da tabela alunos concluída!")
            else:
                cur.execute("DROP TABLE alunos_temp")
        else:
            cur.execute("ALTER TABLE alunos_temp RENAME TO alunos")

        # Tabela Professores
        cur.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT,
            cpf TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            disciplina TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        print("Banco de dados configurado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro no Banco", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# PALETA DE CORES 
# =========================
DARK_BG = "#0B1120"         
DARK_CARD = "#151E2E"       
DARK_INPUT = "#1E293B"      
DARK_BLUE = "#00B4D8"       
DARK_BLUE_HOVER = "#0096C7" 
DARK_TEXT = "#E2E8F0"       
DARK_BORDER = "#334155"     




# PLACEHOLDER DOS CAMPOS
# =========================
PLACEHOLDER_FG = "#94A3B8"


def adicionar_placeholder(entry, texto):
    entry.placeholder = texto
    entry.default_fg = DARK_TEXT

    def ao_entrar(event):
        if entry.get() == entry.placeholder:
            entry.delete(0, END)
            entry.config(fg=entry.default_fg)

    def ao_sair(event):
        if not entry.get().strip():
            entry.insert(0, entry.placeholder)
            entry.config(fg=PLACEHOLDER_FG)

    entry.insert(0, texto)
    entry.config(fg=PLACEHOLDER_FG)
    entry.bind("<FocusIn>", ao_entrar)
    entry.bind("<FocusOut>", ao_sair)


def valor_entry(entry):
    texto = entry.get().strip()
    if hasattr(entry, "placeholder") and texto == entry.placeholder:
        return ""
    return texto


def restaurar_placeholder(entry):
    entry.delete(0, END)
    if hasattr(entry, "placeholder"):
        entry.insert(0, entry.placeholder)
        entry.config(fg=PLACEHOLDER_FG)
    else:
        entry.config(fg=DARK_TEXT)


# FUNÇÕES AUXILIARES
# =========================

def limpar_campos(entries):
    for entry in entries:
        restaurar_placeholder(entry)


def selecionar_item(tree, entries):
    try:
        item = tree.focus()
        if not item:
            return

        valores = tree.item(item, "values")
        if not valores:
            return

    
        valores_sem_id = valores[1:]

        limpar_campos(entries)
        for i, entry in enumerate(entries):
            if i < len(valores_sem_id):
                entry.delete(0, END)
                entry.insert(0, valores_sem_id[i])
                entry.config(fg=DARK_TEXT)
    except Exception as e:
        print("Erro ao selecionar item:", e)


# CRUD ALUNOS 
# =========================

def cadastrar_aluno(entries, tree):
    nome = valor_entry(entries[0])   
    if not nome:
        messagebox.showwarning("Aviso", "Nome do aluno é obrigatório!")
        return

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO alunos (nome, data_nascimento, cpf, telefone, email)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            valor_entry(entries[1]),   # Data Nascimento
            valor_entry(entries[2]),   # CPF
            valor_entry(entries[3]),   # Telefone
            valor_entry(entries[4])    # Email
        ))
        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
        limpar_campos(entries)
        atualizar_tabela_alunos(tree)
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "CPF já cadastrado!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()

# CRUD PROFESSORES
# =========================

def cadastrar_professor(entries, tree):
    nome = valor_entry(entries[0])  
    if not nome:
        messagebox.showwarning("Aviso", "Nome do professor é obrigatório!")
        return

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO professores (nome, data_nascimento, cpf, telefone, email, disciplina)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nome,
            valor_entry(entries[1]),
            valor_entry(entries[2]),
            valor_entry(entries[3]),
            valor_entry(entries[4]),
            valor_entry(entries[5])
        ))
        conn.commit()
        messagebox.showinfo("Sucesso", "Professor cadastrado com sucesso!")
        limpar_campos(entries)
        atualizar_tabela_professores(tree)
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "CPF já cadastrado!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


def atualizar_tabela_professores(tree):
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT * FROM professores ORDER BY id")
        for row in cur.fetchall():
            tree.insert("", END, values=row)
    finally:
        if 'conn' in locals():
            conn.close()


# FUNÇÕES DA ABA DE NOTAS
# =========================

def carregar_alunos_combo(combo):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM alunos ORDER BY nome")
        combo["values"] = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(e)
    finally:
        if 'conn' in locals():
            conn.close()


def converter_nota(valor):
    valor = str(valor).strip().replace(",", ".")
    if not valor:
        return 0
    return float(valor)


def salvar_nota(combo, entry_nota, entry_media, tree_alunos=None):
    
    aluno_nome = combo.get().strip()
    if not aluno_nome:
        messagebox.showwarning("Aviso", "Selecione ou digite o nome do aluno!")
        return

    try:
        nota = converter_nota(valor_entry(entry_nota))
        media = converter_nota(valor_entry(entry_media))

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE alunos
            SET nota_final = ?, media = ?
            WHERE TRIM(nome) = TRIM(?) COLLATE NOCASE
        """, (nota, media, aluno_nome))

        if cur.rowcount == 0:
            messagebox.showwarning("Aviso", "Aluno não encontrado pelo nome informado!")
            return

        conn.commit()
        messagebox.showinfo("Sucesso", f"Notas atualizadas para: {aluno_nome}")
        restaurar_placeholder(entry_nota)
        restaurar_placeholder(entry_media)

        if tree_alunos is not None:
            atualizar_tabela_alunos(tree_alunos)

    except ValueError:
        messagebox.showerror("Erro", "Digite apenas números nas notas. Exemplo: 8.5 ou 8,5")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# INTERFACE GRÁFICA 
# =========================

def criar_interface():
    janela = Tk()
    janela.title("Sistema Escolar - 3 Interfaces")
    janela.geometry("1550x980")        
    janela.resizable(True, True)       
    janela.config(bg=DARK_BG)


    # ESTILO
    # =========================
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TNotebook", background=DARK_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=DARK_CARD, foreground=DARK_TEXT,
                    padding=[20, 12], font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", DARK_BLUE)],
              foreground=[("selected", "white")])

    # TÍTULO
    Label(janela, text="Sistema Escolar", font=("Segoe UI", 30, "bold"),
          bg=DARK_BG, fg=DARK_BLUE).pack(pady=(20, 10))

    Frame(janela, bg=DARK_BLUE, height=3).pack(fill="x", padx=450, pady=(0, 15))

    notebook = ttk.Notebook(janela)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # ===================== ABA 1: ALUNOS =====================
    frame_alunos = Frame(notebook, bg=DARK_BG)
    notebook.add(frame_alunos, text=" Cadastro de Alunos")

    frame_form_a = Frame(frame_alunos, bg=DARK_CARD, padx=35, pady=25,
                         highlightbackground=DARK_BORDER, highlightthickness=1)
    frame_form_a.pack(pady=10, fill="x", padx=25)

    labels_a = ["Nome", "Data Nascimento", "CPF", "Telefone", "Email"]
    placeholders_a = [
        "Digite o nome completo",
        "Ex: 10/05/2000",
        "Ex: 123.456.789-00",
        "Ex: (21) 99999-9999",
        "Ex: aluno@email.com"
    ]
    entries_a = []
    for i, texto in enumerate(labels_a):
        Label(frame_form_a, text=texto + ":", bg=DARK_CARD, fg=DARK_TEXT,
              font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=8, padx=(10,20))
        
        entry = Entry(frame_form_a, width=48, bg=DARK_INPUT, fg=DARK_TEXT,
                      font=("Segoe UI", 11), relief="flat", bd=8)
        entry.grid(row=i, column=1, pady=8, padx=10, ipady=4)
        adicionar_placeholder(entry, placeholders_a[i])
        entries_a.append(entry)

    # Botões
    btn_frame_a = Frame(frame_alunos, bg=DARK_BG)
    btn_frame_a.pack(pady=10)
    Button(btn_frame_a, text="Cadastrar", bg=DARK_BLUE, fg="white", width=15, height=2,
           command=lambda: (cadastrar_aluno(entries_a, tree_alunos), carregar_alunos_combo(combo_alunos))).grid(row=0, column=0, padx=5)
    Button(btn_frame_a, text="Atualizar", bg="#10B981", fg="white", width=15, height=2,
           command=lambda: (atualizar_aluno(entries_a, tree_alunos), carregar_alunos_combo(combo_alunos))).grid(row=0, column=1, padx=5)
    Button(btn_frame_a, text="Excluir", bg="#EF4444", fg="white", width=15, height=2,
           command=lambda: (excluir_aluno(entries_a, tree_alunos), carregar_alunos_combo(combo_alunos))).grid(row=0, column=2, padx=5)
    Button(btn_frame_a, text="Limpar", bg="#64748B", fg="white", width=12, height=2,
           command=lambda: limpar_campos(entries_a)).grid(row=0, column=3, padx=5)
    
    colunas_a = ["ID", "Nome", "Data Nascimento", "CPF", "Telefone", "Email", "Nota Final", "Média"]
    tree_alunos = ttk.Treeview(frame_alunos, columns=colunas_a, show="headings", height=9)
    for col in colunas_a:
        tree_alunos.heading(col, text=col)
        tree_alunos.column(col, width=135)
    tree_alunos.pack(fill="both", expand=True, padx=25, pady=10)

    tree_alunos.bind("<<TreeviewSelect>>", lambda e: selecionar_item(tree_alunos, entries_a))
    atualizar_tabela_alunos(tree_alunos)

       # ===================== ABA 2: PROFESSORES =====================
    frame_prof = Frame(notebook, bg=DARK_BG)
    notebook.add(frame_prof, text="Cadastro de Professores")

    # Formulário mais compacto
    frame_form_p = Frame(frame_prof, bg=DARK_CARD, padx=35, pady=20)
    frame_form_p.pack(pady=8, fill="x", padx=25)

    labels_p = ["Nome", "Data Nascimento", "CPF", "Telefone", "Email", "Disciplina"]
    placeholders_p = [
        "Digite o nome completo",
        "Ex: 10/05/1985",
        "Ex: 123.456.789-00",
        "Ex: (21) 99999-9999",
        "Ex: professor@email.com",
        "Ex: Matemática"
    ]
    entries_p = []
    for i, texto in enumerate(labels_p):
        Label(frame_form_p, text=texto + ":", bg=DARK_CARD, fg=DARK_TEXT,
              font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=6, padx=(10,20))
        
        entry = Entry(frame_form_p, width=48, bg=DARK_INPUT, fg=DARK_TEXT,
                      font=("Segoe UI", 11), relief="flat", bd=8)
        entry.grid(row=i, column=1, pady=6, padx=10, ipady=4)
        adicionar_placeholder(entry, placeholders_p[i])
        entries_p.append(entry)

    # Botões
    btn_frame_p = Frame(frame_prof, bg=DARK_BG)
    btn_frame_p.pack(pady=8)
    Button(btn_frame_p, text="Cadastrar", bg=DARK_BLUE, fg="white", width=15, height=2,
           command=lambda: cadastrar_professor(entries_p, tree_prof)).grid(row=0, column=0, padx=5)
    Button(btn_frame_p, text="Atualizar", bg="#10B981", fg="white", width=15, height=2,
           command=lambda: atualizar_professor(entries_p, tree_prof)).grid(row=0, column=1, padx=5)
    Button(btn_frame_p, text="Excluir", bg="#EF4444", fg="white", width=15, height=2,
           command=lambda: excluir_professor(entries_p, tree_prof)).grid(row=0, column=2, padx=5)
    Button(btn_frame_p, text="Limpar", bg="#64748B", fg="white", width=12, height=2,
           command=lambda: limpar_campos(entries_p)).grid(row=0, column=3, padx=5)

    # Tabela mais compacta
    colunas_p = ["ID", "Nome", "Data Nascimento", "CPF", "Telefone", "Email", "Disciplina"]
    tree_prof = ttk.Treeview(frame_prof, columns=colunas_p, show="headings", height=10)
    for col in colunas_p:
        tree_prof.heading(col, text=col)
        tree_prof.column(col, width=150)   # Aumentei um pouco a largura
    tree_prof.pack(fill="both", expand=True, padx=25, pady=8)

    tree_prof.bind("<<TreeviewSelect>>", lambda e: selecionar_item(tree_prof, entries_p))

    atualizar_tabela_professores(tree_prof)

    # ===================== ABA 3: NOTAS =====================
    frame_notas = Frame(notebook, bg=DARK_BG)
    notebook.add(frame_notas, text="Notas e Médias")

    Label(frame_notas, text="Gerenciamento de Notas e Médias", 
          font=("Segoe UI", 20, "bold"), bg=DARK_BG, fg=DARK_TEXT).pack(pady=25)

    frame_n = Frame(frame_notas, bg=DARK_CARD, padx=50, pady=35)
    frame_n.pack(pady=10, padx=30)

    Label(frame_n, text="Selecione o Aluno:", bg=DARK_CARD, fg=DARK_TEXT, 
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    combo_alunos = ttk.Combobox(frame_n, width=60, state="readonly", font=("Segoe UI", 11))
    combo_alunos.pack(pady=10)

    Label(frame_n, text="Nota Final:", bg=DARK_CARD, fg=DARK_TEXT, 
          font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20,5))
    entry_nota = Entry(frame_n, width=45, font=("Segoe UI", 12))
    entry_nota.pack(pady=8)
    adicionar_placeholder(entry_nota, "Ex: 8.5")

    Label(frame_n, text="Média Geral:", bg=DARK_CARD, fg=DARK_TEXT, 
          font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(15,5))
    entry_media = Entry(frame_n, width=45, font=("Segoe UI", 12))
    entry_media.pack(pady=8)
    adicionar_placeholder(entry_media, "Ex: 7.0")

    Button(frame_n, text="SALVAR NOTA E MÉDIA", bg=DARK_BLUE, fg="white", 
           font=("Segoe UI", 12, "bold"), width=30, height=2,
           command=lambda: salvar_nota(combo_alunos, entry_nota, entry_media, tree_alunos)).pack(pady=15)


    carregar_alunos_combo(combo_alunos)

    def ao_trocar_aba(event):
        aba_atual = notebook.tab(notebook.select(), "text")
        if "Notas" in aba_atual:
            carregar_alunos_combo(combo_alunos)

    notebook.bind("<<NotebookTabChanged>>", ao_trocar_aba)

    janela.mainloop()



# FUNÇÕES ALUNOS
# =========================

def atualizar_tabela_alunos(tree):
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, data_nascimento, cpf, telefone, email, 
                   nota_final, media 
            FROM alunos ORDER BY id
        """)
        for row in cur.fetchall():
            tree.insert("", END, values=row)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar alunos:\n{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


def atualizar_aluno(entries, tree):
    try:
        item = tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um aluno na tabela para atualizar!")
            return

        valores = tree.item(item, "values")
        nome_original = valores[1]

        nome = valor_entry(entries[0])
        if not nome:
            messagebox.showwarning("Aviso", "Nome é obrigatório!")
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE alunos
            SET nome = ?, data_nascimento = ?, cpf = ?, telefone = ?, email = ?
            WHERE TRIM(nome) = TRIM(?) COLLATE NOCASE
        """, (
            nome,
            valor_entry(entries[1]),
            valor_entry(entries[2]),
            valor_entry(entries[3]),
            valor_entry(entries[4]),
            nome_original
        ))
        if cur.rowcount == 0:
            messagebox.showwarning("Aviso", "Aluno não encontrado pelo nome selecionado!")
            return

        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso!")
        limpar_campos(entries)
        atualizar_tabela_alunos(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


def excluir_aluno(entries, tree):
    try:
        item = tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir!")
            return
        
        valores = tree.item(item, "values")
        nome = valores[1]

        if not messagebox.askyesno("Confirmar", f"Excluir o aluno {nome}?"):
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM alunos WHERE TRIM(nome) = TRIM(?) COLLATE NOCASE", (nome,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno excluído!")
        limpar_campos(entries)
        atualizar_tabela_alunos(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()



# FUNÇÕES DE PROFESSORES 
# =========================

def atualizar_professor(entries, tree):
    try:
        item = tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um professor na tabela para atualizar!")
            return

        valores = tree.item(item, "values")
        prof_id = valores[0]

        nome = valor_entry(entries[0])
        if not nome:
            messagebox.showwarning("Aviso", "Nome do professor é obrigatório!")
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE professores 
            SET nome = ?, data_nascimento = ?, cpf = ?, telefone = ?, email = ?, disciplina = ?
            WHERE id = ?
        """, (
            nome,
            valor_entry(entries[1]),
            valor_entry(entries[2]),
            valor_entry(entries[3]),
            valor_entry(entries[4]),
            valor_entry(entries[5]),
            prof_id
        ))
        conn.commit()
        messagebox.showinfo("Sucesso", "Professor atualizado com sucesso!")
        limpar_campos(entries)
        atualizar_tabela_professores(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


def excluir_professor(entries, tree):
    try:
        item = tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um professor para excluir!")
            return
        
        valores = tree.item(item, "values")
        prof_id = valores[0]
        nome = valores[1]

        if not messagebox.askyesno("Confirmar Exclusão", 
                f"Deseja realmente excluir o professor:\n\n{nome} ?"):
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM professores WHERE id = ?", (prof_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Professor excluído com sucesso!")
        limpar_campos(entries)
        atualizar_tabela_professores(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        if 'conn' in locals():
            conn.close()


# INICIALIZAÇÃO
# =========================

if __name__ == "__main__":
    criar_tabelas()
    criar_interface()