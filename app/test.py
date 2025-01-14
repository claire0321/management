import random
import string
from dataclasses import dataclass


def generate_id() -> str:
    return "".join(random.choices(string.ascii_uppercase, k=12))


@dataclass
class Icecream:
    name: str
    flavor: str


def main() -> None:
    icecream = Icecream(name="together", flavor="vanilla")
    print(icecream)


if __name__ == "__main__":
    main()
