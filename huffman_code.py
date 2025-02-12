from queue import PriorityQueue


class Node:
    def __init__(self, char=None, frequency=0, left_node=None, right_node=None):
        """
        Initializes a node in the Huffman tree.

        Parameters:
        - char: The character stored in the node. Defaults to None.
        - frequency: The frequency of occurrence of the character. Defaults to 0.
        - left_node: The left child node. Defaults to None.
        - right_node: The right child node. Defaults to None.
        """
        if left_node == None and right_node == None:
            self.frequency = frequency
            self.char = char
        else:
            self.frequency = left_node.frequency + right_node.frequency
            self.char = None
        self.left_node = left_node
        self.right_node = right_node

    def get_freq(self):
        """
        Returns the frequency of the node.

        Returns:
        - The frequency of the node.
        """
        return self.frequency

    def __lt__(self, other):
        """
        Overrides the less than comparison operator.
        Compares nodes based on their frequencies.

        Parameters:
        - other: The other node to compare against.

        Returns:
        - True if this node's frequency is less than the other node's frequency, False otherwise.
        """
        return self.frequency < other.frequency


class Huffman:
    def __init__(self, text):
        """
        Initializes the Huffman object with the given text.

        Parameters:
        - text: The input data to be encoded.
        """
        self.text = text
        self.root = None
        self.char_count_dict = {}
        self.count_chars()
        self.huffman_code_dict = {}
        self.tree_index = 0

    def count_chars(self):
        """
        Counts the occurrences of each character in the input text and stores them in char_count_dict.
        """
        for char in self.text:
            if char in self.char_count_dict:
                self.char_count_dict[char] += 1
            else:
                self.char_count_dict[char] = 1

    def create_tree(self):
        """
        Constructs the Huffman tree based on the character frequencies.
        """
        priority_queue = PriorityQueue()
        for char in self.char_count_dict:
            leaf = Node(char, self.char_count_dict[char])
            priority_queue.put(leaf)
        while priority_queue.qsize() > 1:
            priority_queue.put(Node(None, 0, priority_queue.get(), priority_queue.get()))
        self.root = priority_queue.get()

    def is_leaf(self, node):
        """
        Checks if a given node is a leaf node (i.e., has no children).

        Parameters:
        - node: The node to be checked.

        Returns:
        - True if the node is a leaf node, False otherwise.
        """
        return node.right_node == node.left_node == None

    def encode(self, is_tree_exist=False):
        """
        Encodes the input text using Huffman coding.

        Parameters:
        - is_tree_exist: Indicates whether the Huffman tree has already been created.
                         Defaults to False.

        Returns:
        - The encoded text.
        """
        if not is_tree_exist:
            self.create_tree()
        if self.is_leaf(self.root):
            self.huffman_code_dict[self.root.char] = "0"
        else:
            self.create_huffman_code(self.root, "")
        return self.get_encode_text()

    def create_huffman_code(self, root, code):
        """
        Recursively generates Huffman codes for each character in the Huffman tree.

        Parameters:
        - root: The root node of the current subtree.
        - code: The Huffman code obtained so far.
        """
        if root.right_node == root.left_node == None:
            self.huffman_code_dict[root.char] = code
            return
        self.create_huffman_code(root.left_node, code + "0")
        self.create_huffman_code(root.right_node, code + "1")

    def get_encode_text(self):
        """
        Generates the encoded text using the Huffman codes.

        Returns:
        - The encoded text.
        """
        encode = ""
        for char in self.text:
            encode += self.huffman_code_dict[char]
        return encode

    def decode(self, encoded_string):
        if self.is_leaf(self.root):  # in case of 1 char:
            return int(self.root.char).to_bytes(1, byteorder='little') * self.root.frequency
        current = self.root
        decoded_string = b""
        # go bit bit in the encoded string of 1 and 0 and decode the data using he tree:
        for bit in encoded_string:
            if bit == "0":  # 0 stands for left
                current = current.left_node
            elif bit == "1": # 1 stands for left
                current = current.right_node

            if current.right_node == current.left_node == None:

                decoded_string += int(current.char).to_bytes(1, byteorder='little')
                current = self.root
        return decoded_string

    def serialize(self, root):
        """
        Serialize a Huffman tree into a string representation.

        Args:
        - root: The root node of the Huffman tree.

        Returns:
        - str: A string representation of the Huffman tree.
        explanation : although it is not a recursive function it still act similar to a recursive one because:
        it uses a stack  and convert to string as long as the stack is not empty ,
        as long has there is a node that we didnt go threw
        """
        if not root:
            return None

        stack = [root]
        tree_list = []
        # do it pre order traversal way:
    #  Visit the current node: Visit the root node first.
    #  Traverse the left subtree: Recursively traverse the left subtree.
    #  Traverse the right subtree: Recursively traverse the right subtree.
        SEPERATOR ="sep"
        while stack:
            node = stack.pop()

            # If current node is None, put None symbol
            if node == None:
                tree_list.append("None")
            else:
                # if it is a freqency node:
                if node.char == None:
                    tree_list.append(str(node.frequency))
                else:

                    if node.char == ",":
                        # special treatment if the char is a',' because it could create problems in the deserialize :
                        # the ',' are separators and comma represent the char - ","
                        tree_list.append("comma" + SEPERATOR + str(node.frequency))
                    else:
                        tree_list.append(str(node.char) +SEPERATOR + str(node.frequency))
                # go for the rest the tree
                stack.append(node.right_node)
                stack.append(node.left_node)
        return ",".join(tree_list)

        # Decodes your encoded data to tree.

    def deserialize(self, data):
        """
            Deserialize a string representation of a Huffman tree into the tree structure.

            Args:
            - data (str): The serialized string representation of the Huffman tree.

            Returns:
            - Node: The root node of the reconstructed Huffman tree.
            """
        if not data:
            return None
        arr = data.split(",")
        self.tree_index = 0
        return self.str_to_tree(arr)

    def str_to_tree(self, arr):
        CHAR_INDEX = 0
        FREQ_INDEX=1
        if arr[self.tree_index] == "None":
            return None

        # Create node with this item
        # and recur for children
        if "sep" in arr[self.tree_index]:
            # If the current item contains "sep", it means it represents a node with a character and frequency
            char = arr[self.tree_index].split("sep")[CHAR_INDEX]
            if char == "comma":
                char = ","
            freq = int(arr[self.tree_index].split("sep")[FREQ_INDEX])
            root = Node(char, freq)
        else:
            root = Node(None, int(arr[self.tree_index]))
        # increment the index pointer in the string tree and recursively build the rest of the tree
        self.tree_index += 1
        root.left_node = self.str_to_tree(arr)
        self.tree_index += 1
        root.right_node = self.str_to_tree(arr)
        return root



    def print_inorder(self, root):
        if root:
            self.print_inorder(root.left_node)
            print(root.frequency, root.char, end=" ")
            self.print_inorder(root.right_node)
