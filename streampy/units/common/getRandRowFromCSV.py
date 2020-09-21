'''
@author: Kosh
'''
import csv

from streampy.units.base.pooled import Pool, Worker as Base
from time import sleep

class Worker(Base):
    '''
    Считываем csv файл последовательно несколько батчей, отдаем псевдорандомно их смешав
    '''

    def generator(self):
        config = self.config
        csvfile = open(config['file'], 'r')
        delimiter = config.get('delimiter', ' ')
        reader = csv.reader(csvfile, delimiter = delimiter)
        for row in reader:
            yield row
            
    def init(self):
        # индексируем csv-файл - считываем построчно, запоминаем позиции каждой строки
        # при генерации используем индекс
        self.i = 0
        self.gen = self.generator()
        
    def process(self, inData, inMeta):

        batch = self.config.get('batch', False)
        batchSize = self.config.get('batchSize', 10000)

        
        data = []
        limit = batchSize
        generator = self.gen
        while limit > 0:
            limit -= 1
            try:
                if batch:
                    data.append(generator.__next__())
                else:
                    data.append({'row':generator.__next__()})
            except:
                if len(data) == 0:
                    sleep(1)
                break
             
        self.i += len(data)
        print(self.i)
        
#         print([{'rows':data}])
#         sleep(10)
        if batch:
#             print('rows', len(data))
            return [{'rows':data}]
        else:
            return data

            