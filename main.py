import os
import zipfile
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox

class ShellEmulator:
    def __init__(self, hostname, zip_path):
        self.hostname = hostname
        self.zip_path = zip_path
        self.virtual_fs = {}
        self.current_dir = "/"
        self.load_virtual_filesystem()

    def load_virtual_filesystem(self):
        # Проверяем, что ZIP-файл существует и является файлом
        if not os.path.isfile(self.zip_path):
            messagebox.showerror("Error", f"{self.zip_path} не является файлом.")
            sys.exit(1)

        # Извлекаем ZIP-файл во временную директорию
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall("/tmp/vfs")
        self.virtual_fs = self.build_fs_structure("/tmp/vfs")

    def build_fs_structure(self, path):
        fs_structure = {}
        for dirpath, dirnames, filenames in os.walk(path):
            rel_path = os.path.relpath(dirpath, path)
            rel_path = "/" if rel_path == "." else f"/{rel_path}".replace("\\", "/")
            fs_structure[rel_path] = {
                "dirs": dirnames,
                "files": filenames
            }
        return fs_structure

    def list_directory(self):
        contents = self.virtual_fs.get(self.current_dir, {})
        dirs = contents.get("dirs", [])
        files = contents.get("files", [])
        return dirs + files

    def change_directory(self, new_dir):
        new_dir = new_dir.replace('\\', '/')
        if new_dir == "..":
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir.rstrip('/'))
                if not self.current_dir:
                    self.current_dir = "/"
        else:
            if not new_dir.startswith("/"):
                new_dir = os.path.normpath(os.path.join(self.current_dir, new_dir))
                new_dir = new_dir.replace("\\", "/")
            if new_dir in self.virtual_fs:
                self.current_dir = new_dir
            else:
                return "No such directory."

    def who(self):
        return self.hostname

    def rev(self):
        return self.current_dir[::-1]

    def execute_command(self, command):
        command = command.replace('\\', '/')
        parts = command.strip().split()
        if not parts:
            return ""
        cmd = parts[0]

        if cmd == "ls":
            return "\n".join(self.list_directory())
        elif cmd == "cd":
            if len(parts) > 1:
                return self.change_directory(parts[1])
            else:
                return "No directory specified."
        elif cmd == "exit":
            sys.exit(0)
        elif cmd == "who":
            return self.who()
        elif cmd == "rev":
            return self.rev()
        else:
            return "Command not found."

class EmulatorGUI:
    def __init__(self, root, hostname, zip_path):
        self.emulator = ShellEmulator(hostname, zip_path)

        self.root = root
        self.root.title("Shell Emulator")
        
        self.output_text = scrolledtext.ScrolledText(root, state='disabled', width=80, height=20)
        self.output_text.pack(padx=10, pady=10)

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(root, textvariable=self.input_var, width=80)
        self.input_entry.pack(padx=10, pady=10)
        self.input_entry.bind('<Return>', self.execute_command)

    def execute_command(self, event):
        command = self.input_var.get()
        self.input_var.set("")  # Очистка ввода
        output = self.emulator.execute_command(command)

        self.output_text.configure(state='normal')  # Разрешить редактирование
        self.output_text.insert(tk.END, f"{self.emulator.hostname}:{self.emulator.current_dir}$ {command}\n")
        if output:
            self.output_text.insert(tk.END, output + "\n")
        self.output_text.configure(state='disabled')  
        self.output_text.see(tk.END)  

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <hostname> <zip_path>")
        sys.exit(1)

    hostname = sys.argv[1]  
    zip_path = sys.argv[2]

    root = tk.Tk()
    emulator_gui = EmulatorGUI(root, hostname, zip_path)
    root.mainloop()
