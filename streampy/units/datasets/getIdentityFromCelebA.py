'''
@author: Kosh
'''
import csv
from random import shuffle, randint

from pprint import pprint 

from streampy.units.base.pooled import Pool, Worker as Base
import time
class Worker(Base):
    '''
    Считываем csv файл мешаем его, делаем выборку
    '''

    def init(self):
        self.data = {}

        config = self.config
        filename = config['filename']
        imagesPath = config.get('imagesPath')
        print('Loading file {}...'.format(filename))
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter = ' ')
            for row in reader:
                if row[1] not in self.data:
                    self.data[row[1]] = {'id': int(row[1]), 'images':[]}
                self.data[row[1]]['images'].append(imagesPath + row[0])
                
    def process(self, inData, inMeta):
        data = []
        try:
            row = self.data.popitem()
            data.append({'identity': row[1]})
        except Exception:
            time.sleep(1)
            pass
        return data
    
    def send(self, outData, outMeta):
        config = self.config
        # если надо внедрять идентификатор 
        # то для каждого куска данных делаем отправку отдельно
#         print(outData)
        for data in outData:
            outMeta.update({'id':data['identity']['id']})
            super().send([data], outMeta)

            