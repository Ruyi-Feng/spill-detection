from rsu_simulator import Smltor


# 通过
def test_simulator():
    p = './data/result.txt'
    s = Smltor(p)

    while True:
        msg = s.run()
        if msg == '':
            break
        assert (type(msg) == str) | (type(msg) == list)

    assert type(msg) == str
