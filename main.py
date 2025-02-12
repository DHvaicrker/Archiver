from gui import CompressorGUI
from zip import Zip
import threading
import argparse
import time

class ZipController():

    def __init__(self):
        """initialize variables and bind the gui buttons with the zip commands"""
        self.function_dict = {"compress": self.on_compress_button_click, "extract": self.on_extract_button_click,
                              "update": self.on_update_button_click, "add": self.on_add_button_click,
                              "delete": self.on_delete_button_click}
        self._gui = CompressorGUI()
        self._gui.bind_buttons(self.function_dict)  # Bind callback using bind method

    def start_task(self, task_name, *args, **kwargs):
        """given a task name and the arguments its need to complete the task,
         do the task and show the task statistics results"""
        ARGS_INDEX = 0
        try:
            task_res = ""
            if task_name == "compress":
                archive_name, files = args[ARGS_INDEX]
                archive_file = Zip(archive_name)
                task_res = archive_file.compress(*files, **kwargs)

            elif task_name == "extract":

                archive_name, extract_dir = args[ARGS_INDEX]
                archive_file = Zip(archive_name.replace(".bin", ""))
                task_res = archive_file.extract(extract_dir, **kwargs)
            elif task_name == "add":

                archive_name, path_to_add = args[ARGS_INDEX]
                archive_file = Zip(archive_name.replace(".bin", ""))
                task_res = archive_file.add(path_to_add, **kwargs)
            elif task_name == "delete":

                archive_name, relative_path = args[ARGS_INDEX]
                archive_file = Zip(archive_name.replace(".bin", ""))
                task_res = archive_file.delete(relative_path, **kwargs)
            elif task_name == "update":
                archive_name, full_path = args[ARGS_INDEX]
                archive_file = Zip(archive_name.replace(".bin", ""))
                task_res = archive_file.update(full_path, **kwargs)

            self._gui.update_status("current task - None")
            self._gui.show_success_message(task_res)
        except Exception as e:
            self._gui.update_status("current task - None")

            self._gui.show_error_message(str(e))

    def on_compress_button_click(self, event):
        """create the compression thread and start it"""
        *args, kwargs = self._gui.get_input("compress")
        if args == [[None]]:  # meaning not valid input
            return
        task_thread = threading.Thread(target=self.start_task, args=("compress", *args), kwargs=kwargs)
        self._gui.update_status("Current task - start compressing...")
        task_thread.start()

    def on_extract_button_click(self, event):
        """create the extract thread and start it"""
        *args, kwargs = self._gui.get_input("extract")
        if args == [[None]]:
            return
        task_thread = threading.Thread(target=self.start_task, args=("extract", *args), kwargs=kwargs)
        self._gui.update_status("Current task - start extracting...")
        task_thread.start()

    def on_update_button_click(self, event):
        """create the update thread and start it"""
        *args, kwargs = self._gui.get_input("update")
        if args == [[None]]:
            return
        task_thread = threading.Thread(target=self.start_task, args=("update", *args), kwargs=kwargs)
        self._gui.update_status("Current task - start updating...")
        task_thread.start()

    def on_add_button_click(self, event):
        """create the add thread and start it"""
        *args, kwargs = self._gui.get_input("add")
        if args == [[None]]:
            return
        task_thread = threading.Thread(target=self.start_task, args=("add", *args), kwargs=kwargs)
        self._gui.update_status("Current task - start adding...")
        task_thread.start()

    def on_delete_button_click(self, event):
        """create the delete thread and start it"""
        *args, kwargs = self._gui.get_input("delete")
        if args == [[None]]:
            return
        task_thread = threading.Thread(target=self.start_task, args=("delete", *args), kwargs=kwargs)
        self._gui.update_status("Current task - start deleting...")
        task_thread.start()

    def run(self):
        """run the gui"""
        self._gui.run()


