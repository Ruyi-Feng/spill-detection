from rsu_simulator import Smltor
from pathlib import Path


def test_simulator():
    p = (Path(__file__) / './../../data/result.txt').resolve()
    s = Smltor(str(p))

    while True:
        a = s.run()
        if a == '':
            break
        print(a)


if __name__ == "__main__":
    test_simulator()
