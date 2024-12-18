import qr_raw_data as raw
from icecream import ic

class QR_Code_String:
    def __init__(self, data_type, data, eclevel):
        self.data_type = data_type  # 0: Numeric, 1: AlphaNumeric, 2: Binary
        self.data = data
        self.current_index = 0
        self.history = []
        self.version = 0
        self.size = 0



        # Initialise matrix size and version
        length = len(data)
		  ic(length)
        v_list = raw.version_data[data_type][eclevel]
        self.version = self.first_largest(v_list, length)
		  ic(self.version)
        self.size = 17 + (self.version * 4)
        self.matrix = [["" for _ in range(self.size)] for _ in range(self.size)]

    def __repr__(self):

    mapping = {1: "█", 0: " ", "v": "v", "":"-"}
    

    return "\n".join(
        "".join(mapping.get(cell, str(cell)) for cell in row) 
        for row in self.matrix
    )


    @staticmethod
    def first_largest(sorted_list, value):

        for i, x in enumerate(sorted_list):
            if x > value:
                return i
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
		for i in range(7):
			self.matrix[8][i] = 0
			self.matrix[self.size - 8]


    def add_timing(self):
         # Add the horizontal timing pattern
        for i in range(8, self.size - 8):
            self.matrix[6][i] = (i+1) % 2

        # Add the vertical timing pattern
        for i in range(8, self.size - 8):
            self.matrix[i][6] = (i+1) % 2

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



























