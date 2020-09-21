'''
@author: Kosh
'''
import csv
import sys
from random import shuffle, randint

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Считываем csv файл мешаем его, делаем выборку
    '''

    def init(self):
#         print('getRowFromCSV.init')
        self.fullData = []
        config = self.config
        delimiter = config.get('delimiter', ' ')
        csv.field_size_limit(1024*1024)
        
        with open(config['file'], 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = delimiter)
            i = 0
            for row in reader:
                self.fullData.append(row)
                i += 1
                if (i > 1000000):
                    break;
             
        if config.get('shuffle', False):
            shuffle(self.fullData)

    def process(self, inData, inMeta):
#         print('getRowFromCSV.process')
        data = []
        config = self.config
        count = len(self.fullData)
        getFrom = config.get('from', 0.0)
        getTo = config.get('to', 1.0)
        offset = randint(count * getFrom, count * getTo - 1)
        data.append({'row':self.fullData[offset]})
        return data

    def send(self, outData, outMeta):
        config = self.config
        if 'metaIdField' in config:
            # если надо внедрять идентификатор 
            # то для каждого куска данных делаем отправку отдельно
            for data in outData:
                outMeta.update({'id':data['row'][int(config['metaIdField'])]})
#                 print('putting')
#                 print(data)
#                 print(self.outs)
                super().send([data], outMeta)
        else:
            super().send(outData, outMeta)
            
            