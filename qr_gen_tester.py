from qr_gen_class import QR_Code_String

generator = QR_Code_String(
    1, "Hello123 my name is, my name is, mey name is, HELLLLOOOOO", 1)
print(generator, "\n\n\n\n")
generator.add_positions()
print(generator, "\n\n\n\n")
generator.add_padding()
print(generator, "\n\n\n\n")
generator.add_timing()
print(generator, "\n\n\n\n")
generator.add_alignment()
print(generator, "\n\n\n\n")
generator.reserve_format_strip()
print(generator, "\n\n\n\n")
