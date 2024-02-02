import json
import pandas as pd
import os
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
KAFKA_HOST = "localhost"    #服务器地址
KAFKA_PORT = 9092       #端口号
KAFKA_TOPIC = "test"  #topic
API_VERSION = (3, 5, 1)
data=pd.read_csv(os.getcwd()+'\\connector\\score.csv')
key_value=data.to_json()        # str类型

''' Only used for learing. Not for the project.'''


class Kafka_producer():
    def __init__(self, kafkahost, kafkaport, kafkatopic, key):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.key = key
        self.producer = KafkaProducer(bootstrap_servers=
                                      '{kafka_host}:{kafka_port}'.format(
                                          kafka_host=self.kafkaHost,
                                          kafka_port=self.kafkaPort),
                                          api_version=API_VERSION
                                          )
    def sendjsondata(self, params):
        try:
            parmas_message = params
            producer = self.producer
            print('sending...')
            producer.send(self.kafkatopic, key=self.key, value=parmas_message.encode('utf-8'))
            print('flushing...')
            producer.flush()
        except KafkaError as e:
            print(e)


class Kafka_consumer():
    def __init__(self, kafkahost, kafkaport, kafkatopic, groupid,key):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.groupid = groupid
        self.key = key
        self.consumer = KafkaConsumer(self.kafkatopic, group_id=self.groupid,bootstrap_servers='{(kafka_host}:{kafka_port}'.format(
            kafka_host=self.kafkaHost,
            kafka_port=self.kafkaPort)
        )
    def consume_data(self):
        try:
            for message in self.consumer:
                yield message
        except:
            pass


def sortedDictValues(adict):
    items = adict.items()
    items=sorted(items,reverse=False)
    return [value for key, value in items]


def main(xtype, group, key):
    if xtype == "p":
        #生产模块
        producer = Kafka_producer(KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC, key)
        print("===========>producer:", producer)
        params =key_value
        producer.sendjsondata(params)
    if xtype == 'c':
        #消费模块
        consumer = Kafka_consumer(KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC, group,key)
        print("===========> consumer:", consumer)
        message = consumer.consume_data()
        for msg in message:
            msg=msg.value.decode('utf-8')
            print(msg)
            python_data=json.loads(msg)#tt字符串转换成字典
            key_list=list(python_data)
            test_data=pd.DataFrame()
            for index in key_list:
                if index=='Name':
                    a1=python_data[index]
                    data1 = sortedDictValues(a1)
                    test_data[index]=data1
                else:
                    a2 = python_data[index]
                    data2 = sortedDictValues(a2)
                    test_data[index] = data2
            print(test_data)


# 数据在kafka的传输
# 结构化数据，在python中表示为dict
# 将数据传输到kafka，经过的数据转化为
# dict→json(str)→bytes
# 其中, json是有组织格式的str
# str和bytes之前转化，通过编码解码实现
# 即str编码为bytes, bytes解码为str
# kafka服务器存储的数据就是bytes
# 从kafka接收数据是反过来的
# 接收到bytes, 解码为str, 并加载为dict(python中这个加载过程是json.loads())

# if __name__=='__main_ ':
main(xtype='p',group='py_test',key=None)
main(xtype='c',group='py_test',key=None)
