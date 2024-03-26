import sys
import os


def txtRead(path: str, sep: str = ',', type: str = 'tuple',
            row_type: str = 'tuple', element_type: str = 'int',
            skip_header: bool = False):
    '''function txtRead

    input
    -----
    path: str, 文件路径
    sep: str, 分隔符, 默认为','
    type: str, 返回类型, 默认为'tuple', 可选为'tuple', 'list', 'dict'
          dict会将每行数据的第一个元素作为key, 其余元素作为value
    row_type: str, 行类型, 默认为'tuple', 可选为'tuple', 'list'
    element_type: str, 元素类型, 默认为'int', 可选为'int', 'float'
    skip_header: bool, 是否跳过首行, 默认为False

    return
    ------
    result: list, 从txt文件中读取的数据。

    从txt文件中读取数据, 返回list
    csv读取排除表头时, 应当设置skip_header为True
    内存占用:tuple < list < ndarray < dataFrame
    若读取出的数据不会被修改, 建议使用tuple, 否则使用list。
    '''
    result = []
    with open(path, 'r') as file:
        if skip_header:
            file.readline()  # 跳过首行的表头
        for line in file:
            line = line.strip().split(sep)
            # 处理元素类型
            if element_type == 'int':
                line = [int(x) for x in line]
            elif element_type == 'float':
                line = [float(x) for x in line]
            else:
                print('element_type error in txtReadList, should be int/float')
                sys.exit()
            # 处理行类型
            if row_type == 'tuple':
                line = tuple(line)
            elif row_type == 'list':
                pass
            else:
                print('row_type error in txtReadList, should be tuple/list')
                sys.exit()
            result.append(line)
    # 处理返回类型
    if type == 'tuple':
        return tuple(result)
    elif type == 'list':
        return result
    elif type == 'dict':
        return {x[0]: x[1:] for x in result}
    else:
        print('type error in txtReadList, should be tuple or list')
        return None


def getRowNum(path: str, skip_header: bool = False):
    '''function getRowNum

    input
    -----
    path: str, 文件路径
    skip_header: bool, 是否跳过首行, 默认为False

    return
    ------
    rowNumber: int, 文件行数

    '''
    with open(path, 'r') as f:
        if skip_header:
            f.readline()    # 跳过首行的csv表头
        rowNumber = 0
        for line in f:
            if line.strip() == '':
                continue    # 跳过空行
            rowNumber += 1
        return rowNumber


def saveTxtLineBytesIndex(path: str, end: str = '\n',
                          skip_header: bool = False):
    '''function csvSaveLineBytesIndex

    input
    -----
    path: str, 文件路径
    end: str, 保存的字符串行尾, default is '\n'
    skip_header: bool, 是否跳过首行, 默认为False

    以字节形式读取文件, 利用seek函数,
    保存每行数据的起始和终止字节位置到文件中.
    当读取csv文件时, 应当设置skip_header为True
    保存的文件名为path+'.index'
    index文件格式:
    0, 10
    10, 20
    '''

    with open(path, 'rb') as f:
        index_path = path + '.index'
        if skip_header:
            f.readline()    # 跳过表头行
        bytes_start = f.tell()
        with open(index_path, 'w') as index_f:
            while True:
                line = f.readline()
                if not line:
                    break
                bytes_end = bytes_start + len(line)
                index_f.write(f'{bytes_start}, {bytes_end}'+end)
                bytes_start = bytes_end


def readTxtByLineBytesIndex(path: str, row_index: str,
                            index_path: str = 'default') -> str:
    '''function readTxtByLineBytesIndex

    input
    -----
    path: str, 文件路径
    row_index: int, 行号
    index_path: str, index文件路径, 默认为path+'.index'

    根据index文件, 从对应的文件中读取指定行的数据
    '''
    with open(path, 'rb') as f:
        bytesIndex = txtRead(index_path)
        bytes_start, bytes_end = bytesIndex[row_index]
        f.seek(bytes_start)
        line = f.read(bytes_end - bytes_start)
        return line.decode('utf-8').strip()


class BigFileReader:
    '''class BigFileReader

    attributes
    ----------
    path: str, 文件路径
    index_path: str, index文件路径
    skip_header: bool, 是否跳过首行
    rowNumber: int, 文件行数
    rowsBytesIndex: list, 每行数据的起始和终止字节位置

    methods
    -------
    getRow(row_index: int) -> str: 根据index文件, 从对应的文件中读取指定行的数据

    专用于读取大文件txt或csv
    '''
    def __init__(self, path: str):
        '''function __init__

        input
        -----
        path: str, 文件路径

        初始化BigFileReader类
        0. 检查文件后缀, 若为csv则会在后续跳过首行的处理
        1. 检查是否有文件的.index文件, 若没有则生成。将index保存为类的属性
        2. 获取该文件的行数
        '''
        # 路径
        self.path = path
        self.index_path = path + '.index'
        # 文件类别
        if path.endswith('.csv'):
            self.skip_header = True
        else:
            self.skip_header = False
        # 行数
        self.rowNumber = getRowNum(path, self.skip_header)
        # 检查index文件
        if not os.path.exists(self.index_path):
            print(f'creating row bytes index file for {path}...', end='    ')
            saveTxtLineBytesIndex(path, skip_header=self.skip_header)
            print('Done.')
        self.rowsBytesIndex = txtRead(self.index_path)

    def getRow(self, row_index: int) -> str:
        '''function getRow

        input
        -----
        row_index: int, 行号

        根据index文件, 从对应的文件中读取指定行的数据
        '''
        bytes_start, bytes_end = self.rowsBytesIndex[row_index]
        with open(self.path, 'rb') as f:
            f.seek(bytes_start)
            line = f.read(bytes_end - bytes_start)
            return line.decode('utf-8').strip()


if __name__ == '__main__':
    # path = r'D:\myscripts\file_read\test2.txt'
    path = r'D:\myscripts\NN_Template-main\datasets\FreewayC-01.csv'

    # 读取文件
    f = open(path, 'r')
    if path.endswith('.csv'):
        f.readline()    # 跳过首行的表头
    reader = BigFileReader(path)
    for i in range(reader.rowNumber):
        print()
        assert reader.getRow(i) == f.readline().strip()
    print('func test is ok!')
