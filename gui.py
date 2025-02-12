import tkinter as tk
from tkinter import filedialog, messagebox

import os

theme_screen_colors = {"extract": {"bg": "Gold"}, "compress": {"bg": "Salmon1"}, "add": {"bg": "DodgerBlue2"},
                       "update": {"bg": "lightseagreen"}, "delete": {"bg": "Crimson"}}
theme_font_colors = {"extract": {"fg": "black"}, "compress": {"fg": "SteelBlue"}, "add": {"fg": "gold"},
                     "update": {"fg": "dark green"}, "delete": {"fg": "black"}}

font = {"font":("Arial",11, "bold")}


class CompressionScreen:
    """Class representing the compression screen of the GUI."""

    def show_frame(self):
        """Display the compression screen frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self):
        """Hide the compression screen frame."""
        self.frame.pack_forget()

    def show_byte_entry(self):
        """Display the byte entry field for certain compression algorithms."""
        self.label_byte_seq_len.pack()
        self.entery_byte_seq_len.pack()

    def hide_byte_entry(self):
        """Hide the byte entry field."""
        self.label_byte_seq_len.pack_forget()
        self.entery_byte_seq_len.pack_forget()

    def select_path_to_archive(self):
        """Open a dialog to select the path to the archive."""
        dir_name = filedialog.askdirectory(title="Select Directory")
        self.archive_path_label.configure(text=dir_name)

    def __init__(self, root):
        """Initialize the CompressionScreen."""
        self.frame = tk.Frame(root, **theme_screen_colors["compress"])
        self.dirs_to_compress = []
        self.files_to_compress = []

        # --- Compression Screen Elements ---

        # Archive File Name
        self.archive_name_label = tk.Label(self.frame, text="Archive file name:", **font)
        self.archive_name_label.pack()
        self.archive_name_entry = tk.Entry(self.frame, width=50, **font)
        self.archive_name_entry.pack(pady=(0, 10))

        # Path to Archive File
        self.enter_archive_path_label = tk.Label(self.frame, text="Select the path to the archive file:", **font)
        self.enter_archive_path_label.pack()
        self.archive_path_label = tk.Label(self.frame, text="", bg="white", width=80, **font)
        self.archive_path_label.pack()
        self.enter_archive_path_button = tk.Button(self.frame, text="Select path...",
                                                   command=self.select_path_to_archive, **font)
        self.enter_archive_path_button.pack(pady=(0, 10))

        # Compression Algorithm
        self.algo_label = tk.Label(self.frame, text="Compression Algorithm:", **font)
        self.algo_label.pack()
        self.algo_var = tk.StringVar(self.frame)
        self.algo_var.set("RLE")  # Set default algorithm
        self.rle_radio = tk.Radiobutton(self.frame, text="RLE", variable=self.algo_var, value="RLE",
                                        command=self.show_byte_entry, **font)
        self.rle_radio.pack()
        self.huffman_radio = tk.Radiobutton(self.frame, text="Huffman", variable=self.algo_var, value="HUFFMAN",
                                            command=self.hide_byte_entry, **font)
        self.huffman_radio.pack()
        self.byte_frame = tk.Frame(self.frame)
        self.label_byte_seq_len = tk.Label(self.byte_frame, text="Enter the number of bytes in a single unit:", **font,
                                           width=50)
        self.label_byte_seq_len.pack()
        self.entery_byte_seq_len = tk.Entry(self.byte_frame, **font, width=50)
        self.entery_byte_seq_len.pack()
        self.byte_frame.pack(pady=(0, 10))

        # Files to Compress
        self.enter_file_label = tk.Label(self.frame, text="Enter files to compress:", **font)
        self.enter_file_label.pack()
        self.file_label = tk.Label(self.frame, text="", bg="white", width=80, **font)
        self.file_label.pack()
        self.browse_button = tk.Button(self.frame, text="Add Files...", command=self.browse_files, **font)
        self.browse_button.pack(pady=(0, 10))

        # Directories to Compress
        self.enter_dir_label = tk.Label(self.frame, text="Add directories to compress:", **font)
        self.enter_dir_label.pack()
        self.dir_label = tk.Label(self.frame, text="", bg="white", width=80, **font)
        self.dir_label.pack()
        self.select_button = tk.Button(self.frame, text="Add Directories...", command=self.browse_dirs, **font)
        self.select_button.pack()

        # Compression Button
        self.compress_button = tk.Button(self.frame, text="Compress...", **font)
        self.compress_button.pack(pady=10)

        # Clear Button

        self.clear_button = tk.Button(self.frame, text="Clear..", command=self.clear_fields, borderwidth=4, **font)
        self.clear_button.pack()

        self.frame.pack(fill=tk.BOTH, expand=True)

    def clear_fields(self):
        """Clear all entry fields and reset variables."""
        self.dir_label.configure(text="")
        self.file_label.configure(text="")
        self.archive_path_label.configure(text="")
        self.dirs_to_compress = []
        self.files_to_compress = []
        self.archive_name_entry.delete(0, tk.END)
        self.entery_byte_seq_len.delete(0, tk.END)

    def has_only_files(self, folder_path):
        """Check if a directory contains only files and no subdirectories."""
        try:
            entries = os.listdir(folder_path)
            if not entries:
                return False
            return all(os.path.isfile(os.path.join(folder_path, entry)) for entry in entries)
        except FileNotFoundError:
            return False

    def valid_input(self):
        """Check if the provided input for compression is valid."""
        if self.archive_name_entry.get() == "":
            tk.messagebox.showerror("Not valid input", "no name was giving to the archive")
            return False

        if self.archive_path_label.cget("text") == "":
            tk.messagebox.showerror("Not valid input", "no path to archive was selected")
            return False

        if self.dirs_to_compress == [] and self.files_to_compress == []:
            tk.messagebox.showerror("Not valid input", "no files or directorys was selected")
            return False

        if self.algo_var.get()[:3] == "RLE" and self.entery_byte_seq_len.get() == "":
            tk.messagebox.showerror("Not valid input", "no specified byte sequence length was given")
            return False
        for dir in self.dirs_to_compress:
            if not self.has_only_files(dir):
                tk.messagebox.showerror("Not valid input", f"The directory {dir} has directorys in it:\n enter only "
                                                           f"directory with only files as sons")
                return False
        try:
            with open(self.archive_name_entry.get(), 'w'):
                pass
            os.remove(self.archive_name_entry.get())
        except OSError:
            tk.messagebox.showerror("Not valid input", "not valid archive name")
            return False

        return True

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def get_dir_name(self, file_path: str) -> str:
        """Get the directory name from a full file path."""
        return "/".join(file_path.split("/")[-2::])

    def browse_dirs(self):
        """Open a dialog to browse directories for compression."""
        dir_name = filedialog.askdirectory(title="Select Directory")
        if dir_name in self.dirs_to_compress:
            messagebox.showerror("Error", f"Directory {self.get_dir_name(dir_name)} was already selected")
        elif dir_name != "":
            self.dirs_to_compress.append(dir_name)
            current_dirs = self.dir_label.cget("text")
            self.dir_label.configure(text=current_dirs + self.get_dir_name(dir_name) + ", ")

    def browse_files(self):
        """Open a dialog to browse files for compression."""
        filenames = filedialog.askopenfilenames(title="Select Files to Compress")
        for file_name in filenames:
            if file_name in self.files_to_compress:
                messagebox.showerror("Error", f"file {self.get_filename(file_name)} was already selected")
            else:
                self.files_to_compress.append(file_name)
                current_dirs = self.file_label.cget("text")
                self.file_label.configure(text=current_dirs + self.get_filename(file_name) + ", ")

    def get_data(self):
        """Get the data entered in the compression screen."""
        if self.valid_input():
            return self.archive_path_label.cget("text") + "/" + self.archive_name_entry.get(), self.files_to_compress, {
                "encoding": self.algo_var.get()[:3],
                "dir": self.dirs_to_compress,
                "byte_seq_len": self.entery_byte_seq_len.get()}
        else:
            return None, {}


class ExtractScreen:
    """Class representing the extraction screen of the GUI."""

    def show_frame(self):
        """Display the extraction screen frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self):
        """Hide the extraction screen frame."""
        self.frame.pack_forget()

    def __init__(self, root):
        """Initialize the ExtractScreen."""
        self.frame = tk.Frame(root, **theme_screen_colors["extract"])

        self.select_extract_archive_label = tk.Label(self.frame, text="Select Archive File:", **font)
        self.select_extract_archive_label.pack()
        self.archive_file_path = ""
        self.extract_dir_path = ""
        self.archive_path_label = tk.Label(self.frame, width=50, **font)
        self.archive_path_label.pack()

        self.extract_archive_browse_button = tk.Button(self.frame, text="Browse...",
                                                       command=self.browse_extract_archive_file, **font)
        self.extract_archive_browse_button.pack(pady=(0, 10))

        self.select_extract_directory_label = tk.Label(self.frame, text="Select extract directory:", **font)
        self.select_extract_directory_label.pack()

        self.extract_directory_label = tk.Label(self.frame, width=50, **font)
        self.extract_directory_label.pack()

        self.extract_directory_button = tk.Button(self.frame, text="Browse...",
                                                  command=self.browse_extract_directory, **font)
        self.extract_directory_button.pack(pady=(0, 10))

        self.extract_button = tk.Button(self.frame, text="Extract", **font)
        self.extract_button.pack()

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_fields, width=15, **font)

        self.clear_button.pack(pady=10)

    def clear_fields(self):
        """Clear all entry fields and reset variables."""
        self.archive_path_label.configure(text="")
        self.extract_directory_label.configure(text="")
        self.archive_file_path = ""

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def browse_extract_archive_file(self):
        """Open a dialog to browse the archive file for extraction."""
        filename = filedialog.askopenfilename(
            title="Select The Archive File",
            filetypes=[("Binary Files", "*.bin")]
        )
        self.archive_file_path = filename
        self.archive_path_label.configure(text=self.get_filename(filename))

    def get_dir_name(self, file_path: str) -> str:
        """Get the directory name from a full file path."""
        return "/".join(file_path.split("/")[-2::])

    def browse_extract_directory(self):
        """Open a dialog to browse the directory for extraction."""
        dir_path = filedialog.askdirectory(title="Select Directory")
        self.extract_dir_path = dir_path
        self.extract_directory_label.configure(text=self.get_dir_name(dir_path))

    def is_valid_input(self):
        """Check if the provided input for extraction is valid."""
        if self.archive_file_path == "" or self.extract_dir_path == "":
            tk.messagebox.showerror("Not valid input", "no path was giving to the archive/the extract directory")
            return False

        if os.listdir(self.extract_dir_path) != []:
            tk.messagebox.showerror("Not valid input", "The extract directory should be empty, you can create a empty "
                                                       "directory in the file explorer")
            return False

        return True

    def get_data(self):
        """Get the data entered in the extraction screen."""
        if self.is_valid_input():
            return self.archive_file_path, self.extract_dir_path, {}
        return None, {}



