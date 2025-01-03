from qr_gen_class import QR_Code_String

generator = QR_Code_String(
    "bytes", "Hello World!", "L")
generator.encode()
generator.build_string()




print(generator, "\n\n\n\n")
generator.add_positions()
print(generator, "\n\n\n\n")
generator.add_padding()
print(generator, "\n\n\n\n")
generator.add_timing()
print(generator, "\n\n\n\n")
generator.add_alignment()
print(generator, "\n\n\n\n")
generator.add_unchanging_bit()
generator.reserve_format_strip()
generator.reserve_version_info()
print(generator, "\n\n\n\n")
generator.place_data()
print(generator, "\n\n\n\n")
generator.apply_mask()
print(generator, "\n\n\n\n")
generator.add_format_strip()