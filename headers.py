from typing import Tuple, List
import base64


class ArchiveHeader:
    def __init__(self, *args, **kwargs):
        """Initializes an instance of ArchiveHeader."""
        # Number of bytes for various header fields
        self.NUM_OF_CHECKSUM_BYTES = 16
        self.NUM_OF_PASSWORD_BYTES = 16
        self.NUM_OF_KET_BYTES = 32
        self.IS_DIR_BYTES = 1
        self.COMPRESSION_ALGO_BYTES = 1
        self.NUM_OF_SEQ_LEN_BYTE = 2
        self.NUM_ARCHIVE_FILE_SIZE_BYTES = 10
        self.NUM_OF_FILES_IN_ARCHIVE_BYTES = 4
        self.NUM_OF_FILENAME_LENGTH_BYTES = 4
        self.NUM_OF_FILE_SIZE_BYTES = 8
        self.NUM_OF_BYTES_RLE_COUNTER = 2
        self.HUFFMAN_ALGO_CODE = 2
        self.RLE_ALGO_CODE = 1

        # Initialize attributes based on arguments or binary data
        if "to_bytes" in kwargs:
            # Initialize from provided arguments
            self.md5_password, self.key, self.checksum, self.comp_algo, self.byte_seq_len, self.total_files_size, self.number_of_files = args
        elif "from_bytes" in kwargs:
            # Initialize from binary data
            try:
                archive_file = args[0]
                self.md5_password, self.key, self.checksum, self.comp_algo, self.byte_seq_len, self.total_files_size, self.number_of_files = self.__from_bytes(
                    archive_file)
            except:
                raise IOError("Potential file corruption detected. The header of the archive was destroyed")

    def get_pass(self):
        return self.md5_password

    def to_bytes(self):
        """the hedaer of the archive file look like this:

         +-----------------+-------------+---------------+--------------------------+---------------------------+-----------------------+-----------------------------+
         | Password(16B)  |  key (32B)  | Checksum (16B) |Compression algorithm (1B)| Byte sequence length (2B)| Total file size (10B) |  Total number of Files (4B)  |
         +----------------+-------------+----------------+--------------------------+--------------------------+-----------------------+-----------------------------+
             ( when i am referring to file name i meant to the archive file name)
             also the Byte sequence length is the len of the sequence of bytes that were use in the rle algorithm
            Checksum- MD5 generates a 128-bit (16-byte) hash value.
            we need to allocate 16 bytes in the header to store the complete checksum/password.
            the key for the encryption is a 32 bits key.

             """
        archive_file_header = b""
        archive_file_header += self.md5_password
        key_decoded = base64.urlsafe_b64decode(self.key)  # for the key to be 32 bytes
        archive_file_header += key_decoded
        archive_file_header += self.checksum
        if self.comp_algo == "RLE":
            archive_file_header += self.RLE_ALGO_CODE.to_bytes(length=1, byteorder="little")
        elif self.comp_algo == "HUF":
            archive_file_header += self.HUFFMAN_ALGO_CODE.to_bytes(length=1, byteorder="little")
        # Byte sequence length (2 bytes)
        archive_file_header += self.byte_seq_len.to_bytes(length=2, byteorder="little")
        # File Size
        archive_file_header += self.total_files_size.to_bytes(length=10, byteorder="little")
        # num of files in the archives:
        archive_file_header += self.number_of_files.to_bytes(length=4, byteorder="little")

        return archive_file_header

    def __from_bytes(self, archive_file):
        """
        Parses the binary data from the archive file to retrieve header information.

        Args:
            archive_file (file): The binary IO archive file object.

        Returns:
            tuple: A tuple containing the parsed header information.
        """
        # Read password, key, and checksum from the archive file
        password = archive_file.read(self.NUM_OF_PASSWORD_BYTES )
        key_decoded = archive_file.read(self.NUM_OF_KET_BYTES)
        key = base64.urlsafe_b64encode(key_decoded)
        checksum = archive_file.read(self.NUM_OF_CHECKSUM_BYTES)

        # Read compression algorithm code from the archive file
        comp_algo = archive_file.read(self.COMPRESSION_ALGO_BYTES)
        comp_algo = int.from_bytes(comp_algo, byteorder="little")

        # Read byte sequence length from the archive file
        byte_seq_len = archive_file.read(self.NUM_OF_SEQ_LEN_BYTE)
        byte_seq_len = int.from_bytes(byte_seq_len, byteorder="little")

        # Read total file size from the archive file
        total_file_size = archive_file.read(self.NUM_ARCHIVE_FILE_SIZE_BYTES)
        total_file_size = int.from_bytes(total_file_size, byteorder="little")

        # Read number of files in the archive from the archive file
        number_of_files = archive_file.read(self.NUM_OF_FILES_IN_ARCHIVE_BYTES)
        number_of_files = int.from_bytes(number_of_files, byteorder="little")

        return password, key, checksum, comp_algo, byte_seq_len, total_file_size, number_of_files


