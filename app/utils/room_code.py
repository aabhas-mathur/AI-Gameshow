import random
import string


def generate_room_code(length: int = 6) -> str:
    """Generate a random room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))