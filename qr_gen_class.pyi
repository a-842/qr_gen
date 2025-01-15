from typing import Any, List, Tuple
import numpy as np

class QR_Code_String:
    def __init__(self, data_type: str, data: str, eclevel: int):
        self.data_type: str
        self.data: str
        self.eclevel: int
        self.current_index: int
        self.history: List[Any]
        self.version: int
        self.size: int
        self.binary_data: str
        self.full_binary: str
        self.format_strip: str
        self.mask_id: int
        self.length: int
        self.matrix: np.ndarray

    def __str__(self) -> str: ...

    def build(self) -> List[Any]: ...

    def build_string(self) -> None: ...

    def encode(self) -> None: ...

    def encode_numeric(self) -> None: ...

    def encode_alphanumeric(self) -> None: ...

    def encode_ISO_8859_1(self) -> None: ...

    @staticmethod
    def first_largest(data_dict: dict, value: int) -> int: ...

    @staticmethod
    def add_positions(matrix: np.ndarray, size: int) -> np.ndarray: ...

    @staticmethod
    def add_padding(matrix: np.ndarray, size: int) -> np.ndarray: ...

    @staticmethod
    def add_timing(matrix: np.ndarray, size: int) -> np.ndarray: ...

    @staticmethod
    def add_alignment(matrix: np.ndarray, version: int) -> np.ndarray: ...

    @staticmethod
    def add_unchanging_bit(matrix: np.ndarray, version: int) -> np.ndarray: ...

    @staticmethod
    def reserve_format_strip(matrix: np.ndarray, size: int) -> np.ndarray: ...

    @staticmethod
    def reserve_version_info(matrix: np.ndarray, version: int) -> np.ndarray: ...

    @staticmethod
    def place_data(matrix: np.ndarray, size: int, full_binary: str) -> np.ndarray: ...

    @staticmethod
    def calculate_reed_solomon_code(current_full: str, version: int, eclevel: int) -> str: ...

    @staticmethod
    def apply_mask(matrix: np.ndarray, size: int, mask_id: int) -> np.ndarray: ...

    @staticmethod
    def mask_pattern(mask_id: int, i: int, j: int) -> bool: ...

    @staticmethod
    def add_format_strip(matrix: np.ndarray, mask_id: int, eclevel: int) -> Tuple[np.ndarray, str]: ...