def handle_compress(args):
    """compress files into a archive file given the following command line:
    compress archive.zip file1.txt file2.txt --dirs_to_compress dir1 --encoding HUF/RLE --byte_seq_len 8 --password my_password
"""
    archive_path = args.archive_path
    files_to_compress = args.files_to_compress
    dirs_to_compress = args.dirs_to_compress
    encoding = args.encoding
    byte_seq_len = args.byte_seq_len
    password = args.password

    # Perform compression logic here
    print("Compress command")
    print(f"Archive path: {archive_path}")
    print(f"Files to compress: {files_to_compress}")
    print(f"Directories to compress: {dirs_to_compress}")
    print(f"Encoding: {encoding}")
    print(f"Byte sequence length: {byte_seq_len}")
    print(f"Password: {password}")
    try:
        archive_file = Zip(archive_path)
        if byte_seq_len==None:
            byte_seq_len =1
        archive_file.compress(*files_to_compress,dir=dirs_to_compress,encoding=encoding,byte_seq_len=byte_seq_len,password=password,compress = True)
    except Exception as e:
        print(str(e))
def handle_add(args):
    """add the archive file given the following command line:
    add archive.zip file_to_add.txt --password my_password
    """
    archive_path = args.archive_path
    file_or_dir_to_add = args.file_or_dir_to_add
    password = args.password

    # Perform add logic here
    print("Add command")
    print(f"Archive path: {archive_path}")
    print(f"File or directory to add: {file_or_dir_to_add}")
    print(f"Password: {password}")

    try:
        archive_path = args.archive_path.replace(".bin", "")
        archive_file = Zip(archive_path)
        archive_file.add(file_or_dir_to_add, password=password,add = True)
    except Exception as e:
        print(str(e))
def handle_delete(args):

    """delete the archive file given the following command line:
    delete archive.zip file_or_dir_to_delete.txt --password my_password
    """
    print("Delete command arguments:")
    print("  Archive path:", args.archive_path)
    print("  File or directory to delete:", args.file_or_dir_to_delete)
    print("  Password:", args.password)

    try:
        archive_path = args.archive_path.replace(".bin", "")
        archive_file = Zip(archive_path)
        archive_file.delete(args.file_or_dir_to_delete, password=args.password,delete = True)
    except Exception as e:
        print(str(e))
def handle_update(args):
    """update the archive file given the following command line:
    update archive_path file_or_dir_to_update --password PASSWORD"""
    print("Update command arguments:")
    print("  Archive path:", args.archive_path)
    print("  File or directory to update:", args.file_or_dir_to_update)
    print("  Password:", args.password)

    try:
        archive_path = args.archive_path.replace(".bin", "")
        archive_file = Zip(archive_path)
        archive_file.update(args.file_or_dir_to_update, password=args.password,update = True)
    except Exception as e:
        print(str(e))
def handle_extract(args):
    """extract the archive file given his input
    extract /path/to/extract/dir --password my_password"""
    print("Extract command arguments:")
    print("  Archive path:", args.archive_path)
    print("  Path to extract directory:", args.path_to_extract_dir)
    print("  Password:", args.password)
    try:
        archive_path = args.archive_path.replace(".bin", "")
        archive_file = Zip(archive_path)
        archive_file.extract(args.path_to_extract_dir, password=args.password,extract = True)
    except Exception as e:
        print(str(e))
