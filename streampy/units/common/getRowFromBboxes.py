'''
@author: Kosh
'''
import csv
from random import shuffle, randint

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Считываем текстовый файл с multi bounding boxes
    первая строка - имя файла
    вторая строка - кол-во ббоксов
    третья строка+ - сами боксы
    '''

    def init(self):
#         print('getRowFromCSV.init')
        self.fullData = []
        config = self.config
        with open(config['file'], 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = ' ')

            isFilename = True
            isBboxCount = False
            isBbox = 0
            dataRow = {}
            for row in reader:
#                 print(row)
                if isFilename:
                    isFilename = False
                    isBboxCount = True
                    dataRow['filename'] = row[0]
                elif isBboxCount:
                    isBboxCount = False
                    if int(row[0]) > 0:
                        isBbox = int(row[0])
                    else:
                        isBbox = 1
                elif isBbox > 0:
                    isBbox -= 1
                    if 'bboxes' not in dataRow:
                        dataRow['bboxes'] = []
                    dataRow['bboxes'].append(row)
                    if isBbox == 0:
                        isFilename = True
                        self.fullData.append(dataRow)
#                         print(dataRow['filename'])
#                         print(dataRow)
                        dataRow = {}
                        
                    
        
        if config.get('shuffle', False):
            shuffle(self.fullData)
            
        self.count = len(self.fullData)
        self.offset = int(self.count * config.get('from', 0.0))
        
        print(('samples count:', len(self.fullData)))

    def process(self, inData, inMeta):
        data = []
        config = self.config

        if config.get('shuffle', False):
            self.offset = randint(int(self.count * config.get('from', 0.0)), 
                                  int(self.count * config.get('to', 1.0)) - 1)
        else:
            self.offset += 1
            if self.offset > self.count * config.get('to', 1.0) - 1:
                self.offset = int(self.count * config.get('from', 0.0))
            
#         print(self.fullData[offset])
        data.append({'row':self.fullData[self.offset]})
        return data

    def send(self, outData, outMeta):
        config = self.config
        if 'metaIdField' in config:
            # если надо внедрять идентификатор 
            # то для каждого куска данных делаем отправку отдельно
            for data in outData:
                outMeta.update({'id':data['row'][config['metaIdField']]})
#                 print('putting')
#                 print(data)
#                 print(self.outs)
                super().send([data], outMeta)
        else:
            super().send(outData, outMeta)
            
            