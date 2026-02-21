# MyNote! v1.5 
# Bloco de notas em Python (Tkinter)
# Funcionalidades:
# - Abas múltiplas
# - Autosave
# - Busca de texto
# - Zoom
# - Contador de linhas, palavras e caracteres
# - Atalhos básicos

# - Desenvolvedor: Vicente Bajay ( ViquinhoDev )

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import os

AUTOSAVE_INTERVAL = 30000  # 30 segundos

class MyNote:
    def __init__(self, root):
        self.root = root
        self.root.title("MyNote! v1.5")
        self.root.geometry("900x550")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.status = tk.Label(root, anchor="w")
        self.status.pack(fill="x")

        self.create_menu()
        self.bind_shortcuts()

        self.new_tab()
        self.update_status()
        self.autosave()

    # ---------- MENU ----------
    def create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nova aba", command=self.new_tab)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Salvar", command=self.save_file)
        file_menu.add_command(label="Salvar como", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Desfazer", command=lambda: self.text().edit_undo())
        edit_menu.add_command(label="Refazer", command=lambda: self.text().edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Buscar", command=self.search_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Zoom +", command=lambda: self.zoom(1))
        edit_menu.add_command(label="Zoom -", command=lambda: self.zoom(-1))

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.about)

        menubar.add_cascade(label="Arquivo", menu=file_menu)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        self.root.config(menu=menubar)

    # ---------- SHORTCUTS ----------
    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_tab())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-f>", lambda e: self.search_text())

    # ---------- ABAS ----------
    def new_tab(self, content=""):
        frame = tk.Frame(self.notebook)
        text = ScrolledText(
            frame,
            wrap=tk.WORD,
            undo=True,
            font=("Arial", 11)
        )
        text.pack(expand=True, fill="both")
        text.insert(tk.END, content)

        text.bind("<<Modified>>", self.on_modified)

        frame.text = text
        frame.file_path = None
        frame.font_size = 11

        self.notebook.add(frame, text="Sem título")
        self.notebook.select(frame)

    def current_tab(self):
        return self.notebook.nametowidget(self.notebook.select())

    def text(self):
        return self.current_tab().text

    # ---------- ARQUIVOS ----------
    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.new_tab(f.read())
            tab = self.current_tab()
            tab.file_path = path
            self.notebook.tab(tab, text=os.path.basename(path))

    def save_file(self):
        tab = self.current_tab()
        if tab.file_path:
            with open(tab.file_path, "w", encoding="utf-8") as f:
                f.write(tab.text.get(1.0, tk.END))
        else:
            self.save_as()

    def save_as(self):
        tab = self.current_tab()
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt")]
        )
        if path:
            tab.file_path = path
            self.save_file()
            self.notebook.tab(tab, text=os.path.basename(path))

    # ---------- FUNCIONALIDADES ----------
    def search_text(self):
        query = simpledialog.askstring("Buscar", "Texto:")
        if not query:
            return

        self.text().tag_remove("search", "1.0", tk.END)
        idx = "1.0"
        while True:
            idx = self.text().search(query, idx, nocase=True, stopindex=tk.END)
            if not idx:
                break
            end = f"{idx}+{len(query)}c"
            self.text().tag_add("search", idx, end)
            idx = end

        self.text().tag_config("search", background="yellow")

    def zoom(self, delta):
        tab = self.current_tab()
        tab.font_size = max(8, tab.font_size + delta)
        tab.text.config(font=("Arial", tab.font_size))

    def autosave(self):
        for tab_id in self.notebook.tabs():
            tab = self.notebook.nametowidget(tab_id)
            if tab.file_path:
                with open(tab.file_path, "w", encoding="utf-8") as f:
                    f.write(tab.text.get(1.0, tk.END))
        self.root.after(AUTOSAVE_INTERVAL, self.autosave)

    def on_modified(self, event=None):
        self.update_status()
        self.text().edit_modified(False)

    def update_status(self):
        content = self.text().get(1.0, tk.END)
        lines = content.count("\n")
        words = len(content.split())
        chars = len(content) - 1
        self.status.config(
            text=f"Linhas: {lines} | Palavras: {words} | Caracteres: {chars}"
        )

    def about(self):
        messagebox.showinfo(
            "Sobre",
            "MyNote! v1.5\n\n"
            "• Abas múltiplas\n"
            "• Autosave\n"
            "• Busca de texto\n"
            "• Zoom\n"
            "• Contadores\n\n"
            "Python + Tkinter"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MyNote(root)
    root.mainloop()
