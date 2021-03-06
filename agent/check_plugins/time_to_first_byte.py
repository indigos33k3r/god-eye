import logging
import asyncio
from agent.check_plugins import AbstractCheckPlugin

# Do khong biet dung thu vien asyncio ntn ca nen em dung thu vien request
# python
import requests
import sys
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class FirstByte(AbstractCheckPlugin):

    @asyncio.coroutine
    def __call__(self, client, dnode):
        logger.info('Caculating time for download first byte...')
        r = requests.get('http://{}'.format(dnode), stream=True)
        total_length = int(r.headers.get('content-length'))
        if total_length is None:
            logger.info("empty file!")
        else:
            start_chunk = time.clock()
            for chunk in r.iter_content(1024):  # 1kB1024 1MB 1048576
                end_chunk = time.clock()
                break

            delta = end_chunk - start_chunk  # time to first byte
            yield from self._queue.put(self.get_result(dnode, delta))
            
    @asyncio.coroutine
    def get_result(self, url, delta):
        """Download and processing data.

        Args:
            url (str): url file download.
            delta (s): time to download first kB.(1024 Byte)
        
        Returns:
            (list) with item 0 : json format for influxdb
        """
        logger.info("Caculation time for download first byte done!")
        return [self.output([self._snode, url, datetime.now(), delta])]

    def output(self, my_array):
        return {
            "measurement": "time_to_first_byte",
            "tags": {
                "snode": "{}".format(my_array[0]),
                "dnode": "{}".format(my_array[1])
            },
            # "time": "{}".format(my_array[2]),
            "fields": {
                "value": my_array[3]
            }
        }