def get_parser():
    """"create the commands formats and return the argparse object"""

    parser = argparse.ArgumentParser(prog='zip_project')
    subparsers = parser.add_subparsers(dest='command', metavar='command', help='Commands')

    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress files and directories.')
    compress_parser.add_argument('archive_path', help='Path to the archive file.')
    compress_parser.add_argument('files_to_compress', nargs='+', help='Files to compress.')
    compress_parser.add_argument('--dirs_to_compress', nargs='+', default=[], help='Directories to compress.')
    compress_parser.add_argument('--encoding', choices=['HUF', 'RLE'], required=True,
                                 help='Compression encoding (HUF or RLE).')
    compress_parser.add_argument('--byte_seq_len', type=int, help='Number of bytes in a single unit (for RLE).')
    compress_parser.add_argument('--password', required=True, help='Password for encryption.')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add file or directory to an existing archive file.')
    add_parser.add_argument('archive_path', help='Path to the archive file.')
    add_parser.add_argument('file_or_dir_to_add', help='File or directory to add.')
    add_parser.add_argument('--password', required=True, help='Password for encryption.')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete file or directory from an existing archive file.')
    delete_parser.add_argument('archive_path', help='Path to the archive file.')
    delete_parser.add_argument('file_or_dir_to_delete', help='File or directory to delete.')
    delete_parser.add_argument('--password', required=True, help='Password for encryption.')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update file or directory in an existing archive file.')
    update_parser.add_argument('archive_path', help='Path to the archive file.')
    update_parser.add_argument('file_or_dir_to_update', help='File or directory to update.')
    update_parser.add_argument('--password', required=True, help='Password for encryption.')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract files and directories from the archive file.')
    extract_parser.add_argument('archive_path', help='Path to the archive file.')
    extract_parser.add_argument('path_to_extract_dir', help='Path to the directory to extract to.')
    extract_parser.add_argument('--password', required=True, help='Password for encryption.')

    return parser
def handle_terminal_commands():
    """get user input and act according to his commands( update add compress extract quit delete)"""
    parser = get_parser()

    while True:
        command = input("Enter a command: ").strip()
        # validate input:
        if command == "quit":
            print("Exiting the program.")
            return

        parts = command.split()
        if not parts:
            time.sleep(0.01)
            print("Please enter a valid command.")
            continue

        try:
            # do the command:
            args = parser.parse_args(parts)
            if args.command == 'compress':
                handle_compress(args)
            elif args.command == 'add':
                handle_add(args)
            elif args.command == 'delete':
                handle_delete(args)
            elif args.command == 'update':
                handle_update(args)
            elif args.command == 'extract':
                handle_extract(args)
            else:
                print("Invalid command:", args.command)
        except SystemExit:
            # he entered a empty command
            print("Please enter a valid command.")
        except Exception as e:
            print("An error occurred:", e)





def main():
    """start the running of project"""
    # create the help instruction:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
    A zip project that uses huffman and rle algorithms to compress combine with gui and some cool features.
    If you chose the gui option it is pretty straight forward. The terminal commands are:

    TO COMPRESS (and create the archive file) FILES AND DIRECTORYS (with only files underneath):
    compress archive_name_with_no_ending file_path_to_compress1 file2... --dirs_to_compress dir_path_to_compress1 dir2... 
    --byte_seq_len number(in case of RLE)  --encoding HUF/RLE (must be specified)
    --password my_password ( must be specified)


    TO ADD FILE OR DIRECTORY (only one at a time) to an existing archive file (only one is allowed at a time):
    add archive_path ( must be specified) file_to_add.txt --password my_password ( must be specified)

    TO DELETE FILE OR DIRECTORY (only one at a time) from an existing archive file:
    delete archive_path  ( must be specified) file_or_dir_to_delete --password my_password ( must be specified)


    TO UPDATE FILE OR DIRECTORY (only one at a time) that an exist in the archive file:
    update archive_path ( must be specified)  path_of_file_to_update/directory_path (only one is allowed at a time) 
    --password PASSWORD ( must be specified)


    TO EXTRACT the files and directorys from the archive file:
    extract archive_path path_to_extract_dir(needs to be empty) --password my_pass( must be specified)

    quit - to exit and stop the program'''
    )

    parser.add_argument('-e', '--epilog', help="I hope you will enjoy it :)")

    parser.parse_args()
    # get user choice of gui or terminal and the project:
    while True:
        user_choice = input(
            "Do you want to use GUI or terminal? (Enter 'gui' or 'terminal', or 'exit' to quit): ").lower()

        if user_choice == 'gui':
            z = ZipController()
            z.run()

        elif user_choice == 'terminal':
            handle_terminal_commands()
        elif user_choice == 'exit':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter 'gui', 'terminal', or 'exit'.")


if __name__ == "__main__":
    main()

