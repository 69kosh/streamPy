'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
from typing import Iterable
import pickle
import time
import socket
import csv

class Worker(Base):
    '''
    Воркер для отправки данных по сокету с упаковкой pickle
    '''
    def process(self, inData, inMeta):
#         print('qweqweqwe')
        self.writer.writerow(inData['row'])
#         return [inData]
        return []

    def init(self):
        file = self.config.get('file')
        delimiter = self.config.get('delimiter',' ')
        quotechar = self.config.get('quotechar', '/')
        
        csvfile = open(file, 'w', newline='')
        self.writer = csv.writer(csvfile, delimiter=delimiter,
                            quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)

#     def send(self, outData, outMeta):
#         self.writer.writerow(outData['row'])