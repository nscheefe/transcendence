import random
import string

def generate_random_string(size=10):
    """Generate a random string of letters and digits with the given size."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size)) 