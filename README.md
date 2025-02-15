# 🗜️ Archiver - A Powerful and Feature-Rich Archiving Tool

[![Archiver GUI](https://github.com/DHvaicrker/Compressor/blob/main/Compressor.jpg)](https://github.com/DHvaicrker/Compressor/blob/main/Compressor.jpg)

Archiver is a Python-based archiving utility that goes beyond basic compression.  It offers a comprehensive set of features, including a graphical user interface, robust compression using Huffman's algorithm, support for multiple files and folders, secure encryption, and the ability to update or delete archive contents.

## ✨ Key Features

* **Graphical User Interface (GUI):**  A user-friendly interface allows for easy access to all functionalities, making archiving and extraction a breeze. 💻
* **Huffman Compression:**  Efficiently shrinks files and directories of *any* type (not just text) using a custom implementation of Huffman's algorithm.  🚀
* **Multi-File/Folder Support:**  Compress multiple files and folders together while preserving the original directory structure.  📂
* **Archive Modification:**  Delete or update individual files and folders within an existing archive without needing to re-create the entire archive. 🛠️
* **Symmetric Encryption:** Secure your archives with strong symmetric encryption using the `cryptography` library. 🔒
* **Custom Serialization:**  A unique and efficient format for serializing and deserializing the Huffman tree, enabling seamless compression and decompression. 🌳

## ⚙️ Technical Details

* **Huffman Implementation:**
    * Custom `Node` and `Tree` classes.
    * Tree construction using a priority queue.
    * Serialization:  Tree converted to a custom textual representation, then encoded to UTF-8.
    * Deserialization: UTF-8 decoded, then tree reconstructed from the string.
* **Multi-Folder Support:**
    * Each compressed file includes a header byte indicating whether it's part of a folder.
    * Folder structure recreated during extraction based on file headers and names.
* **Delete/Update Functionality:**
    * Files extracted to a temporary directory.
    * Operations (delete/update) performed on the extracted files.
    * Archive re-created with the modified files.
    * Temporary directory deleted.
* **Password and Encryption:**
    * Password hashed using `haslib.md5` for secure storage within the archive header.
    * Encryption applied to the entire archive file using the `cryptography` library.
* **GUI Implementation:**
    * Main GUI class manages all screens.
    * Separate classes for each screen (compress, delete, add, etc.).
    * Controller class links GUI and backend logic.

## 🚀 How to Run

*(Provide clear and concise instructions on how to run your project.  Include any dependencies and how to install them.)*

```bash
# Example (replace with your actual instructions)
pip install cryptography  # Install necessary dependencies
python main.py      # Run the main script
