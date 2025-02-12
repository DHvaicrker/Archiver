import time
import os
import hashlib
from huffman_code import Huffman
import shutil
from typing import Tuple, List,BinaryIO
import tempfile
from headers import ArchiveHeader, HuffFileHeader, RleFileHeader
from decorators import with_temp_dir,password_check
from cryptography.fernet import Fernet

class Zip:

    def __init__(self, archive_filename: str) -> None:
        """
        Initializes a Zip object with its archive filename (without extension).

        Args:
            archive_filename (str): The base name of the archive file to be created.
        """

        self.files_to_compress = []  # List of file paths to compress
        self.file_sizes = []  # Corresponding sizes of files to compress
        self.dirs_to_compress = {}  # Mapping of directory paths to relative paths within the archive
        self.archive_path = archive_filename + ".bin"  # Path to the archive file

        self.byte_seq_len = 1  # Length of a byte sequence in the header
        self.is_dir = 0  # Flag indicating directory (0 for False in binary)

        self.time_to_extract = 0.0  # Time taken for extraction (initially 0)
        self.time_to_compress = 0.0  # Time taken for compression (initially 0)
        self.archive_size = 0  # Total size of the archive (initially 0)
        self.total_files_size = 0  # Total size of files to be compressed (initially 0)
        self.encryption_key = None  # Encryption key (initially None)
        self.password = b""  # Password for encryption (initially empty bytes)

    def get_filename(self, file_path: str) -> str:
        """
        Extracts the filename with its extension from a given file path.

        Args:
            file_path (str): The full path to the file.

        Returns:
            str: The filename with its extension.
        """

        return os.path.basename(file_path)

    def get_dir_name(self, file_path: str) -> str:
        """given a full path of a file, return the name of the file and is dad folder with its type"""
        return "/".join(file_path.split("/")[-2::])

    def get_files_size(self) -> int:
        """go over all the files to compress and get thier size with the is method"""
        size = 0
        for file in self.files_to_compress:
            self.file_sizes.append(os.path.getsize(file))
            size += os.path.getsize(file)
        for dir in self.dirs_to_compress:
            for file in self.dirs_to_compress[dir]:
                self.file_sizes.append(os.path.getsize(file))
                size += os.path.getsize(file)
        return size

    def convert_to_8_bits(self, data: str) -> bytes:
        """given a string of 1 and 0 representing a binary sequnce of bits, return the byte representation in 8 bits"""
        bits_count = 0
        BASE = 2
        NUM_OF_BITS = 8
        ARTIFICIAL_ZERO = "0"
        encoded_data = bytearray()
        compress_binary_data_len = len(data)
        compress_binary_8_bits = data
        # if the number of 0 and 1 doesnt divided by the 8 add artificial zeros:
        if compress_binary_data_len % NUM_OF_BITS != 0:
            # complete the zeros:
            compress_binary_8_bits += ARTIFICIAL_ZERO * (NUM_OF_BITS - (compress_binary_data_len % NUM_OF_BITS))

        while bits_count < len(compress_binary_8_bits):
            # convert to 1 byte:
            byte = int(compress_binary_8_bits[bits_count:bits_count + NUM_OF_BITS], BASE)
            encoded_data.append(
                byte)  # 8 becasue of the 8 bits i basicly trick the system to think that those bits are in 8 bits but i just add zeros so it will divide correcly by 8 and
            bits_count += NUM_OF_BITS
        return encoded_data

    def get_compressed_huff_file(self, file_path_to_compress: str, is_dir: bool) -> Tuple[bytes, int]:
        """
        Compresses a file using Huffman coding and returns the compressed data and its size.

        Args:
            file_path_to_compress (str): The path to the file to compress.
            is_dir (bool): Indicates whether the path points to a directory (True) or a file (False).

        Returns:
            tuple: A tuple containing the compressed data as bytes and its size in bytes.
        """

        with open(file_path_to_compress, "rb") as file:
            file_data = file.read()
        # create the tree object:
        huffman = Huffman(file_data)
        # compress the data:
        compress_binary_data = huffman.encode()
        # convert to 8 bits:
        encoded_huffman_data = self.convert_to_8_bits(compress_binary_data)
        # serialize the tree:
        huff_tree = huffman.serialize(huffman.root)
        # encode the tree string representation of the tree:
        encoded_huff_tree = huff_tree.encode()
        # create the file header:
        header_args = file_path_to_compress, len(encoded_huffman_data), len(compress_binary_data), len(
            encoded_huff_tree), is_dir

        huff_file_header = HuffFileHeader(*header_args, to_bytes=True)
        # convert to bytes:
        huff_file_header_byte = huff_file_header.to_bytes()

        return (huff_file_header_byte + encoded_huff_tree + encoded_huffman_data,
                len(huff_file_header_byte) + len(encoded_huffman_data) + len(encoded_huff_tree))

    def compress_Huffman(self,**kwargs) -> str:
        """
        Compresses all files using Huffman coding, encrypts the compressed data,
        and creates the archive file.

        Returns:
            str: A summary string containing compression statistics.
        """

        start_time = time.time()  # Capture start time

        # Initialize archive variables
        archive_data = b""
        total_archive_size = 0

        # Compress individual files
        for file_path in self.files_to_compress:
            compressed_file, compressed_size = self.get_compressed_huff_file(file_path, False)
            archive_data += compressed_file
            total_archive_size += compressed_size

        # Compress files within directories
        for directory, files in self.dirs_to_compress.items():
            for file_path in files:
                compressed_file, compressed_size = self.get_compressed_huff_file(file_path, True)
                archive_data += compressed_file
                total_archive_size += compressed_size

        # Create archive header
        header_args = (
            self.calculate_checksum(self.password),
            self.key,
            self.calculate_checksum(archive_data),
            "HUF",  # Archive format (consider using an enum for clarity)
            self.byte_seq_len,
            total_archive_size,
            len(self.files_to_compress) + self.calc_num_of_files_inside_dirs(),
        )
        archive_header = ArchiveHeader(*header_args, to_bytes=True)
        header_bytes = archive_header.to_bytes()

        # Encrypt and write data
        encrypted_archive = self.encrypt_data(archive_data)
        with open(self.archive_path, "wb") as archive_file:
            archive_file.write(header_bytes + encrypted_archive)

        # Calculate and print statistics
        end_time = time.time()
        compression_time = end_time - start_time
        if "compress"in kwargs:
            print(f"Compression Time: {compression_time:.2f} seconds\n"
                  f"Files Size Before: {self.files_size} bytes\n"
                  f"Files Size After: {total_archive_size} bytes\n"
                  f"Archive Size: {os.path.getsize(self.archive_path)} bytes\n")

        return (f"Compression Time: {compression_time:.2f} seconds\n"
                f"Files Size Before: {self.files_size} bytes\n"
                f"Files Size After: {total_archive_size} bytes\n"
                f"Archive Size: {os.path.getsize(self.archive_path)} bytes\n")


    def extract_Huffman(self, extract_dir_path: str,**kwargs) -> str:
        """
        Extracts compressed data from the archive file and recreates the files in the specified directory.

        Args:
            extract_dir_path (str): The path to the directory where extracted files will be written.

        Returns:
            str: A summary string containing extraction time.
        """

        start_time = time.time()

        # Open archive file and create temporary decrypted data container
        with open(self.archive_path, "rb") as archive_file, \
                tempfile.TemporaryFile(mode="w+b") as decrypted_archive:

            # Read and validate archive header
            archive_header = ArchiveHeader(archive_file, from_bytes=True)
            decrypted_data = self.decrypt_data(archive_header.key, archive_file.read())

            if self.calculate_checksum(decrypted_data) != archive_header.checksum:
                raise IOError("Checksum mismatch! Potential file corruption detected.\n"
                              "The calculated checksum doesn't match the stored checksum.")

            # Decrypt and store decrypted data
            decrypted_archive.write(decrypted_data)
            decrypted_archive.seek(0)  # Move file pointer to the beginning

            # Extract files
            extracted_files = {}
            for _ in range(archive_header.number_of_files):
                huff_header = HuffFileHeader(decrypted_archive, from_bytes=True)
                extracted_files[huff_header.file_path] = (
                    huff_header.is_dir,
                    self.extract_data_HUF(decrypted_archive,
                                          huff_header.actual_file_size,
                                          huff_header.correct_file_size,
                                          huff_header.tree_size)
                )

        # Write extracted files
        self.write_extracted_files_HUF(extract_dir_path, extracted_files)

        # Calculate and print statistics
        end_time = time.time()
        extraction_time = end_time - start_time
        if "extract" in kwargs:
            print(f"Extraction Time: {extraction_time:.2f} seconds")

        return f"Extraction Time: {extraction_time:.2f} seconds"

    def write_extracted_files_HUF(self, extract_dir_path: str, dict_files: dict) -> None:
        """
        Writes the extracted files from the dictionary to the specified directory,
        creating directories as needed.

        Args:
            extract_dir_path (str): The path to the directory where extracted files will be written.
            extracted_files (dict): A dictionary containing information about extracted files,
                                     including their paths, data, and directory status.
        """
        is_dir_index = 0
        main_extarct_path = extract_dir_path
        for file in dict_files:
            if dict_files[file][is_dir_index]:  # if it a file that under a dir
                # get the directory of the sub files and if it is the first file in the directory then create the directory inside the extarct directory
                dir_name = self.get_dir_name(file).split("/")[0]
                extract_dir_path += "/" + dir_name
                if not os.path.isdir(extract_dir_path):
                    os.mkdir(extract_dir_path)
            with open(f"{extract_dir_path}/{self.get_filename(file)}", "wb") as f:
                file_data = dict_files[file][1]
                f.write(file_data)
            extract_dir_path = main_extarct_path

    def extract_data_HUF(self, archive_file: BinaryIO, file_size: int, correct_size: int, tree_size: int) -> bytes:
        """
        Extracts data encoded with Huffman coding from the archive file.

        Args:
            archive_file (BinaryIO): A file-like object representing the archive data.
            file_size (int): Size of the compressed data (including artificial zeros).
            correct_size (int): Size of the actual compressed data (without artificial zeros).
            tree_size (int): Size of the Huffman tree data in bytes.

        Returns:
            bytes: The decompressed data.
        """

        # Read Huffman tree data
        tree_serialized = archive_file.read(tree_size).decode()

        # Read compressed data
        compressed_data = archive_file.read(file_size)

        # Convert compressed data to bit string (more efficient than byte-by-byte conversion)
        bits_string = ''.join(f'{byte:08b}' for byte in compressed_data)

        # Remove artificial zeros (more efficient slicing approach)
        bits_string = bits_string[:correct_size]

        # Create Huffman object, set tree, and decode data
        huffman = Huffman("")
        huffman.root = huffman.deserialize(tree_serialized)
        return huffman.decode(bits_string)

    def encode_rle_data(self, data_to_compress: bytes) -> List:
        """given the data to compress, compress it with the rle algorithm and return the compressed data"""
        compress_data = []
        if len(data_to_compress) == 0:
            return compress_data
        count_seq = 0
        # get first bytes sequence:
        prev_seq = data_to_compress[:self.byte_seq_len]
        for index in range(0, len(data_to_compress), self.byte_seq_len):
            # get next bytes sequence:
            current_seq = data_to_compress[index:index + self.byte_seq_len]
            # compare the sequence to the current byte sequence:
            if current_seq == prev_seq:
                # same , increment the number of appearances by 1
                count_seq += 1
            if current_seq != prev_seq:
                # different , restart with new  bytes sequence
                compress_data.append((count_seq, prev_seq))
                count_seq = 1
            prev_seq = current_seq
            # last sequence:
            if index == len(data_to_compress) - self.byte_seq_len:
                compress_data.append((count_seq, prev_seq))
                break
        if len(data_to_compress) % self.byte_seq_len != 0:
            # add the reminder of data to the list:
            OCCURRENCE = 1
            num_of_bytes_reminder = len(data_to_compress) % self.byte_seq_len
            data_reminder = data_to_compress[len(data_to_compress) - num_of_bytes_reminder::]

            compress_data.append((OCCURRENCE, data_reminder))

        return compress_data


    def get_compressed_rle_file(self, file_path_to_compress, is_dir):
        """given the compressed file path ,compressed  it (with rle algorithm),
         and return the compressed file"""
        compress_file_data = b""
        NUM_OF_BYTES_TO_COUNT = 2
        with open(file_path_to_compress, "rb") as file_data:
            # get the list of sequences appearances:
            RLE_file_list = self.encode_rle_data(file_data.read())
            # convert it to byte string:
            for count, byte_seq in RLE_file_list:
                # the counter take 2 bytes:
                count_bytes = count.to_bytes(length=NUM_OF_BYTES_TO_COUNT,
                                             byteorder="little")
                compress_file_data += count_bytes + byte_seq

        compress_file_size = len(compress_file_data)
        # create the header:
        header_args = file_path_to_compress, compress_file_size, is_dir
        rle_file_header = RleFileHeader(*header_args, to_bytes=True)
        rle_file_header_bytes = rle_file_header.to_bytes()

        return (rle_file_header_bytes + compress_file_data,
                compress_file_size + len(rle_file_header_bytes))  # include the header

    def calc_num_of_files_inside_dirs(self):
        """"go over the dict of dirctory and calculate how many fies are insdie each directory"""
        count_files = 0
        for dir in self.dirs_to_compress:
            count_files += len(self.dirs_to_compress[dir])
        return count_files

    def calculate_checksum(self, archive_file_data: bytes) -> bytes:
        """given data in bytes, return the checksum of it"""
        return hashlib.md5(archive_file_data).digest()

    def encode_RLE(self,**kwargs) -> str:
        """
        Encodes and compresses files using RLE, creates an archive with header and encryption.
        """

        self.archive_size = 0  # Reset archive size

        start = time.time()  # Start time for compression timing

        archive_file_data = b""  # Empty byte string for combined compressed data
        archive_file_size = 0  # Variable to track total compressed file size

        # Compress individual files
        for file_path_to_compress in self.files_to_compress:
            current_compressed_file, current_comp_file_size = self.get_compressed_rle_file(
                file_path_to_compress, False  # Not part of a directory
            )
            archive_file_size += current_comp_file_size  # Update total size
            archive_file_data += current_compressed_file  # Append compressed data

        # Compress files within directories
        for dir in self.dirs_to_compress:
            for file_path_to_compress in self.dirs_to_compress[dir]:
                current_compressed_file, current_comp_file_size = self.get_compressed_rle_file(
                    file_path_to_compress, True  # Part of a directory
                )
                archive_file_size += current_comp_file_size  # Update total size
                archive_file_data += current_compressed_file  # Append compressed data

        end = time.time()  # End time for compression timing
        self.time_to_compress = end - start  # Calculate compression time

        # Create archive header
        header_args = (
            self.calculate_checksum(self.password),
            self.key,
            self.calculate_checksum(archive_file_data),
            "RLE",
            self.byte_seq_len,
            archive_file_size,
            len(self.files_to_compress) + self.calc_num_of_files_inside_dirs(),
        )
        archive_file_header = ArchiveHeader(*header_args, to_bytes=True)

        # Encrypt compressed data
        encrypt_compressed_archve_file = self.encrypt_data(archive_file_data)

        # Calculate final archive size
        archive_file_header_bytes = archive_file_header.to_bytes()
        self.archive_size += archive_file_size + len(archive_file_header_bytes)

        # Write archive to file
        with open(self.archive_path, "wb") as archive_file:
            archive_file.write(archive_file_header_bytes + encrypt_compressed_archve_file)

        # Print compression statistics
        if "compress" in kwargs:
            print(
                f"Time took to compress: {self.time_to_compress:.2f} seconds\n"
                f"Files sizes before compression - {self.files_size} bytes\n"
                f"Files sizes after compression - {self.archive_size} bytes\n"
                f"After encryption size - {os.path.getsize(self.archive_path)} bytes\n"
        )
        return f"Time took to compress: {self.time_to_compress} seconds\n  files sizes before compression - {self.files_size} bytes \n files sizes after compression - {self.archive_size}  bytes\n after encryption size - {os.path.getsize(self.archive_path)} bytes\n"


    def encrypt_data(self,data):
        """Encrypts a binary string and returns the encrypted data and key."""
        # Generate a secure encryption key
        # Encrypt the data
        f = Fernet(self.key)
        encrypted_data = f.encrypt(data)

        return encrypted_data

    def valid_checksum(self):
        """read the file header extract the checksum and calculate the checksum from the data and compare them
        and return whether or not they are equal"""
        with open(self.archive_path, "rb") as file:
            header = ArchiveHeader(file, from_bytes=True)
            cacl_checksum = self.calculate_checksum(file.read())
            checksum = header.checksum

        if cacl_checksum != checksum:
            raise IOError("Checksum mismatch! Potential file corruption detected.\n"
                          "The calculated checksum doesn't match the stored checksum.")

    def extract_data_RLE(self, file_size, archive_file, byte_seq_len):
        """
        Extracts data from an archive file using the Run-Length Encoding (RLE) compression algorithm.

        Parameters:
        - file_size: The size of the file to be extracted.
        - archive_file: The archive file object from which data will be extracted.
        - byte_seq_len: The length of the byte sequence used in RLE compression.

        Returns:
        - A list containing tuples of (count, sequence) representing the extracted data.

        Raises:
        - IOError: If potential file corruption is detected due to mismatched file sizes.
        """
        file_data = []
        COUNT_BYTES = 2
        current_file_size = 0

        while file_size != current_file_size:
            # Read count byte
            count_byte = archive_file.read(COUNT_BYTES)

            # Convert count byte to integer
            count = int.from_bytes(count_byte, byteorder="little")

            # Read sequence of bytes
            if current_file_size + COUNT_BYTES + byte_seq_len > file_size:
                reminder_bytes = file_size - (current_file_size + COUNT_BYTES)
                seq_of_data = archive_file.read(reminder_bytes)
                current_file_size += COUNT_BYTES + reminder_bytes
            else:
                seq_of_data = archive_file.read(byte_seq_len)
                current_file_size += COUNT_BYTES + byte_seq_len

            # Append (count, sequence) tuple to data
            file_data.append((count, seq_of_data))

            # Check for potential file corruption
            if current_file_size > file_size:
                raise IOError("Potential file corruption detected.\n"
                              "File size doesn't match its actual size")

        return file_data

    def decrypt_data(self,key,encrypted_data):
        """Decrypts encrypted data using the provided key and returns the original data."""
        try:
            # Create a Fernet object with the decryption key
            f = Fernet(key)

            # Decrypt the data
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data
        except:
            raise IOError("Potential file corruption detected.\n"
                          "Cant decrypt the file")

    def extract_RLE(self, extract_dir_path, **kwargs):
        """
        Extracts files from the archive using the Run-Length Encoding (RLE) compression algorithm.

        Parameters:
        - extract_dir_path: The path to the directory where the extracted files will be saved.
        - **kwargs: Additional keyword arguments.

        Returns:
        - A string indicating the time taken to extract the files.

        Raises:
        - IOError: If checksum mismatch is detected, indicating potential file corruption.
        """
        # Start time measurement
        start = time.time()

        # Dictionary to store extracted files
        dict_files = {}

        # Open the archive file for reading in binary mode
        with open(self.archive_path, "rb") as archive_file, tempfile.TemporaryFile(mode='w+b') as decrypted_archive:
            # Read and parse the archive header
            arch_header = ArchiveHeader(archive_file, from_bytes=True)

            # Decrypt the archive data
            decrypted_file_data = self.decrypt_data(arch_header.key, archive_file.read())

            # Verify checksum to detect potential file corruption
            if self.calculate_checksum(decrypted_file_data) != arch_header.checksum:
                raise IOError("Checksum mismatch! Potential file corruption detected.\n"
                              "The calculated checksum doesn't match the stored checksum.")

            # Write decrypted data to temporary file
            decrypted_archive.write(decrypted_file_data)
            decrypted_archive.seek(0)  # Move the file pointer to the beginning

            # Extract files from the archive
            for file in range(arch_header.number_of_files):
                # Read and parse the RLE file header
                rle_header = RleFileHeader(decrypted_archive, from_bytes=True)

                # Extract file data using RLE compression
                dict_files[rle_header.file_path] = (
                    rle_header.is_dir,
                    self.extract_data_RLE(rle_header.compress_file_size, decrypted_archive, arch_header.byte_seq_len)
                )

        # Write the extracted files to the specified directory
        self.write_extracted_files_RLE(extract_dir_path, dict_files)

        # End time measurement
        end = time.time()
        self.time_to_extract = end - start

        # Print or return the time taken to extract files based on kwargs
        if "extract" in kwargs:
            print(f"time took to extract: {self.time_to_extract} seconds")

        return f"time took to extract: {self.time_to_extract} seconds"

    def write_extracted_files_RLE(self, extract_dir_path, dict_files):
        """
        Writes extracted files to the specified directory after RLE decompression.

        Parameters:
        - extract_dir_path: The path to the directory where the extracted files will be saved.
        - dict_files: A dictionary containing information about the extracted files.

        Returns:
        - None
        """
        is_dir_index = 0  # Index to identify if the extracted file is a directory
        main_extarct_path = extract_dir_path  # Store the main extract directory path

        # Iterate over each file in the dictionary
        for file in dict_files:
            if dict_files[file][is_dir_index]:  # Check if the file is under a directory
                # Extract the directory name from the file path
                dir_name = self.get_dir_name(file).split("/")[0]
                # Append the directory name to the extract directory path
                extract_dir_path += "/" + dir_name
                # If the directory does not exist, create it
                if not os.path.isdir(extract_dir_path):
                    os.mkdir(extract_dir_path)

            # Open the file for writing in binary mode
            with open(f"{extract_dir_path}/{self.get_filename(file)}", "wb") as f:
                file_data = dict_files[file][1]  # Get the data of the file
                raw_data = b""  # Initialize a variable to store the raw data
                # Iterate over each (count, sequence) tuple in the file data
                for count, seq in file_data:
                    # Append the sequence to the raw data 'count' times
                    for i in range(count):
                        raw_data += seq
                # Write the raw data to the file
                f.write(raw_data)

            # Reset the extract directory path to the main extract directory path for the next file
            extract_dir_path = main_extarct_path
    @password_check
    def compress(self, *args, **kwargs):
        """
        Compresses the specified files and directories into an archive file.

        Parameters:
        - args: Positional arguments representing file paths to compress.
        - kwargs: Keyword arguments containing additional parameters for compression.

        Keyword Arguments:
        - password: Password for encryption.
        - encoding: Compression encoding method (HUF or RLE).
        - byte_seq_len: Number of bytes in a single unit (for RLE).
        - dir: List of directory paths to compress.

        Returns:
        - Compressed data or archive file, depending on the compression method.
        """
        self.archive_size = 0  # Initialize the archive size

        # Check if an archive file with the same name already exists
        if os.path.isfile(self.archive_path) and "override" not in kwargs:
            raise ValueError("There is already an archive file with the name you provided")
        elif os.path.isfile(self.archive_path) and "override" in kwargs:
            # Remove the existing archive file if 'override' flag is provided
            os.remove(self.archive_path)

        # If directories are specified, validate and add files from those directories
        if "dir" in kwargs:
            for dir in kwargs["dir"]:
                try:
                    os.listdir(dir)
                except FileNotFoundError:
                    raise FileNotFoundError(f"The directory '{dir}' does not exist.")
                except OSError as e:
                    raise OSError(f"An error occurred while accessing the directory '{dir}': {e}") from e
                # Get the file paths from the directory and add them to the list of files to compress
                self.dirs_to_compress[dir] = [f'{dir}/{filename}' for filename in os.listdir(dir)]

        # Add the specified file paths to the list of files to compress
        self.files_to_compress += [file_path for file_path in args]

        # Calculate the total size of the files to be compressed
        self.files_size = self.get_files_size()

        # Set the password for encryption
        self.password = kwargs["password"]

        encoding_method = kwargs["encoding"]  # Get the compression encoding method
        self.key = Fernet.generate_key()  # Generate a key for encryption

        if encoding_method == "HUF":
            # For Huffman encoding, byte sequence length is fixed to 1
            self.byte_seq_len = 1
            return self.compress_Huffman(**kwargs)

        elif encoding_method == "RLE":
            # For RLE encoding, check and set the byte sequence length
            if "byte_seq_len" in kwargs:
                try:
                    self.byte_seq_len = int(kwargs["byte_seq_len"])
                except ValueError:
                    raise ValueError("Not a valid byte sequence length")
            else:
                self.byte_seq_len = 1  # Default byte sequence length is 1
            self.check_byte_seq_len()  # Check if byte sequence length is valid
            return self.encode_RLE(**kwargs)

    def check_byte_seq_len(self):
        """
        Checks if the specified byte sequence length is valid for compression.

        Raises:
        - ValueError: If the byte sequence length is longer than the smallest file size.
        """
        if min(self.file_sizes) < self.byte_seq_len:
            # Raise an error if the byte sequence length is longer than the smallest file size
            raise ValueError(
                f"The byte sequence length is longer than one of the files (should be less than {min(self.file_sizes)})")
        if self.byte_seq_len<1:
            raise ValueError("Byte needs to be at least 1")

    def get_algo(self):
        """
        Retrieves the compression algorithm used for the archive.

        Returns:
        - str: The compression algorithm used ("RLE" or "HUF").

        Raises:
        - ValueError: If the compression algorithm specified in the archive header is invalid.
        """
        # Open the archive file and read the archive header
        with open(self.archive_path, "rb") as archive_file:
            arch_header = ArchiveHeader(archive_file, from_bytes=True)

        # Determine the compression algorithm based on the value in the archive header
        if arch_header.comp_algo == 1:
            return "RLE"
        elif arch_header.comp_algo == 2:
            return "HUF"
        else:
            raise ValueError("Invalid compression algorithm specified in the archive header")

    @password_check
    def extract(self, path_to_dir, **kwargs):
        """
        Extracts files from the archive to the specified directory.

        Args:
        - path_to_dir (str): The path to the directory where the files will be extracted.

        Keyword Args:
        - password (str): The password used to encrypt the archive.

        Returns:
        - str: A message indicating the success of the extraction process.

        Raises:
        - ValueError: If the provided password is incorrect or if there's a chance of file corruption.
        - IOError: If the header of the archive is corrupted or if the compression algorithm specified in the archive is invalid.
        """
        # Set the password for decryption
        self.password = kwargs["password"]

        # Open the archive file and read the archive header
        with open(self.archive_path, "rb") as archive_file:
            arch_header = ArchiveHeader(archive_file, from_bytes=True)

        # Verify the password by comparing MD5 checksums
        if arch_header.md5_password != self.calculate_checksum(self.password):
            raise ValueError("Wrong password (or a chance of file corruption)")

        # Determine the compression algorithm used in the archive
        decoding_method = self.get_algo()

        # Extract files based on the compression algorithm
        if decoding_method == "HUF":
            return self.extract_Huffman(path_to_dir, **kwargs)
        elif decoding_method == "RLE":
            return self.extract_RLE(path_to_dir, **kwargs)
        else:
            raise IOError("Potential file corruption detected.\nThe header of the archive was destroyed")

    def get_added_compressed_files(self, file_path: str, encoding_method: str) -> Tuple[bytes, int, int]:
        """
        Compresses specified files or a directory using the given encoding method and returns the compressed data.

        Args:
            file_path (str): Path to the file or directory to be compressed.
            encoding_method (str): Encoding method to use, either "HUF" for Huffman or "RLE" for Run-Length Encoding.

        Returns:
            A tuple containing:
                - added_comp_files (bytes): The compressed data of the added files.
                - added_size (int): The total size of the compressed files.
                - num_of_files (int): The number of files compressed.

        Raises:
            ValueError: If the encoding method is invalid or if the file path is invalid.
        """

        num_of_files = 0
        added_size = 0
        added_comp_files = b""  # Empty byte string to store combined compressed data

        # Handle directory compression
        if os.path.isdir(file_path):
            for file in os.listdir(file_path):  # Iterate through files in the directory
                # Compress each file in the directory using the specified encoding method
                if encoding_method == "HUF":
                    comp_file, file_size = self.get_compressed_huff_file(f"{file_path}/{file}", True)
                elif encoding_method == "RLE":
                    comp_file, file_size = self.get_compressed_rle_file(f"{file_path}/{file}", True)
                else:
                    raise ValueError(f"Invalid encoding method: {encoding_method}")  # Raise error for unknown method

                added_comp_files += comp_file  # Append compressed data
                added_size += file_size  # Update total size
                num_of_files += 1  # Increment file count

        # Handle single file compression
        elif os.path.isfile(file_path):
            # Compress the single file using the specified encoding method
            if encoding_method == "HUF":
                comp_file, file_size = self.get_compressed_huff_file(file_path, False)
            elif encoding_method == "RLE":
                comp_file, file_size = self.get_compressed_rle_file(file_path, False)
            else:
                raise ValueError(f"Invalid encoding method: {encoding_method}")  # Raise error for unknown method

            added_comp_files += comp_file  # Append compressed data
            added_size += file_size  # Update total size
            num_of_files += 1  # Increment file count

        else:
            raise ValueError(f"Invalid file path: {file_path}")  # Raise error for invalid path

        return added_comp_files, added_size, num_of_files
    @password_check
    def add(self, path: str, **kwargs) -> str:
        """
        Adds a new file to an existing archive, maintaining the original encryption and compression format.

        Args:
            path (str): Path to the file to be added to the archive.
            **kwargs: Additional keyword arguments.

        Returns:
            str: A string containing information about the operation.

        Raises:
            ValueError: If the password is incorrect or if an invalid encoding method is encountered.
        """

        start_time = time.time()  # Record start time for performance measurement
        arc_size_before = os.path.getsize(self.archive_path)  # Get current size of the archive file

        # Open the existing archive file and read its header information
        with open(self.archive_path, "rb") as archive_file:
            archive_header = ArchiveHeader(archive_file, from_bytes=True)
            encrypted_archive_data = archive_file.read()  # Read encrypted data from the archive

        # Validate password by comparing its checksum with the stored checksum in the archive header
        if archive_header.md5_password != self.calculate_checksum(kwargs["password"]):
            raise ValueError("wrong password (or a chance of file corruption)")

        # Extract necessary information from the archive header
        num_of_files = archive_header.number_of_files
        self.byte_seq_len = archive_header.byte_seq_len
        encoding_method = "RLE" if archive_header.comp_algo == 1 else "HUF"

        # Decrypt the existing archive data
        decrypt_file_data = self.decrypt_data(archive_header.key, encrypted_archive_data)
        new_arc_size = len(decrypt_file_data)

        # Get compressed data and information for the new file to be added
        added_comp_files, added_files_size, num_of_added_files = self.get_added_compressed_files(path, encoding_method)

        # Update archive data and information
        self.key = archive_header.key  # Retain the key for encryption
        new_arc_size += added_files_size
        decrypt_file_data += added_comp_files
        num_of_files += num_of_added_files

        # Re-encrypt the updated archive data
        arc_data_encrypted = self.encrypt_data(decrypt_file_data)

        # Calculate checksum for the updated archive data
        checksum = self.calculate_checksum(decrypt_file_data)

        # Prepare updated header information
        header_args = (
            archive_header.md5_password,
            self.key,
            checksum,
            encoding_method,
            self.byte_seq_len,
            new_arc_size,
            num_of_files,
        )
        archive_file_header = ArchiveHeader(*header_args, to_bytes=True)
        new_arc_header_bytes = archive_file_header.to_bytes()

        # Write the updated header and encrypted archive data back to the archive file
        with open(self.archive_path, "wb") as archive_file:
            archive_file.write(new_arc_header_bytes + arc_data_encrypted)

        end_time = time.time()  # Record end time for performance measurement

        # If specified, print information about the operation
        if "add" in kwargs:
            print(f"before adding, the archive size was: {arc_size_before} bytes\n"
                  f"after adding, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n"
                  f"the adding took: {end_time - start_time} seconds\n")

        # Return a string containing information about the operation
        return f"before adding, the archive size was: {arc_size_before} bytes\n" \
               f"after adding, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n" \
               f"the adding took: {end_time - start_time} seconds\n"

    def update(self, full_path, **kwargs):
        """
        Updates an existing file in the archive with a new version, maintaining the original encryption and compression format.

        Args:
            full_path (str): Full path to the file in the archive that needs to be updated.
            **kwargs: Additional keyword arguments.

        Returns:
            str: A string containing information about the operation.

        Raises:
            ValueError: If the file or directory specified for update doesn't exist in the archive.
        """

        arc_size_before = os.path.getsize(self.archive_path)  # Get current size of the archive file
        start_time = time.time()  # Record start time for performance measurement

        try:
            # Attempt to delete the existing file (or directory) from the archive
            self.delete(self.get_dir_name(full_path), **kwargs)  # If the file is inside a directory
        except:
            try:
                self.delete(self.get_filename(full_path), **kwargs)  # If the file is in the root folder
            except:
                # Raise error if the file or directory to be updated doesn't exist in the archive
                raise ValueError("the file/ directory you gave doesn't appear in the archive "
                                 "(a chance of file corruption)")

        # Add the new version of the file to the archive
        self.add(full_path, **kwargs)

        end_time = time.time()  # Record end time for performance measurement

        # If specified, print information about the operation
        if "update" in kwargs:
            print(f"before updating, the archive size was: {arc_size_before} bytes\n"
                  f"after updating, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n"
                  f"the updating took: {end_time - start_time} seconds\n")

        # Return a string containing information about the operation
        return f"before updating, the archive size was: {arc_size_before} bytes\n" \
               f"after updating, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n" \
               f"the updating took: {end_time - start_time} seconds\n"

    @password_check
    @with_temp_dir
    def delete(self, relative_path, **kwargs):
        """
        Deletes a file or directory from the archive and updates the archive accordingly.

        Args:
            relative_path (str): The relative path to the file or directory to be deleted within the archive.
            **kwargs: Additional keyword arguments.

        Returns:
            str: A string containing information about the operation.

        Raises:
            ValueError: If the provided password does not match the archive's password.
            FileNotFoundError: If the specified file or directory to be deleted does not exist in the archive.
        """
        # Obtain the temporary directory path from keyword arguments
        temp_dir = kwargs["temp_dir"]

        # Print the temporary directory path (for debugging purposes)
        print(temp_dir)

        # Initialize variables to record archive size before deletion and start time
        arc_size_before = os.path.getsize(self.archive_path)
        start_time = time.time()

        # Read archive header information
        with open(self.archive_path, "rb") as archive_file:
            archive_header = ArchiveHeader(archive_file, from_bytes=True)

        # Verify password against the archive's password
        if archive_header.md5_password != self.calculate_checksum(kwargs["password"]):
            raise ValueError("Wrong password (or a chance of file corruption)")

        # Start the timer to measure deletion time
        encoding_method = self.get_algo()  # Determine the encoding method used in the archive
        kwargs["password"] = kwargs["password"].decode()  # Decode password if it's in bytes format

        # Extract archive contents into the temporary directory
        self.extract(temp_dir, **kwargs)

        # Construct the full path to the file or directory to be deleted within the temporary directory
        full_path = f"{temp_dir}/{relative_path}"

        # Check if the specified path corresponds to a file or directory and delete it accordingly
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path, ignore_errors=True)
        else:
            raise FileNotFoundError(
                "The relative path of the file/directory you gave doesn't appear in the archive files")

        # Prepare lists of files and directories in the temporary directory for compression
        files_to_compress = []
        dirs_to_compress = []
        for son in os.listdir(temp_dir):
            son_path = f"{temp_dir}/{son}"
            if os.path.isfile(son_path):
                files_to_compress.append(son_path)
            elif os.path.isdir(son_path):
                dirs_to_compress.append(son_path)

        # Clear the `dirs_to_compress` and `files_to_compress` attributes
        self.dirs_to_compress = {}
        self.files_to_compress = []

        # Compress the updated files and directories back into the archive, overriding the existing archive file
        self.compress(*files_to_compress, encoding=encoding_method, byte_seq_len=archive_header.byte_seq_len,
                      dir=dirs_to_compress, override=True, **kwargs)

        # Record the end time of the operation
        end_time = time.time()

        # If specified, print information about the operation
        if "delete" in kwargs:
            print(f"Before deleting, the archive size was: {arc_size_before} bytes\n"
                  f"After deleting, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n"
                  f"The deletion took: {end_time - start_time} seconds\n")

        # Return a string containing information about the operation
        return f"Before deleting, the archive size was: {arc_size_before} bytes\n" \
               f"After deleting, the new archive size is: {os.path.getsize(self.archive_path)} bytes\n" \
               f"The deletion took: {end_time - start_time} seconds\n"
