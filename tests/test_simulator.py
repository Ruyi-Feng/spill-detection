from rsu_simulator import Smltor
from pathlib import Path


def test_simulator():
    p = (Path(__file__) / './../../data/result.txt').resolve()
    s = Smltor(str(p))

    while True:
        msg = s.run()
        if msg == '':
            break

    return msg


if __name__ == "__main__":
    msg = test_simulator()
    assert type(msg) == str
