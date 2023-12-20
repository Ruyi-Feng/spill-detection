from rsu_simulator import Smltor


def test_simulator():
    p = './data/result.txt'
    s = Smltor(p)

    while True:
        msg = s.run()
        if msg == '':
            break

    assert type(msg) == str
