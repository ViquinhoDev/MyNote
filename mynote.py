import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


class MyNoteApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MyNote")
        self.root.geometry("900x600")

        self.current_file: Path | None = None

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        self.text = tk.Text(self.root, wrap="word", undo=True)
        self.text.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.text)
        scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Novo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar como...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.exit_app)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Desfazer", command=self.text.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refazer", command=self.text.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=lambda: self.text.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=lambda: self.text.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Colar", command=lambda: self.text.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_command(label="Selecionar tudo", command=self.select_all, accelerator="Ctrl+A")

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)

        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda _: self.new_file())
        self.root.bind("<Control-o>", lambda _: self.open_file())
        self.root.bind("<Control-s>", lambda _: self.save_file())
        self.root.bind("<Control-S>", lambda _: self.save_file_as())
        self.root.bind("<Control-a>", lambda _: self.select_all())

    def _has_unsaved_changes(self) -> bool:
        return self.text.edit_modified()

    def _confirm_discard_changes(self) -> bool:
        if not self._has_unsaved_changes():
            return True

        choice = messagebox.askyesnocancel(
            "Alterações não salvas",
            "Você deseja salvar as alterações antes de continuar?",
        )
        if choice is None:
            return False
        if choice:
            return self.save_file()
        return True

    def _update_title(self) -> None:
        file_name = self.current_file.name if self.current_file else "Sem título"
        self.root.title(f"MyNote - {file_name}")

    def new_file(self) -> bool:
        if not self._confirm_discard_changes():
            return False

        self.text.delete("1.0", tk.END)
        self.current_file = None
        self.text.edit_modified(False)
        self._update_title()
        return True

    def open_file(self) -> bool:
        if not self._confirm_discard_changes():
            return False

        file_path = filedialog.askopenfilename(
            title="Abrir arquivo",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return False

        path = Path(file_path)
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{error}")
            return False

        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.current_file = path
        self.text.edit_modified(False)
        self._update_title()
        return True

    def save_file(self) -> bool:
        if self.current_file is None:
            return self.save_file_as()

        try:
            self.current_file.write_text(self.text.get("1.0", tk.END), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{error}")
            return False

        self.text.edit_modified(False)
        self._update_title()
        return True

    def save_file_as(self) -> bool:
        file_path = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return False

        self.current_file = Path(file_path)
        return self.save_file()

    def select_all(self) -> None:
        self.text.tag_add("sel", "1.0", "end")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")

    def show_about(self) -> None:
        messagebox.showinfo("Sobre", "MyNote\nBloco de notas simples em Python com Tkinter.")

    def exit_app(self) -> None:
        if self._confirm_discard_changes():
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = MyNoteApp(root)
    app._update_title()
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()


if __name__ == "__main__":
    main()
