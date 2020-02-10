'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.mapReduce.map import Pool, Worker as Base
from typing import Iterable
from time import sleep
class Worker(Base):
    def emit(self, values):

        buffer = {}
        for value in values:
#             value = values[i]        
            key = []
            for i in self.keyConfig:
                key.append(value[i])
            
            val = value[self.valueConfig]
            
#             print(self.keyConfig, key)
            strKey = '_'.join(key)
            
            if not strKey in buffer:
                buffer[strKey] = (key, [])
            buffer[strKey][1].append(val)
        
#         print(buffer)
        return list(buffer.values())
