'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
import numpy as np
import copy
class Worker(Base):
    '''
    Преобразуем пришедшие даные в набор связанных по мете но отдельных запросов
    В последствии, после обработки, их можно будет обратно сжать сделав reduce
    Так же генерим идентифкатор для мёржа для части
    '''
    def init(self):
        self.mainBuffer = []
        self.bufferSize = 0
        self.entityBuffer = {}
    
    def prepare(self):
        data = {}
        meta = {}

        '''
        Принимаем, пока не заполнили очердным все части, 
        или не добрались до лимита буфера
        '''
        size = self.config.get('bufferSize', 1000)
        returnedId = None
        while size > self.bufferSize:
            key = list(self.ins.keys())[0] # предполагаем что у нас всегда одна очередь
            
            package = self.ins[key].get()
            entityId = package['meta']['id']
#             print(package['meta'])
            if entityId not in self.entityBuffer:
                self.entityBuffer[entityId] = {'data':{}, 
                                               'meta':copy.deepcopy(package['meta'])}
                self.entityBuffer[entityId]['meta']['partKeys'] = []
                self.mainBuffer.append(entityId)
#                 print('entity added to buffer', entityId)
            partKey = package['meta']['partKey']
#             print('entity:', entityId, 'partKey:', partKey, 'all count',package['meta']['partCount'])
            entity = self.entityBuffer[entityId]
            entity['data'][partKey] = package['data']
            entity['meta']['partKeys'].append(package['meta']['partKey'])
            entity['meta']['partCount'] = package['meta']['partCount']
            
            self.bufferSize += 1
            if len(entity['meta']['partKeys']) >= int(package['meta']['partCount']):
                returnedId = entityId
                break

        
        if (returnedId == None) and (size <= self.bufferSize):
            returnedId = self.mainBuffer.pop(0)
            print('Buffer pop: ', returnedId)
            
        if returnedId != None and returnedId in self.entityBuffer:
            data = self.entityBuffer[returnedId]['data']
            meta = self.entityBuffer[returnedId]['meta']
            self.bufferSize -= len(self.entityBuffer[returnedId]['meta']['partKeys'])    
            del self.entityBuffer[returnedId]
    
#         print ((data, meta))
        return (data, meta)

#     def process2(self, inData, inMeta):
#         image = ''
#         for k in inData:
#             if not len(image):
#                 image = np.array(inData[k])
#             else:
#                 image = np.append(image, inData[k], axis=1)
# #                 image[0:96,0:96,0:3] = np.array(inData[k])
# #         print(image)
#         return [{'row':np.array(image)}]

    def process(self, inData, inMeta):
#         print(inData)
        return [{'row':inData}]