class HuffFileHeader:
    def __init__(self, *args, **kwargs):
        """
        Initializes a RleFileHeader object.

        Attributes:
            FILE_SIZE_BYTES (int): Number of bytes for file size.
            TREE_SIZE_BYTES (int): Number of bytes for tree size.
            THE_CORRECT_SIZE_BYTES (int): Number of bytes for correct size.
            FILE_NAME_BYTES (int): Number of bytes for file name.
            IS_DIR_BYTES (int): Number of bytes for directory indicator.

        Raises:
            IOError: If parsing from bytes encounters issues.
        """
        self.FILE_SIZE_BYTES = 8
        self.TREE_SIZE_BYTES = 5
        self.THE_CORRECT_SIZE_BYTES = 7
        self.FILE_NAME_BYTES = 4
        self.IS_DIR_BYTES = 1

        if "to_bytes" in kwargs:
            self.file_path, self.actual_file_size, self.correct_file_size, self.tree_size, self.is_dir = args
        elif "from_bytes" in kwargs:
            archive_file = args[0]
            self.file_path, self.actual_file_size, self.correct_file_size, self.tree_size, self.is_dir = self.__from_bytes(
                archive_file)

    def get_filename(self, file_path: str) -> str:
        """given a full path of a file, return the name of the file with its type"""
        return file_path.split("/")[-1]

    def get_dir_name(self, file_path: str) -> str:
        """given a full path of a file, return the name of the file and is dad folder with its type"""
        return "/".join(file_path.split("/")[-2::])

    def to_bytes(self) -> bytes:
        """given the path to the file to compress,
        its compress size with the artificial 0 and without and the size of the tree text file
        return the header of the compressed file with look like the following:
        +-------------------+------------------+--------------------------+-----------------------+---------------------+
        |Is directory (1B)   |  File size (8B)   |  Tree size (5B)  |  Correct file Size (7B)  |  Filename Length (4B) | Filename (X bytes) |
        +-------------------+------------------+--------------------------+-----------------------+--------------------+
         correct_size is without the artificial zeros i add in order to overcome the obstacle of the 8 bits when writing to a file

         """

        header = b""
        if self.is_dir:
            is_dir = 1
            header += is_dir.to_bytes(length=self.IS_DIR_BYTES, byteorder="little")
            filename = self.get_dir_name(self.file_path)  # return only the relative path of the file
            # its directory/ file
        else:
            is_dir = 0
            header += is_dir.to_bytes(length=self.IS_DIR_BYTES, byteorder="little")
            filename = self.get_filename(self.file_path)  # return only the file name
        # File Size (8 bytes)
        header += self.actual_file_size.to_bytes(length=self.FILE_SIZE_BYTES, byteorder="little")
        # huffman tree size (5 bytes):
        header += self.tree_size.to_bytes(length=self.TREE_SIZE_BYTES, byteorder="little")
        # the actual data size without the last artificial 0 to complete to 8 bits
        header += self.correct_file_size.to_bytes(length=self.THE_CORRECT_SIZE_BYTES, byteorder="little")
        filename_length = len(filename.encode("ascii"))
        # Add filename length
        header += filename_length.to_bytes(length=self.FILE_NAME_BYTES, byteorder="little")

        # Add filename (ASCII encoding)
        header += filename.encode("ascii")
        return header

    def __from_bytes(self, archive_file) -> Tuple[str, int, int, int, bool]:
        """given the archive file,
         return  the header of the compressed file (include the tree file and the text file)"""

        # convert to integer the sizes of the files and the file name:
        is_dir = archive_file.read(self.IS_DIR_BYTES)
        is_dir = int.from_bytes(is_dir, byteorder="little")

        file_size = archive_file.read(self.FILE_SIZE_BYTES)
        file_size = int.from_bytes(file_size, byteorder="little")

        tree_size = archive_file.read(self.TREE_SIZE_BYTES)
        tree_size = int.from_bytes(tree_size, byteorder="little")

        correct_size = archive_file.read(self.THE_CORRECT_SIZE_BYTES)
        correct_size = int.from_bytes(correct_size, byteorder="little")

        filename_length = archive_file.read(self.FILE_NAME_BYTES)
        filename_length = int.from_bytes(filename_length, byteorder="little")
        filename = archive_file.read(filename_length)
        filename = filename.decode("ascii")

        return filename, file_size, correct_size, tree_size, is_dir == 1


