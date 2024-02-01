from kafka import KafkaConsumer
from requests import post
import json 

'''Connect the server and algorithms by Kafka.'''


class KafkaConsumer():
    '''class KafkaConsumer

    properties
    ----------
    consumer: KafkaConsumer, kafka消费者
    用法:
    message = consumer.run()
    从broker接收数据, 得到message
    '''
    def __init__(self, ip, topic, groupid='kafka', key=None):
        '''function __init__

        input
        -----
        ip: str, kafka接收数据的ip地址
        topic: str, kafka接收数据的topic
        groupid: str, kafka接收数据的groupid
        key: str, kafka接收数据的key
        '''
        self.consumer = KafkaConsumer(topic, bootstrap_servers=ip,
                                      group_id=groupid)

    def run(self) -> dict:
        '''function run

        output
        ------
        message: dict, kafka接收到的数据
        '''
        try:
            for message in self.consumer:
                msgStr = message.value.decode('utf-8')
                msgDict = json.loads(msgStr)
                yield msgDict
        except:
            # pass
            yield None


class HttpPoster():
    '''class HttpPoster

    properties
    ----------
    url: str, http上报的url
    用法:
    poster = HttpPoster(url)
    poster.run(data)
    将data上报到url
    '''
    def __init__(self, url):
        '''function __init__

        input
        -----
        url: str, http上报的url
        '''
        self.url = url

    def run(self, events: list):
        pass

    def postData(self, data: dict):
        '''function run

        input
        -----
        data: dict, 需要上报的数据

        将字典格式的数据以POST形式上传给http
        '''
        post(self.url, data=data)
