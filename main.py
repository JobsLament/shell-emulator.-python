import os
import zipfile
import sys


class ShellEmulator:
    def __init__(self, hostname, zip_path):
        self.hostname = hostname
        self.zip_path = zip_path
        self.virtual_fs = {}
        self.current_dir = "/"
        self.load_virtual_filesystem()

    def load_virtual_filesystem(self):
        # Extract the ZIP file to a temporary directory
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall("/tmp/vfs")
        self.virtual_fs = self.build_fs_structure("/tmp/vfs")

    def build_fs_structure(self, path):
        fs_structure = {}
        for dirpath, dirnames, filenames in os.walk(path):
            rel_path = os.path.relpath(dirpath, path)
            # Normalize root path to be "/"
            rel_path = "/" if rel_path == "." else f"/{rel_path}".replace("\\", "/")
            fs_structure[rel_path] = {
                "dirs": dirnames,
                "files": filenames
            }
        return fs_structure

    def list_directory(self):
        # List contents of the current directory
        contents = self.virtual_fs.get(self.current_dir, {})
        dirs = contents.get("dirs", [])
        files = contents.get("files", [])
        return dirs + files

    def change_directory(self, new_dir):
        # Replace backslashes with forward slashes for consistency
        new_dir = new_dir.replace('\\', '/')

        if new_dir == "..":
            if self.current_dir != "/":
                self.current_dir = os.path.dirname(self.current_dir.rstrip('/'))
                if not self.current_dir:
                    self.current_dir = "/"
        else:
            # Normalize new_dir to absolute path if necessary
            if not new_dir.startswith("/"):
                new_dir = os.path.normpath(os.path.join(self.current_dir, new_dir))
                new_dir = new_dir.replace("\\", "/")  # Ensure no backslashes
            if new_dir in self.virtual_fs:
                self.current_dir = new_dir
            else:
                return "No such directory."

    def who(self):
        return "Current user: User"

    def rev(self):
        return self.current_dir[::-1]

    def execute_command(self, command):
        # Normalize command by replacing backslashes
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

    def start(self):
        while True:
            command = input(f"{self.hostname}:{self.current_dir}$ ")
            output = self.execute_command(command)
            if output:
                print(output)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python shell_emulator.py <hostname> <zip_path>")
        sys.exit(1)

    hostname = sys.argv[1]
    zip_path = sys.argv[2]

    emulator = ShellEmulator(hostname, zip_path)
    emulator.start()