class RleFileHeader:
    def __init__(self, *args, **kwargs):
        """
        Initializes an ArchiveHeader object.

        Raises:
            IOError: If parsing from bytes encounters issues.
        """
        self.NUM_OF_CHECKSUM_BYTES = 16
        self.IS_DIR_BYTES = 1
        self.COMPRESSION_ALGO_BYTES = 1
        self.NUM_OF_SEQ_LEN_BYTE = 2
        self.NUM_ARCHIVE_FILE_SIZE_BYTES = 10
        self.NUM_OF_FILES_IN_ARCHIVE_BYTES = 4
        self.NUM_OF_FILENAME_LENGTH_BYTES = 4
        self.NUM_OF_FILE_SIZE_BYTES = 8
        self.NUM_OF_BYTES_RLE_COUNTER = 2
        self.HUFFMAN_ALGO_CODE = 2
        self.RLE_ALGO_CODE = 1

        if "to_bytes" in kwargs:
            self.file_path, self.compress_file_size, self.is_dir = args
        elif "from_bytes" in kwargs:
            archive_file = args[0]
            self.file_path, self.compress_file_size, self.is_dir = self.__from_bytes(archive_file)

    def get_filename(self, file_path: str) -> str:
        """given a full path of a file, return the name of the file with its type"""
        return file_path.split("/")[-1]

    def get_dir_name(self, file_path: str) -> str:
        """given a full path of a file, return the name of the file and is dad folder with its type"""
        return "/".join(file_path.split("/")[-2::])

    def to_bytes(self) -> bytes:
        """given the path to the file to compress,
        its compress size with the artificial 0 and without and the size of the tree text file
        return the header of the compressed file with look like the following:
        +-------------------+------------------+--------------------------+-----------------------+---------------------+
        |Is directory (1B)   |  File size (8B)   |  Tree size (5B)  |  Correct file Size (7B)  |  Filename Length (4B) | Filename (X bytes) |
        +-------------------+------------------+--------------------------+-----------------------+--------------------+
         correct_size is without the artificial zeros i add in order to overcome the obstacle of the 8 bits when writing to a file

         """
        NUM_BYTES_FILE_SIZE = 8
        NUM_OF_BYES_FILENAME = 4
        IS_DIR_BYTES = 1
        header = b""
        if self.is_dir:
            is_dir = 1
            header += is_dir.to_bytes(length=IS_DIR_BYTES, byteorder="little")
            filename = self.get_dir_name(self.file_path)  # return only the relative path of the file
            # its directory/ file
        else:
            is_dir = 0
            header += is_dir.to_bytes(length=IS_DIR_BYTES, byteorder="little")
            filename = self.get_filename(self.file_path)  # return only the file name

        # File Size (4 bytes)
        header += self.compress_file_size.to_bytes(length=NUM_BYTES_FILE_SIZE, byteorder="little")
        filename_length = len(filename.encode("ascii"))
        # Add filename length
        header += filename_length.to_bytes(length=NUM_OF_BYES_FILENAME, byteorder="little")

        # Add filename (ASCII encoding)
        header += filename.encode("ascii")
        return header

    def __from_bytes(self, archive_file) -> Tuple[str, int, bool]:
        """
        Extracts header information from bytes.

        Args:
            archive_file: Binary file object.

        Returns:
            Tuple[str, int, bool]: Filename, file size, and a boolean indicating if it's a directory.
        """
        is_dir = int.from_bytes(archive_file.read(self.IS_DIR_BYTES), byteorder="little")
        file_size = int.from_bytes(archive_file.read(self.NUM_OF_FILE_SIZE_BYTES), byteorder="little")
        filename_length = int.from_bytes(archive_file.read(self.NUM_OF_FILENAME_LENGTH_BYTES), byteorder="little")
        filename = archive_file.read(filename_length).decode("ascii")
        return filename, file_size, is_dir == 1
