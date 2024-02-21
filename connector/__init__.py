import requests


'''Connect the server and algorithms by Kafka.'''


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
