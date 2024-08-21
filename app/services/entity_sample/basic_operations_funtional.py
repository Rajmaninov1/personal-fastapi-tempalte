from random import random;
import math

def get_random_integer_number(digits:int):
    num = random.random() * (10**digits)
    return str(math.ceil(num))

def greeting(name:str):
    return f'hello {name}'