class UpdateScreen:
    """Class representing the update screen of the GUI."""

    def browse_extract_archive_file(self):
        """Browse for the archive file to update."""
        filename = filedialog.askopenfilename(
            title="Select The Archive File",
            filetypes=[("Binary Files", "*.bin")]
        )
        self.archive_file_path = filename
        self.archive_path_label.configure(text=self.get_filename(filename))

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def show_frame(self):
        """Display the update screen frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self):
        """Hide the update screen frame."""
        self.frame.pack_forget()

    def get_dir_name(self, file_path: str) -> str:
        """Get the directory name from a full file path."""
        return "/".join(file_path.split("/")[-2::])

    def browse_dir(self):
        """Browse for the directory to update."""
        dir_path = filedialog.askdirectory(title="Select Directory")
        self.dir_entry.configure(text=self.get_dir_name(dir_path))
        self.dir_path = dir_path

    def browse_file(self):
        """Browse for the file to update."""
        file_path = filedialog.askopenfile(title="Select Directory").name
        self.file_entry.configure(text=self.get_filename(file_path))
        self.file_path = file_path

    def show_file_choice(self):
        """Display the file update options."""
        self.clear_button.pack_forget()
        self.update_button.pack_forget()
        self.enter_file_label.pack()
        self.file_entry.pack()
        self.browse_file_button.pack()

        self.enter_dir_label.pack_forget()
        self.dir_entry.pack_forget()
        self.browse_dir_button_button.pack_forget()
        self.update_button.pack()
        self.clear_button.pack(pady=10)

    def show_dir_choice(self):
        """Display the directory update options."""
        self.clear_button.pack_forget()
        self.update_button.pack_forget()

        self.enter_file_label.pack_forget()
        self.file_entry.pack_forget()
        self.browse_file_button.pack_forget()

        self.enter_dir_label.pack()
        self.dir_entry.pack()
        self.browse_dir_button_button.pack()
        self.update_button.pack()
        self.clear_button.pack(pady=10)

    def __init__(self, root):
        """Initialize the UpdateScreen."""
        self.frame = tk.Frame(root, **theme_screen_colors["update"])
        self.archive_file_path = ""
        self.dir_path = ""
        self.file_path = ""
        self.extract_archive_label = tk.Label(self.frame, text="Select Archive File:",**font)
        self.extract_archive_label.pack()

        self.archive_path_label = tk.Label(self.frame, width=50,**font)
        self.archive_path_label.pack()

        self.extract_archive_browse_button = tk.Button(self.frame, text="Browse...",
                                                       command=self.browse_extract_archive_file,**font)
        self.extract_archive_browse_button.pack(pady=(0, 10))

        self.algo_label = tk.Label(self.frame, text="Type of file to update:",**font)
        self.algo_label.pack()

        self.add_type_var = tk.StringVar(self.frame)
        self.add_type_var.set("FILE")  # Set default algorithm

        self.file_radio = tk.Radiobutton(self.frame, text="File", variable=self.add_type_var, value="FILE",
                                         command=self.show_file_choice,**font)
        self.file_radio.pack()

        self.dir_radio = tk.Radiobutton(self.frame, text="Directory", variable=self.add_type_var,
                                        value="DIR", command=self.show_dir_choice,**font)
        self.dir_radio.pack(pady=(0, 10))

        self.enter_file_label = tk.Label(self.frame, text="Enter file to update:",**font)
        self.enter_file_label.pack()
        self.selected_files = []  # List to store selected files
        self.file_entry = tk.Label(self.frame, width=50,**font)
        self.file_entry.pack()
        self.browse_file_button = tk.Button(self.frame, text="Select Files...", command=self.browse_file,**font)
        self.browse_file_button.pack()

        self.enter_dir_label = tk.Label(self.frame, text="Enter directory to update:",**font)
        self.enter_dir_label.pack_forget()
        self.selected_files = []  # List to store selected files
        self.dir_entry = tk.Label(self.frame, width=50)
        self.dir_entry.pack_forget()

        self.browse_dir_button_button = tk.Button(self.frame, text="Select Directories", command=self.browse_dir,**font)
        self.browse_dir_button_button.pack_forget()

        self.update_button = tk.Button(self.frame, text="update", command=self.show_frame,**font)
        self.update_button.pack(pady=10)

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_fields,width=15,**font)
        self.clear_button.pack(pady=10)

    def clear_fields(self):
        """Clear all entry fields and reset variables."""
        self.archive_path_label.configure(text="")
        self.dir_entry.configure(text="")
        self.file_entry.configure(text="")
        self.archive_file_path = ""
        self.dir_path= ""
        self.file_path=""

    def has_only_files(self, folder_path):
        """Checks if a directory contains only files and no subdirectories."""
        try:
            entries = os.listdir(folder_path)

            if not entries:
                return False

            return all(os.path.isfile(os.path.join(folder_path, entry)) for entry in entries)
        except FileNotFoundError:
            return False

    def is_valid_input(self):
        """Check if the provided input for update is valid."""
        if self.archive_file_path == "":
            tk.messagebox.showerror("Not valid input", "no path was giving to the archive")
            return False
        if self.add_type_var.get() == "FILE" and self.file_path == "":
            tk.messagebox.showerror("Not valid input", "no path was giving to the file")
            return False
        if self.add_type_var.get() == "DIR" and self.dir_path == "":
            tk.messagebox.showerror("Not valid input", "no path was giving to the directory")
            return False
        if not self.has_only_files(self.dir_path):
            tk.messagebox.showerror("Not valid input", f"The directory {self.dir_path} has directories in it:\n enter only "
                                                       f"directory with only files as sons")
            return False
        return True

    def get_data(self):
        """Get the data entered in the update screen."""
        if self.is_valid_input():
            if self.add_type_var.get() == "FILE":
                return self.archive_file_path, self.file_path, {}
            elif self.add_type_var.get() == "DIR":
                return self.archive_file_path, self.dir_path, {}
        return None, {}


class AddScreen:
    """Class representing the add screen of the GUI."""

    def browse_extract_archive_file(self):
        """Browse for the archive file to add."""
        filename = filedialog.askopenfilename(
            title="Select The Archive File",
            filetypes=[("Binary Files", "*.bin")]
        )
        self.archive_file_path = filename
        self.archive_path_label.configure(text=self.get_filename(filename))

    def show_frame(self):
        """Display the add screen frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self):
        """Hide the add screen frame."""
        self.frame.pack_forget()

    def get_dir_name(self, file_path: str) -> str:
        """Get the directory name from a full file path."""
        return "/".join(file_path.split("/")[-2::])

    def browse_dir(self):
        """Browse for the directory to add."""
        dir_path = filedialog.askdirectory(title="Select Directory")
        self.dir_entry.configure(text=self.get_dir_name(dir_path))
        self.dir_path = dir_path

    def browse_file(self):
        """Browse for the file to add."""
        file_path = filedialog.askopenfile(title="Select Directory").name
        self.file_entry.configure(text=self.get_filename(file_path))
        self.file_path = file_path

    def show_file_choice(self):
        """Display the file add options."""
        self.clear_button.pack_forget()
        self.add_button.pack_forget()
        self.enter_file_label.pack()
        self.file_entry.pack()
        self.browse_file_button.pack()

        self.enter_dir_label.pack_forget()
        self.dir_entry.pack_forget()
        self.browse_dir_button_button.pack_forget()
        self.add_button.pack()
        self.clear_button.pack(pady=10)

    def show_dir_choice(self):
        """Display the directory add options."""
        self.clear_button.pack_forget()
        self.add_button.pack_forget()

        self.enter_file_label.pack_forget()
        self.file_entry.pack_forget()
        self.browse_file_button.pack_forget()

        self.enter_dir_label.pack()
        self.dir_entry.pack()
        self.browse_dir_button_button.pack()
        self.add_button.pack()
        self.clear_button.pack(pady=10)

    def __init__(self, root):
        """Initialize the AddScreen."""
        self.frame = tk.Frame(root, **theme_screen_colors["add"])
        self.archive_file_path = ""
        self.dir_path = ""
        self.file_path = ""
        self.extract_archive_label = tk.Label(self.frame, text="Select Archive File:",**font)
        self.extract_archive_label.pack()

        self.archive_path_label = tk.Label(self.frame, width=50,**font)
        self.archive_path_label.pack()

        self.extract_archive_browse_button = tk.Button(self.frame, text="Browse...",
                                                       command=self.browse_extract_archive_file,**font)
        self.extract_archive_browse_button.pack(pady=(0, 10))

        self.algo_label = tk.Label(self.frame, text="Type of file to add:",**font)
        self.algo_label.pack()

        self.add_type_var = tk.StringVar(self.frame)
        self.add_type_var.set("FILE")  # Set default algorithm

        self.file_radio = tk.Radiobutton(self.frame, text="File", variable=self.add_type_var, value="FILE",
                                         command=self.show_file_choice,**font)
        self.file_radio.pack()

        self.dir_radio = tk.Radiobutton(self.frame, text="Directory", variable=self.add_type_var,
                                        value="DIR", command=self.show_dir_choice,**font)
        self.dir_radio.pack(pady=(0, 10))

        self.enter_file_label = tk.Label(self.frame, text="Enter file to add:",**font)
        self.enter_file_label.pack()
        self.selected_files = []  # List to store selected files
        self.file_entry = tk.Label(self.frame, width=50,**font)
        self.file_entry.pack()
        self.browse_file_button = tk.Button(self.frame, text="Select Files...", command=self.browse_file,**font)
        self.browse_file_button.pack()

        self.enter_dir_label = tk.Label(self.frame, text="Enter directory to add:",**font)
        self.enter_dir_label.pack_forget()
        self.selected_files = []  # List to store selected files
        self.dir_entry = tk.Label(self.frame, width=50,**font)
        self.dir_entry.pack_forget()

        self.browse_dir_button_button = tk.Button(self.frame, text="Select Directories", command=self.browse_dir,**font)
        self.browse_dir_button_button.pack_forget()

        self.add_button = tk.Button(self.frame, text="Add", command=self.show_frame,**font)
        self.add_button.pack(pady=10)

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_fields , width=15,**font)
        self.clear_button.pack(pady=10)

    def clear_fields(self):
        """Clear all entry fields and reset variables."""
        self.archive_path_label.configure(text="")
        self.dir_entry.configure(text="")
        self.file_entry.configure(text="")
        self.archive_file_path = ""
        self.dir_path = ""
        self.file_path = ""

    def has_only_files(self, folder_path):
        """Check if a directory contains only files and no subdirectories."""
        try:
            entries = os.listdir(folder_path)

            if not entries:
                return False

            return all(os.path.isfile(os.path.join(folder_path, entry)) for entry in entries)
        except FileNotFoundError:
            return False

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def is_valid_input(self):
        """Check if the provided input for add is valid."""
        if self.archive_file_path == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the archive")
            return False
        if self.add_type_var.get() == "FILE" and self.file_path == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the added file")
            return False
        if self.add_type_var.get() == "DIR" and self.dir_path == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the added directory")
            return False
        if self.add_type_var.get() == "DIR" and not self.has_only_files(self.dir_path):
            tk.messagebox.showerror("Not valid input", f"The directory {self.dir_path} contains subdirectories:\n"
                                                       f"Please enter only directories with only files as sons")
            return False
        return True

    def get_data(self):
        """Get the data entered in the add screen."""
        if self.is_valid_input():
            if self.add_type_var.get() == "FILE":
                return self.archive_file_path, self.file_path, {}
            elif self.add_type_var.get() == "DIR":
                return self.archive_file_path, self.dir_path, {}
        return None, {}


