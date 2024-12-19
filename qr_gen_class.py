import codecs

import qr_raw_data as raw
from icecream import ic
import numpy as np


class QR_Code_String:

    def __init__(self, data_type, data, eclevel):
        self.data_type = data_type
        self.data = data
        self.eclevel = eclevel
        self.current_index = 0
        self.history = []
        self.version = 0
        self.size = 0
        self.binary_data = ''
        self.full_binary = ''

        # Initialise matrix size and version
        self.length = len(data)
        ic(self.length)

        v_list = raw.version_data[data_type][eclevel]
        self.version = self.first_largest(v_list, self.length)
        ic(self.version)
        self.size = 17 + (self.version * 4)
        self.matrix = np.empty((self.size, self.size), dtype=object)

    def __repr__(self):

        mapping = {"1": "█", "0": " ", "f": "f", "v": "v", }

        build = ''
        for row in self.matrix:
            for col in row:
                if col == None:
                    build += "-"
                else:
                    build += mapping[str(col)]
            build += '\n'
        return build

    def build_string(self):
        # add encoding
        self.full_binary += raw.encodings[self.data_type]
        # add message length
        message_length_binary = bin(self.length)[2:].zfill(8)
        ic(message_length_binary)
        self.full_binary += message_length_binary
        # add actual data
        self.full_binary += self.binary_data
        # add terminator
        self.full_binary += "0000"
        # add padding
        padding_needed = (8 - len(self.full_binary) % 8) % 8
        ic(padding_needed)
        self.full_binary += "0"*padding_needed
        ic(self.full_binary)
        # add excess bytes
        bytes_needed = raw.byte_counts[self.version][self.eclevel]
        ic(bytes_needed)
        f = True
        while len(self.full_binary)/8 != bytes_needed:
            if f:
                self.full_binary += '11101100'
            else:
                self.full_binary += '00010001'
            f = not f

        ic(self.full_binary)



    def encode(self):
        if self.data_type == 0:
            self.encode_numeric()
        elif self.data_type == 1:
            self.encode_alphanumeric()
        elif self.data_type == 2:
            self.encode_ISO_8859_1()

    def encode_numeric(self):
        pass
    def encode_alphanumeric(self):
        pass
    def encode_ISO_8859_1(self):
        encoded = codecs.encode(self.data)
        self.binary_data = ''.join(f'{byte:08b}' for byte in encoded)
        ic(self.binary_data)

    @staticmethod
    def first_largest(data_dict, value):
        for key, val in data_dict.items():
            if val > value:
                return key
        return None

    def add_positions(self):

        pattern = raw.position_pattern

        # Add to the top-left corner
        for i in range(7):
            for j in range(7):
                self.matrix[i][j] = pattern[i][j]

        # Add to the top-right corner
        for i in range(7):
            for j in range(7):
                self.matrix[i][self.size - 7 + j] = pattern[i][j]

        # Add to the bottom-left corner
        for i in range(7):
            for j in range(7):
                self.matrix[self.size - 7 + i][j] = pattern[i][j]

    def add_padding(self):

        for i in range(8):
            self.matrix[i][7] = 0
            self.matrix[i][self.size - 8] = 0
            self.matrix[self.size - 8 + i][7] = 0
        for j in range(7):
            self.matrix[7][j] = 0
            self.matrix[self.size - 8][j] = 0
            self.matrix[7][self.size - 7 + j] = 0

    def add_timing(self):
        # Add the horizontal timing pattern
        for i in range(8, self.size - 8):
            self.matrix[6][i] = (i + 1) % 2

        # Add the vertical timing pattern
        for i in range(8, self.size - 8):
            self.matrix[i][6] = (i + 1) % 2

    def add_alignment(self):
        if self.version > 1:

            needed = raw.alignment_pattern_locations[self.version]
            placements = [(x, y) for x in needed for y in needed]
            placements.pop(0)
            placements.remove((min(needed), max(needed)))
            placements.remove((max(needed), min(needed)))

            ic(placements)
            pattern = raw.alignment_pattern

            for placement in placements:
                for i in range(5):
                    for j in range(5):
                        self.matrix[placement[0] - 2 + i][placement[1] - 2 + j] = pattern[i][j]

    def reserve_format_strip(self):
        for i in range(8):
            if self.matrix[i][8] == None:
                self.matrix[8][i] = "f"
            if self.matrix[i][self.size - 8 + i] == None:
                self.matrix[8][self.size - 8 + i] = "f"







if __name__ == "__main__":
    import qr_gen_tester












