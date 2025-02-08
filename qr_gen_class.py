import codecs

from numpy.ma.core import masked

import qr_raw_data as raw
from icecream import ic
import numpy as np

from reedsolo import RSCodec


class QR_Code_String:

    def __init__(self, data_type, data, eclevel):
        self.format_strip_combined_bits = ""
        self.masks = []
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
        self.useful = []

        self.mask_id = 7

        # Initialise matrix size and version
        self.length = len(data)
        ic(self.length)
        self.useful.append(self.length)

        v_list = raw.version_data[data_type][eclevel]
        ic(v_list)

        self.version = QR_Code_String.first_largest(v_list, self.length)
        ic(self.version)
        self.useful.append(self.version)
        self.size = 17 + (self.version * 4)
        self.useful.append(self.size)
        self.matrix = np.empty((self.size, self.size), dtype=object)
        ic(self.matrix)

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

    def __str__(self):
        st = ""
        for row in self.matrix:
            for bit in row:
                if bit is None:
                    st += "-"
                else:
                    st += str(bit)

            st += "\n"
        return  st

    @staticmethod
    def string(array):
        st = ""
        for row in array:
            for bit in row:
                if bit is None:
                    st += "-"
                else:
                    st += str(bit)

            st += "\n"
        return st


    def build(self):
        self.encode()
        self.build_string()


        self.matrix = self.add_positions(self.matrix, self.size)
        self.history.append(str(self))
        self.matrix = self.add_padding(self.matrix, self.size)
        self.history.append(str(self))
        self.matrix = self.add_timing(self.matrix, self.size)
        self.history.append(str(self))
        self.matrix = self.add_alignment(self.matrix, self.version)
        self.history.append(str(self))
        self.matrix = self.add_unchanging_bit(self.matrix, self.version)
        self.history.append(str(self))
        self.matrix = self.reserve_format_strip(self.matrix, self.size)
        self.matrix = self.reserve_version_info(self.matrix, self.version)
        self.history.append(str(self))
        ic(self)
        self.matrix = self.place_data(self.matrix, self.size, self.full_binary)
        self.history.append(str(self))
        ic(self)
        self.matrix = self.apply_mask(self.matrix, self.size)
        self.history.append(str(self).replace("o", "0").replace("i", "1"))
        ic(self)
        self.matrix, self.format_strip_combined_bits, self.format_strip = self.add_format_strip(self.matrix, self.mask_id, self.eclevel)
        ic(self)
        self.history.append(str(self).replace("o", "0").replace("i", "1"))



    def build_string(self):
        # add encoding
        self.encoding_code = raw.encodings[self.data_type]
        self.full_binary += self.encoding_code
        # add message length
        self.message_length_binary = bin(self.length)[2:].zfill(8)
        ic(self.message_length_binary)
        self.full_binary += self.message_length_binary
        # add actual data
        self.full_binary += self.binary_data
        # add terminator
        self.full_binary += "0000"
        # add padding
        self.padding_needed = (8 - len(self.full_binary) % 8) % 8
        ic(self.padding_needed)
        self.full_binary += "0" * self.padding_needed
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

        self.full_binary = self.calculate_reed_solomon_code(self.full_binary, self.version, self.eclevel)

        ic(self.full_binary)
        ic(len(self.full_binary))





    def encode(self):
        if self.data_type == "numeric":
            self.encode_numeric()
        elif self.data_type == "alphanumeric":
            self.encode_alphanumeric()
        elif self.data_type == "bytes":
            self.encode_ISO_8859_1()

    def encode_numeric(self):
        self.binary_data = ''
        for i in range(0, len(self.data), 3):
            group = self.data[i:i + 3]
            if len(group) == 3:
                self.binary_data += f'{int(group):010b}'  # 3 digits -> 10 bits
            elif len(group) == 2:
                self.binary_data += f'{int(group):07b}'  # 2 digits -> 7 bits
            elif len(group) == 1:
                self.binary_data += f'{int(group):04b}'  # 1 digit -> 4 bits

    def encode_alphanumeric(self):

        self.binary_data = ''
        for i in range(0, len(self.data), 2):
            group = self.data[i:i + 2]
            if len(group) == 2:
                # Two characters -> 11 bits
                value = raw.alphanumeric_table[group[0]] * 45 + raw.alphanumeric_table[group[1]]
                self.binary_data += f'{value:011b}'
            elif len(group) == 1:
                # One character -> 6 bits
                value = raw.alphanumeric_table[group[0]]
                self.binary_data += f'{value:06b}'


    def encode_ISO_8859_1(self):
        encoded = codecs.encode(self.data)
        self.binary_data = ''.join(f'{byte:08b}' for byte in encoded)
        ic(self.binary_data)

    @staticmethod
    def first_largest(data_dict, value):
        for key, val in data_dict.items():
            if val > value:
                return key
        raise Exception("too much data")


    @staticmethod
    def add_positions(matrix, size):

        pattern = raw.position_pattern

       
        for i in range(7):
            for j in range(7):
                matrix[i][j] = pattern[i][j] # Add to the top-left corner
                matrix[i][size - 7 + j] = pattern[i][j] # Add to the top-right corner
                matrix[size - 7 + i][j] = pattern[i][j] # Add to the bottom-left corner

        return matrix

    @staticmethod
    def add_padding(matrix, size):

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
    def add_timing(matrix, size):
        # Add the horizontal timing pattern
        for i in range(8, size - 8):
            matrix[6][i] = (i + 1) % 2

        # Add the vertical timing pattern
        for i in range(8, size - 8):
            matrix[i][6] = (i + 1) % 2

        return matrix

    @staticmethod
    def add_alignment(matrix, version):
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
    def add_unchanging_bit(matrix, version):
        matrix[((4*version)+9)][8] = 1
        return matrix

    @staticmethod
    def reserve_format_strip(matrix, size):
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
    def reserve_version_info(matrix, version):
        if version >= 7:
            print("QR codes Version 7 and above are not supported yet")

        return matrix

    @staticmethod
    def place_data(matrix, size, full_binary):
        ic("placing data")
        ic(size-1)
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

        return matrix

    from reedsolo import RSCodec

    @staticmethod
    def calculate_reed_solomon_code(current_full, version, eclevel):
        # Get the number of error correction codewords required for the given version and error correction level
        ec_blocks = raw.error_correction_blocks[version][eclevel]

        # Convert the binary string into a list of integers (bytes)
        byte_array = [int(current_full[i:i + 8], 2) for i in range(0, len(current_full), 8)]

        # Initialize the Reed-Solomon codec with the number of error correction codewords
        rs = RSCodec(ec_blocks)

        # Encode the data with Reed-Solomon error correction
        encoded_data = rs.encode(byte_array)

        # Convert the encoded data back to a binary string
        binary_string = ''.join(f"{byte:08b}" for byte in encoded_data)

        # Replace '1's with 'i' and '0's with 'o' (if needed for your specific use case)
        binary_string = binary_string.replace("1", "i").replace("0", "o")

        return binary_string

    @staticmethod
    def evaluate_mask(array):
        array = np.array([[0 if x in ['o', 0] else 1 for x in row] for row in array])
        # Rule 1: Find consecutive rows or columns of same color
        def penalty_rule_1(arr):
            penalty = 0
            # Check rows
            for row in arr:
                penalty += count_consecutive(row)
            # Check columns
            for col in arr.T:
                penalty += count_consecutive(col)
            return penalty

        def count_consecutive(line):
            count = 1
            penalty = 0
            for i in range(1, len(line)):
                if line[i] == line[i - 1] and line[i] in [0, 1]:  # Check only binary values
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
            # Check if the last segment has a penalty
            if count >= 5:
                penalty += 3 + (count - 5)
            return penalty

        # Rule 2: Check 2x2 blocks of same color
        def penalty_rule_2(arr):
            penalty = 0
            for y in range(arr.shape[0] - 1):
                for x in range(arr.shape[1] - 1):
                    block = arr[y:y + 2, x:x + 2]
                    if np.all(block == 0) or np.all(block == 1):  # Only binary values
                        penalty += 3
            return penalty

        # Rule 3: Patterns like 1011101 in rows or columns
        def penalty_rule_3(arr):
            penalty = 0
            pattern = [1, 0, 1, 1, 1, 0, 1]

            # Check rows
            for row in arr:
                penalty += count_pattern(row, pattern)

            # Check columns
            for col in arr.T:
                penalty += count_pattern(col, pattern)

            return penalty

        def count_pattern(line, pattern):
            penalty = 0
            for i in range(len(line) - len(pattern) + 1):
                if list(line[i:i + len(pattern)]) == pattern:
                    penalty += 40
            return penalty

        # Rule 4: Balance of black and white pixels
        def penalty_rule_4(arr):
            total_pixels = arr.size
            black_pixels = np.sum(arr == 1)
            percent_black = (black_pixels / total_pixels) * 100
            prev_multiple_5 = int(percent_black // 5) * 5
            next_multiple_5 = prev_multiple_5 + 5
            return min(abs(prev_multiple_5 - 50), abs(next_multiple_5 - 50)) * 10

        # Apply rules to the binary part of the matrix
        binary_array = np.array([[0 if x == 'o' else 1 if x == 'i' else x for x in row] for row in array])

        total_penalty = (
                penalty_rule_1(binary_array) +
                penalty_rule_2(binary_array) +
                penalty_rule_3(binary_array) +
                penalty_rule_4(binary_array)
        )

        return total_penalty


    def apply_mask(self, matrix, size):
        self.masks = []
        for i in range(8):
            attempt = self.attempt_mask(matrix, size, i)
            attempt_penalty = self.evaluate_mask(attempt)
            self.masks.append((QR_Code_String.string(attempt), attempt_penalty))

        def get_key(idx):
            return self.masks[idx][1]

        ic(self.masks)
        best_mask_index = 0
        best_mask_penalty = 9999
        for i, x in enumerate(self.masks):
            if x[1] < best_mask_penalty:
                best_mask_index = i
                best_mask_penalty = x[1]
        ic(best_mask_index)


        best_mask_string = self.masks[best_mask_index][0]
        ic(best_mask_string)
        self.mask_id = best_mask_index+1
        return self.attempt_mask(matrix, size, self.mask_id)


    @staticmethod
    def attempt_mask(matrix, size, mask_id):
        for i in range(size):
            for j in range(size):
                if matrix[i][j] == "i":
                    if QR_Code_String.mask_pattern(mask_id, i, j):
                        matrix[i][j] = "o"

                elif matrix[i][j] == "o":
                    if QR_Code_String.mask_pattern(mask_id, i, j):
                        matrix[i][j] = "i"
        return matrix

    @staticmethod
    def mask_pattern(mask_id, i, j):
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

    @staticmethod
    def add_format_strip(matrix, mask_id, eclevel):
        #calculate the format info
        if eclevel not in raw.error_correction_bits or not (0 <= mask_id <= 7):
            raise ValueError("Invalid EC level or mask ID")

        #error correct the format strip

        ec_bits = raw.error_correction_bits[eclevel]
        mask_bits = f"{mask_id:03b}"
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
        format_strip =  f"{final_format:015b}"
        ic(format_strip)

        #add the error corrected format strip to the QR code

        format_bits = [int(bit) for bit in format_strip]

        #top left

        for i in range(6):
            matrix[8, i] = format_bits[i]

        matrix[8, 7] = format_bits[6]
        matrix[8, 8] = format_bits[7]
        matrix[7, 8] = format_bits[8]

        for i in range(6):
            matrix[(5-i), 8] = format_bits[9+i]

        #the rest

        for i in range(7):
            matrix[-1-i, 8] = format_bits[i]

        for i in range(8):
            matrix[8, -8+i] = format_bits[7+i]

        return matrix, str(combined_bits), format_strip


class QR_Code_Contact(QR_Code_String):
    def __init__(self, data_type, data, eclevel):
        super().__init__(data_type, "Placeholder", eclevel)
        self.fname = ""
        self.lname = ""
        self.title = ""
        self.gender = ""
        self.bday = ""
        self.email = ""
        self.phone = ""
        self.street = ""
        self.city = ""
        self.county = ""
        self.postcode = ""
        self.country = ""
        self.role = ""
        self.org = ""
        self.url = ""
    def build(self):
        self.data = QR_Code_Contact.create_vcard(self.fname, self.lname, self.title, self.gender, self.bday, self.email, self.phone,)
        super().build()
    @staticmethod
    def create_vcard(fname, lname, title, gender, bday, email, phone, street, city, county, postcode, country, role,
                     company, website):
        vcard = f"""BEGIN:VCARD
    VERSION:4.0
    FN:{fname} {lname}
    N:{lname};{fname};;{title};
    GENDER:{gender}
    BDAY:{bday}
    EMAIL:{email}
    TEL;TYPE=cell:{phone}
    ADR;TYPE=HOME:;;{street};{city};{county};{postcode};{country}
    ROLE:{role}
    ORG:{company}
    URL:{website}
    END:VCARD"""
        return vcard

if __name__ == "__main__":
    import server