class DeleteScreen:
    """Class representing the delete screen of the GUI."""

    def browse_extract_archive_file(self):
        """Browse for the archive file to delete."""
        filename = filedialog.askopenfilename(
            title="Select The Archive File",
            filetypes=[("Binary Files", "*.bin")]
        )
        self.archive_file_path = filename
        self.archive_path_label.configure(text=self.get_filename(filename))

    def show_frame(self):
        """Display the delete screen frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self):
        """Hide the delete screen frame."""
        self.frame.pack_forget()

    def get_dir_name(self, file_path: str) -> str:
        """Get the directory name from a full file path."""
        return "/".join(file_path.split("/")[-2::])

    def show_file_choice(self):
        """Display the file delete options."""
        self.clear_button.pack_forget()
        self.delete_button.pack_forget()
        self.enter_file_label.pack()
        self.file_entry.pack()

        self.enter_dir_label.pack_forget()
        self.dir_entry.pack_forget()
        self.delete_button.pack()
        self.clear_button.pack(pady=10)

    def show_dir_choice(self):
        """Display the directory delete options."""
        self.clear_button.pack_forget()
        self.delete_button.pack_forget()

        self.enter_file_label.pack_forget()
        self.file_entry.pack_forget()

        self.enter_dir_label.pack()
        self.dir_entry.pack()

        self.delete_button.pack()
        self.clear_button.pack(pady=10)

    def __init__(self, root):
        """Initialize the DeleteScreen."""
        self.frame = tk.Frame(root, **theme_screen_colors["delete"])
        self.archive_file_path = ""
        self.extract_archive_label = tk.Label(self.frame, text="Select Archive File:",**font)
        self.extract_archive_label.pack()

        self.archive_path_label = tk.Label(self.frame, width=50,**font)
        self.archive_path_label.pack()

        self.extract_archive_browse_button = tk.Button(self.frame, text="Browse...",
                                                       command=self.browse_extract_archive_file,**font)
        self.extract_archive_browse_button.pack(pady=(0, 10))

        self.algo_label = tk.Label(self.frame, text="Type of file to add:",**font)
        self.algo_label.pack()

        self.add_type_var = tk.StringVar(self.frame)
        self.add_type_var.set("FILE")  # Set default algorithm

        self.file_radio = tk.Radiobutton(self.frame, text="File", variable=self.add_type_var, value="FILE",
                                         command=self.show_file_choice,**font)
        self.file_radio.pack()

        self.dir_radio = tk.Radiobutton(self.frame, text="Directory", variable=self.add_type_var,
                                        value="DIR", command=self.show_dir_choice,**font)
        self.dir_radio.pack(pady=(0, 10))

        self.enter_file_label = tk.Label(self.frame, text="Enter relative file path to add: (e.g - folder_name/filename)",**font)
        self.enter_file_label.pack()
        self.selected_files = []  # List to store selected files
        self.file_entry = tk.Entry(self.frame, width=50,**font)
        self.file_entry.pack()


        self.enter_dir_label = tk.Label(self.frame, text="Enter the directory name to delete: (e.g - folder_name)",**font)
        self.enter_dir_label.pack_forget()
        self.selected_files = []  # List to store selected files
        self.dir_entry = tk.Entry(self.frame, width=50,**font)
        self.dir_entry.pack_forget()


        self.delete_button = tk.Button(self.frame, text="Delete", command=self.show_frame,**font)
        self.delete_button.pack(pady=10)

        self.clear_button = tk.Button(self.frame, text="Clear", command=self.clear_fields,width=15,**font)
        self.clear_button.pack(pady=10)

    def clear_fields(self):
        """Clear all entry fields and reset variables."""
        self.archive_path_label.configure(text="")
        self.dir_entry.delete(0, tk.END)
        self.file_entry.delete(0, tk.END)
        self.archive_file_path = ""
        self.dir_path = ""
        self.file_path = ""

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def is_valid_input(self):
        """Check if the provided input for delete is valid."""
        if self.archive_file_path == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the archive")
            return False
        if self.add_type_var.get() == "FILE" and self.file_entry.get() == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the file")
            return False
        if self.add_type_var.get() == "DIR" and self.dir_entry.get() == "":
            tk.messagebox.showerror("Not valid input", "no path was given to the directory")
            return False
        return True

    def get_data(self):
        """Get the data entered in the delete screen."""
        if self.is_valid_input():
            if self.add_type_var.get() == "FILE":
                return self.archive_file_path, self.file_entry.get(), {}
            elif self.add_type_var.get() == "DIR":
                return self.archive_file_path, self.dir_entry.get(), {}
        return None, {}



class CompressorGUI:
    """Class representing the main GUI for file compression and extraction."""

    def update_status(self, msg):
        """Update the status label with a given message."""
        self.status_label.configure(text=msg)

    def bind_buttons(self, functions):
        """Bind buttons to their respective functions."""
        self.compress_frame.compress_button.bind("<Button-1>", functions["compress"])
        self.extract_frame.extract_button.bind("<Button-1>", functions["extract"])
        self.add_frame.add_button.bind("<Button-1>", functions["add"])
        self.update_frame.update_button.bind("<Button-1>", functions["update"])
        self.delete_frame.delete_button.bind("<Button-1>", functions["delete"])

    def get_input(self, frame_name):
        """Get input data from a specific frame."""
        *args, kwargs = self.dict_of_frames[frame_name].get_data()
        kwargs["password"] = self.password_entry.get()
        return args, kwargs

    def __init__(self):
        """Initialize the GUI."""
        root = tk.Tk()
        root.title("File Compressor/Extractor")
        root.resizable(False, False)
        root.geometry("900x750")

        root.configure(**theme_screen_colors["compress"])
        self.main_window = root

        # Create container frames for compression and extraction screens

        # Mode selection (compress or extract)
        self.mode_var = tk.StringVar(self.main_window)
        self.mode_var.set("compress")  # Default mode

        DEFAULT_THEME_SCREEN = theme_screen_colors[self.mode_var.get()]
        DEFAULT_THEME_FONTS = theme_font_colors[self.mode_var.get()]

        self.mode_label = tk.Label(self.main_window, text="Mode:", **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                   font=("Arial", 24, "bold"))
        self.mode_label.pack()

        self.current_mode = tk.Label(self.main_window, text="compress", **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                     font=("Arial", 17, "bold"))
        self.current_mode.pack()

        # Frame for radio buttons (expand horizontally)
        self.mode_button_frame = tk.Frame(self.main_window, **DEFAULT_THEME_SCREEN)
        self.mode_button_frame.pack(fill=tk.X, expand=True)

        # Add radio buttons with weight (relative sizing)
        self.compress_radio = tk.Radiobutton(self.mode_button_frame, text="Compress", variable=self.mode_var,
                                             value="compress",
                                             command=self.change_screen, **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                             font=("Arial", 15, "bold"))
        self.compress_radio.pack(side='left', expand=True)  # Expand to fill available space

        self.delete_radio = tk.Radiobutton(self.mode_button_frame, text="Delete", variable=self.mode_var,
                                           value="delete",
                                           command=self.change_screen, **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                           font=("Arial", 15, "bold"))
        self.delete_radio.pack(side='left', expand=True)  # Expand to fill available space

        self.update_radio = tk.Radiobutton(self.mode_button_frame, text="Update", variable=self.mode_var,
                                           value="update",
                                           command=self.change_screen, **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                           font=("Arial", 15, "bold"))
        self.update_radio.pack(side='left', expand=True)  # Expand to fill available space

        self.add_radio = tk.Radiobutton(self.mode_button_frame, text="Add", variable=self.mode_var, value="add",
                                        command=self.change_screen, **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                        font=("Arial", 15, "bold"))
        self.add_radio.pack(side='left', expand=True)  # Expand to fill available space

        self.extract_radio = tk.Radiobutton(self.mode_button_frame, text="Extract", variable=self.mode_var,
                                            value="extract",
                                            command=self.change_screen, **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN,
                                            font=("Arial", 15, "bold"))
        self.extract_radio.pack(side='left', expand=True)  #

        self.status_label = tk.Label(self.main_window, text="current task - None", font=("Arial", 15, "bold"),
                                      **DEFAULT_THEME_FONTS, **DEFAULT_THEME_SCREEN)
        self.status_label.pack(pady=4)

        self.password_label = tk.Label(self.main_window, text="Enter password:", **font)
        self.password_label.pack()
        self.password_entry = tk.Entry(self.main_window, text="password", **font, width=50)
        self.password_entry.pack(pady=(0, 10))

        self.compress_frame = CompressionScreen(root)
        self.extract_frame = ExtractScreen(root)
        self.extract_frame.hide_frame()
        self.delete_frame = DeleteScreen(root)
        self.delete_frame.hide_frame()
        self.update_frame = UpdateScreen(root)
        self.update_frame.hide_frame()
        self.add_frame = AddScreen(root)
        self.add_frame.hide_frame()
        self.list_radio_buttons = [self.compress_radio, self.extract_radio, self.add_radio, self.update_radio,
                                   self.delete_radio]
        self.dict_of_frames = {"add": self.add_frame, "update": self.update_frame, "delete": self.delete_frame,
                               "extract": self.extract_frame, "compress": self.compress_frame}

    def show_success_message(self, msg):
        """Display a success message."""
        tk.messagebox.showinfo("Task Complete:", msg)

    def show_error_message(self, msg):
        """Display an error message."""
        tk.messagebox.showerror("Not valid input", msg)

    def get_filename(self, file_path: str) -> str:
        """Get the filename from a full file path."""
        return file_path.split(r"/")[-1]

    def change_screen(self):
        """Change the current mode of the GUI."""
        self.current_mode.configure(text=self.mode_var.get(), **theme_font_colors[self.mode_var.get()],
                                    **theme_screen_colors[self.mode_var.get()])
        self.main_window.configure(**theme_screen_colors[self.mode_var.get()])
        for frame_name in self.dict_of_frames:
            if self.mode_var.get() == frame_name:
                self.dict_of_frames[frame_name].show_frame()
            else:
                self.dict_of_frames[frame_name].hide_frame()
        for radio_button in self.list_radio_buttons:
            radio_button.configure(**theme_font_colors[self.mode_var.get()], **theme_screen_colors[self.mode_var.get()])
        self.mode_button_frame.configure(**theme_screen_colors[self.mode_var.get()])
        self.mode_label.configure(**theme_font_colors[self.mode_var.get()], **theme_screen_colors[self.mode_var.get()])
        self.status_label.configure(**theme_font_colors[self.mode_var.get()], **theme_screen_colors[self.mode_var.get()])

    def run(self) -> None:
        """Run the main GUI loop."""
        self.main_window.mainloop()