'''
@author: Kosh
'''
import csv
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
        with open(config['file'], 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = ' ')
    
            for row in reader:
                self.fullData.append(row)
        
        if config['shuffle']:
            shuffle(self.fullData)

    def process(self, inData, inMeta):
#         print('getRowFromCSV.process')
        data = []
        config = self.config
        count = len(self.fullData)
        offset = randint(count * config['from'], count * config['to'] - 1)
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
            
            