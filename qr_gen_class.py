import codecs

from numpy.ma.core import masked

import qr_raw_data as raw
from icecream import ic
import numpy as np

from reedsolo import RSCodec


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
        self.format_strip = ''

        self.mask_id = 7

        # Initialise matrix size and version
        self.length = len(data)
        ic(self.length)

        v_list = raw.version_data[data_type][eclevel]
        self.version = self.first_largest(v_list, self.length)
        ic(self.version)
        self.size = 17 + (self.version * 4)
        self.matrix = np.empty((self.size, self.size), dtype=object)

    def __repr__(self):

        mapping = {"1": "█", "0": " ", "i": "▓", "o": "░", "f": "f", "v": "v",  }

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

        self.full_binary = self.add_reed_solomon_code(self.full_binary)

        ic(self.full_binary)



    def encode(self):
        if self.data_type == "numeric":
            self.encode_numeric()
        elif self.data_type == "alphanumeric":
            self.encode_alphanumeric()
        elif self.data_type == "bytes":
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

    def add_unchanging_bit(self):
        self.matrix[((4*self.version)+9)][8] = 1

    def reserve_format_strip(self):
        for i in range(8):
            if self.matrix[8][i] == None:
                self.matrix[8][i] = "f"
            if self.matrix[8][self.size - 8 + i] == None:
                self.matrix[8][self.size - 8 + i] = "f"
            if self.matrix[i][8] == None:
                self.matrix[i][8] = "f"
            if self.matrix[self.size - 8 + i][8] == None:
                self.matrix[self.size - 8 + i][8] = "f"
        self.matrix[8][8] = "f"

    def reserve_version_info(self):
        if self.version >= 7:
            print("QR codes Version 7 and above are not supported yet")

    def place_data(self):
        ic("placing data")
        toadd = self.full_binary
        colomnpart = -1 #-1 is right , 1 is left
        upordown = -1 # -1 is up and 1 is down
        currentx = self.size-1
        currenty = self.size-1
        while len(toadd) > 0:

            if currenty == -1 or currenty == self.size:
                currenty -= upordown
                currentx -= 2
                colomnpart = -1
                upordown *= -1

            if self.matrix[currenty][currentx] is None:
                self.matrix[currenty][currentx] = toadd[0]

                toadd = toadd[1:]

            if colomnpart == 1:
                colomnpart = -1
                currenty += upordown
                currentx += 1
            elif colomnpart == -1:
                colomnpart = 1
                currentx -= 1

    def add_reed_solomon_code(self, current_full):
        ec_blocks = raw.error_correction_blocks[self.version][self.eclevel]
        byte_array = []
        for i in range(0, len(current_full), 8):
            byte = current_full[i:i + 8]
            byte_array.append(int(byte, 2))

        rs = RSCodec(ec_blocks)
        encoded_data = rs.encode(byte_array)
        return ''.join(f"{byte:08b}" for byte in encoded_data).replace("1", "i").replace("0", "o")

    def apply_mask(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.matrix[i][j] == "i":
                    if self.mask_pattern(self.mask_id, i, j):
                        self.matrix[i][j] = "o"

                elif self.matrix[i][j] == "o":
                    if self.mask_pattern(self.mask_id, i, j):
                        self.matrix[i][j] = "i"


    def mask_pattern(self, mask_id, i, j):
        if mask_id == 0:
            return (i + j) % 2 == 0
        elif mask_id == 1:
            return i % 2 == 0
        elif mask_id == 2:
            return j % 3 == 0
        elif mask_id == 3:
            return (i + j) % 3 == 0
        elif mask_id == 4:
            return (i // 2 + j // 3) % 2 == 0
        elif mask_id == 5:
            return (i * j) % 2 + (i * j) % 3 == 0
        elif mask_id == 6:
            return ((i * j) % 2 + (i * j) % 3) % 2 == 0
        elif mask_id == 7:
            return ((i + j) % 2 + (i * j) % 3) % 2 == 0
        else:
            raise ValueError("Invalid mask_id")

    def add_format_strip(self):
        # add error correction level
        if self.eclevel not in raw.error_correction_bits or not (0 <= self.mask_id <= 7):
            raise ValueError("Invalid EC level or mask ID")

        # Step 1: Combine EC level and mask ID
        ec_bits = raw.error_correction_bits[self.eclevel]
        mask_bits = f"{self.mask_id:03b}"
        combined_bits = ec_bits + mask_bits

        # Step 2: Polynomial division (XOR)
        generator = 0b10100110111  # Generator polynomial
        combined_int = int(combined_bits, 2) << 10  # Shift left by 10 bits for division
        for i in range(len(combined_bits)):
            if combined_int & (1 << (14 - i)):  # Check the highest bit
                combined_int ^= generator << (4 - i)

        # Step 3: Add remainder (10 bits)
        error_bits = combined_int & 0b1111111111  # Last 10 bits
        format_bits = int(combined_bits, 2) << 10 | error_bits

        # Step 4: Apply masking XOR pattern
        mask_pattern = 0b101010000010010
        final_format = format_bits ^ mask_pattern

        # Convert to 15-bit binary string
        self.format_strip =  f"{final_format:015b}"
        ic(self.format_strip)







if __name__ == "__main__":
    import qr_gen_tester












