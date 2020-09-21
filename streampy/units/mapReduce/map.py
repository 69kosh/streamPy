'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
from typing import Iterable
import copy
from copy import deepcopy
class Worker(Base):
    '''
    Собираем несколько частей в одну, для этого устраиваем "буфер"
    определённо длины, если не собрали до исчерпания буфера - селяви
    '''

    def init(self):
        config = self.config.get('emit', {})
        self.keyConfig = list(config.get('key', 0))
        self.valueConfig = list(config.get('value', 1))

    def process(self, inData, inMeta):
        
#         print('items', inData['item'])
        emits = self.emit(inData['item'])
        data = []
#         print(emits)
        for emit in emits:
#             print(emit)
            data.append({'emit':{'key':'_'.join(emit[0]), 
                                 'rawKey':emit[0], 'value':emit[1]}})

#         print(data)
        return data
#         return []
    
    def emit(self, value):

        
        key = []
        for i in self.keyConfig:
            key.append(value[i])
        
        val = []
        for i in self.valueConfig:
                val.append(value[i])
                
#         val = value[self.valueConfig]
            
        return [(key, [val])]


    def prepareSendPackage (self, outData, outMeta):
#         print(outData)
        data = outData['value']
        meta = deepcopy(outMeta)
        meta['key'] = outData['key']
        meta['rawKey'] = outData['rawKey']
#         print({'data':data, 'meta':meta})
        return {'data':data, 'meta':meta} 
        