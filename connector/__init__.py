from kafka import KafkaConsumer
import requests
import json


'''Connect the server and algorithms by Kafka.'''


class MyKafkaConsumer():
    '''class MyKafkaConsumer

    properties
    ----------
    consumer: MyKafkaConsumer, kafka消费者
    用法:
    message = consumer.run()
    从broker接收数据, 得到message
    '''
    def __init__(self, ip, topic, groupid='kafka', producerVersion=(0, 11, 5), key=None):
        '''function __init__

        input
        -----
        ip: str, kafka接收数据的ip地址
        topic: str, kafka接收数据的topic
        groupid: str, kafka接收数据的groupid
        key: str, kafka接收数据的key
        '''
        self.consumer = KafkaConsumer(topic, bootstrap_servers=ip,
                                      api_version=tuple(producerVersion),
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
                # yield msgDict
                return msgDict
        except Exception:
            # pass
            return None
            # yield None


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
        '''function run

        input
        -----
        events: list, 需要上报的事件列表

        将事件列表中的事件以POST形式上传给http.
        按照协议要求, 逐个上报
        '''
        for event in events:
            self.postData(event)
        pass

    def postData(self, data: dict) -> requests.Response:
        '''function run

        input
        -----
        data: dict, 需要上报的数据

        将字典格式的数据以POST形式上传给http
        '''
        r = requests.post(self.url, data=data)
        return r
