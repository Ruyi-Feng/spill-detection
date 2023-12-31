from rsu_simulator import Smltor


# 通过
def test_simulator():
    p = './data/result.txt'
    s = Smltor(p)

    while True:
        msg = s.run()
        if msg == '':
            break
        # 检查点1
        # 输出数据为字符串或者列表
        assert (type(msg) == str) | (type(msg) == list)
    # 检查点2
    # 数据读取完毕的最后一行为str
    assert type(msg) == str
