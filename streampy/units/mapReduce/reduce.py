'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
import numpy as np
import copy
from time import sleep
import gc
from random import randint
class Worker(Base):
    '''
    Сжимаем данные постопающие, пока ключ не изменился
    '''
    def init(self):

        self.nextPacket = None
        
    def prepare(self):
        '''
        Принимаем, пока не доберёмся до нового ключа в мете, или таймаут не слчится
        '''

        dataBuffer = []
        metaBuffer = None
        currentKey = None
        key = None
        timeout = self.config.get('timeout', 1.0)

        while True:
#             temp = self.ins['emit'].get()
#             del temp
 
            if not None == self.nextPacket:
                dataBuffer.append(self.nextPacket['data'])
                del metaBuffer
                metaBuffer = self.nextPacket['meta']
                del currentKey
                currentKey = self.nextPacket['meta']['key']
                del self.nextPacket
                self.nextPacket = None
             
 
            try:
                del self.nextPacket
                self.nextPacket = self.ins['emit'].get(block=True, 
                                                       timeout=timeout)
                 
#                 print(self.nextPacket)
                del key
                key = self.nextPacket['meta']['key']
                 
                if not currentKey == key:
                    return (dataBuffer, metaBuffer)
            except:
                del key
                key = None
                self.nextPacket = None
                if not currentKey == None:
                    return (dataBuffer, metaBuffer)
            

    
    def reduce(self, data):
        return list(np.array(data).flatten())

    def process(self, inData, inMeta):
#         del inData
#         del inMeta

#         print(inData, inMeta)
#         if not None == inData:
#         print(inMeta, [{'emit':self.reduce(inData)}])
#         return [{'emit':list(np.array(inData).flatten())}]
        return [{'emit':self.reduce(inData)}]
#         return []
    
    
    