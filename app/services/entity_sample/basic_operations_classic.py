from random import random;
import math

class SampleMessageList:
    """ """

    def __init__(
            self,
            *,
            list_name: str,
            list_code_prefix: str
    ):
        self.list_name: str = list_name
        self.list_code: int = list_code_prefix + self.get_random_number()
        self.list = []

    def get_random_number():
        num = random.random() * 100000000000
        return str(math.ceil(num))
    
    def add_message(
            self,
            *,
            message: str):
        self.list.append(message)

    def print_messages(self):
        print(self.list)
