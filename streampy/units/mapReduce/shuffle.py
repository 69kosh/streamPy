'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
from time import sleep
from copy import deepcopy
    
class Worker(Base):
    '''
    Сортируем данные по ключу, чтобы редюс работал лучше 
    '''

    def run(self):
        '''
        Нагребаем данных полный буфер или по таймауту 
        его сортируем и отдаем дальше
        Хитрим отдавая половину буфера, тогда есть шанс 
        что остальные опоздавшие подобьют его малым 
        значением а не смешают все карты
        '''
        
        dataBuffer = []
        
        while True:
            inKey = 'emit'
            outKey = 'emit'
            
            timeout = self.config.get('timeout', 1.0)
            size = self.config.get('size', 1000)
            
            
            try:
                while len(dataBuffer) < size :
                    dataBuffer.append(self.ins[inKey].get(block=True, 
                                                        timeout=timeout))
#                 print('dataBuffer', len(dataBuffer))
            except:
#                 print('timeout')
                pass
            
#             print(dataBuffer)
#             # сорируем и отрезаем половину

            packages = sorted(dataBuffer, key=lambda item:item['meta']['key'])
            
            del dataBuffer
            dataBuffer = []
#             print(packages)
#             sleep(10)

            for package in packages:
                if outKey in self.outs:
                    for queue in self.outs[outKey]:
                        queue.put(package)
    
            del packages
                      