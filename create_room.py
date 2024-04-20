from string import ascii_letters
import random

existing_codes = []


def generate_room_code(length):
    while True:
        code_chars = [random.choice(ascii_letters) for i in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            existing_codes.append(code)
            return code