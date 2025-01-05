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

        self.build(self.size)

    def __repr__(self):
#▓░
        mapping = {"1": "█", "0": " ", "i": "█", "o": " ", "f": "f", "v": "v",  }

        build = ''
        for row in self.matrix:
            for col in row:
                if col == None:
                    build += "-"
                else:
                    build += mapping[str(col)]
            build += '\n'
        return build

    def build(self, size):
        self.encode()
        self.build_string()

        print(self, "\n\n\n\n")
        self.matrix = self.add_positions(self.matrix, size)
        print(self, "\n\n\n\n")
        self.matrix = self.add_padding(self.matrix, size)
        print(self, "\n\n\n\n")
        self.matrix = self.add_timing(self.matrix, size)
        print(self, "\n\n\n\n")
        self.matrix = self.add_alignment(self.matrix, self.version)
        print(self, "\n\n\n\n")
        self.matrix = self.add_unchanging_bit(self.matrix, self.version)
        self.matrix = self.reserve_format_strip(self.matrix, size)
        self.matrix = self.reserve_version_info(self.matrix, self.version)
        print(self, "\n\n\n\n")
        self.place_data()
        print(self, "\n\n\n\n")
        self.apply_mask()
        print(self, "\n\n\n\n")
        self.add_format_strip()
        print(self, "\n\n\n\n")

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
        self.full_binary += "0" * padding_needed
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

        self.full_binary = self.add_reed_solomon_code2(self.full_binary)

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
        for key, val in sorted(data_dict.items()):
            if val >= value:
                return key
        return max(data_dict.keys())


    @staticmethod
    def add_positions(self, matrix, size):

        pattern = raw.position_pattern

        # Add to the top-left corner
        for i in range(7):
            for j in range(7):
                matrix[i][j] = pattern[i][j]

        # Add to the top-right corner
        for i in range(7):
            for j in range(7):
                matrix[i][size - 7 + j] = pattern[i][j]

        # Add to the bottom-left corner
        for i in range(7):
            for j in range(7):
                matrix[size - 7 + i][j] = pattern[i][j]
        return matrix

    @staticmethod
    def add_padding(self, matrix, size):

        for i in range(8):
            matrix[i][7] = 0
            matrix[i][size - 8] = 0
            matrix[size - 8 + i][7] = 0
        for j in range(7):
            matrix[7][j] = 0
            matrix[size - 8][j] = 0
            matrix[7][size - 7 + j] = 0

        return matrix

    @staticmethod
    def add_timing(self, matrix, size):
        # Add the horizontal timing pattern
        for i in range(8, size - 8):
            matrix[6][i] = (i + 1) % 2

        # Add the vertical timing pattern
        for i in range(8, size - 8):
            matrix[i][6] = (i + 1) % 2

        return matrix

    @staticmethod
    def add_alignment(self, matrix, version):
        if version > 1:

            needed = raw.alignment_pattern_locations[version]
            placements = [(x, y) for x in needed for y in needed]
            placements.pop(0)
            placements.remove((min(needed), max(needed)))
            placements.remove((max(needed), min(needed)))

            ic(placements)
            pattern = raw.alignment_pattern

            for placement in placements:
                for i in range(5):
                    for j in range(5):
                        matrix[placement[0] - 2 + i][placement[1] - 2 + j] = pattern[i][j]
        return matrix

    @staticmethod
    def add_unchanging_bit(self, matrix, version):
        matrix[((4*version)+9)][8] = 1
        return matrix

    @staticmethod
    def reserve_format_strip(self, matrix, size):
        for i in range(8):
            if matrix[8][i] is None:
                matrix[8][i] = "f"
            if matrix[8][size - 8 + i] is None:
                matrix[8][size - 8 + i] = "f"
            if matrix[i][8] is None:
                matrix[i][8] = "f"
            if matrix[size - 8 + i][8] is None:
                matrix[size - 8 + i][8] = "f"
        matrix[8][8] = "f"
        return matrix

    @staticmethod
    def reserve_version_info(self, matrix, version):
        if version >= 7:
            print("QR codes Version 7 and above are not supported yet")

    @staticmethod
    def place_data(self, matrix, size, full_binary):
        ic("placing data")
        toadd = full_binary
        colomnpart = -1 #-1 is right , 1 is left
        upordown = -1 # -1 is up and 1 is down
        currentx = size-1
        currenty = size-1
        while len(toadd) > 0:

            if currenty == -1 or currenty == size:
                currenty -= upordown
                currentx -= 2
                colomnpart = -1
                upordown *= -1

            if matrix[currenty][currentx] is None:
                matrix[currenty][currentx] = toadd[0]

                toadd = toadd[1:]

            if colomnpart == 1:
                colomnpart = -1
                currenty += upordown
                currentx += 1
            elif colomnpart == -1:
                colomnpart = 1
                currentx -= 1

    def add_reed_solomon_code(self, current_full, version, eclevel):
        ec_blocks = raw.error_correction_blocks[self.version][self.eclevel]
        byte_array = []
        for i in range(0, len(current_full), 8):
            byte = current_full[i:i + 8]
            byte_array.append(int(byte, 2))

        rs = RSCodec(ec_blocks)
        encoded_data = rs.encode(byte_array)
        return ''.join(f"{byte:08b}" for byte in encoded_data).replace("1", "i").replace("0", "o")

    def add_reed_solomon_code2(self, current_full):
        # Get the number of data codewords and error correction codewords per block
        ec_blocks = raw.error_correction_blocks[self.version][self.eclevel]
        total_data_codewords = raw.byte_counts[self.version][self.eclevel]
        total_codewords = total_data_codewords + ec_blocks

        # Convert the full binary string into a list of bytes
        data_bytes = [
            int(current_full[i:i + 8], 2) for i in range(0, len(current_full), 8)
        ]

        # Determine the number of blocks
        num_blocks = ec_blocks
        num_data_per_block = total_data_codewords // num_blocks
        extra_data_blocks = total_data_codewords % num_blocks

        # Split into blocks
        blocks = []
        start = 0
        for i in range(num_blocks):
            size = num_data_per_block + (1 if i < extra_data_blocks else 0)
            blocks.append(data_bytes[start:start + size])
            start += size

        # Generate error correction bytes for each block
        rs = RSCodec(ec_blocks)  # Initialize the Reed-Solomon encoder
        ec_blocks_bytes = []
        for block in blocks:
            ec_bytes = rs.encode(block)[-ec_blocks:]  # Generate parity bytes
            ec_blocks_bytes.append(ec_bytes)

        # Interleave data and error correction bytes
        interleaved_data = []
        max_block_len = max(len(block) for block in blocks)

        # Interleave data bytes
        for i in range(max_block_len):
            for block in blocks:
                if i < len(block):
                    interleaved_data.append(block[i])

        # Interleave error correction bytes
        for i in range(ec_blocks):
            for block in ec_blocks_bytes:
                interleaved_data.append(block[i])

        # Convert interleaved data back to binary string
        interleaved_binary = ''.join(f'{byte:08b}' for byte in interleaved_data)
        return interleaved_binary

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
        #calculate the format info
        if self.eclevel not in raw.error_correction_bits or not (0 <= self.mask_id <= 7):
            raise ValueError("Invalid EC level or mask ID")

        #error correct the format strip

        ec_bits = raw.error_correction_bits[self.eclevel]
        mask_bits = f"{self.mask_id:03b}"
        combined_bits = ec_bits + mask_bits

        generator = 0b10100110111  # Generator polynomial
        combined_int = int(combined_bits, 2) << 10
        for i in range(len(combined_bits)):
            if combined_int & (1 << (14 - i)):
                combined_int ^= generator << (4 - i)

        error_bits = combined_int & 0b1111111111
        format_bits = int(combined_bits, 2) << 10 | error_bits

        mask_pattern = 0b101010000010010
        final_format = format_bits ^ mask_pattern

        # Convert to 15-bit binary string
        self.format_strip =  f"{final_format:015b}"
        ic(self.format_strip)

        #add the error corrected format strip to the QR code

        format_bits = [int(bit) for bit in self.format_strip]

        #top left

        for i in range(6):
            self.matrix[8, i] = format_bits[i]

        self.matrix[8, 7] = format_bits[6]
        self.matrix[8, 8] = format_bits[7]
        self.matrix[7, 8] = format_bits[8]

        for i in range(6):
            self.matrix[(5-i), 8] = format_bits[9+i]

        #the rest

        for i in range(7):
            self.matrix[-1-i, 8] = format_bits[i]

        for i in range(8):
            self.matrix[8, -8+i] = format_bits[7+i]


if __name__ == "__main__":
    import qr_gen_tester












