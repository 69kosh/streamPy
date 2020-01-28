'''
@author: Kosh
'''
import tensorflow as tf
import numpy as np

from streampy.units.base.loader import getClass
from typing import Iterable
from streampy.units.base.pooled import Pool, Worker as Base


class Worker(Base):
    '''
    Используем сетку
    '''
    def init(self):
        config = self.config
        modelConfig = config.get('model', {})
        moduleName = modelConfig.get('module', None)
        className = modelConfig.get('class', None)
        modelModelConfig = modelConfig.get('config', {})
        print(config)
        modelManagerClass = getClass(moduleName, className)
        self.modelManager = modelManagerClass(modelModelConfig)
        
        self.model = self.modelManager.load()
        if None == self.model:
            self.model = self.modelManager.create()

    def prepare(self):
        data = []
        meta = []
        batchSize = self.config.get('batchSize', 32)
        timeout = self.config.get('timeout', 0.02)

        while batchSize > len(data):
            try:           
                # предполагаем что у нас всегда одна очередь
                key = list(self.ins.keys())[0]
                package = self.ins[key].get(block=True, timeout=timeout)
            except Exception:
                if len(data) > 0:
#                     print('break')
                    break
                else:
#                     print('cont')
                    continue
                
            meta.append(package['meta'])
            data.append(package['data'])
            
        return (data, meta)

    def process(self, inData, inMeta):
        
#         config = self.config
#         print(inData)
        result = self.model.predict(x = np.array(inData), batch_size = len(inData))
#         print(len(inData))
#         print(result[0,:,:,0])
        
        ret = []
        for predict in result:
            ret.append({'predict':predict})

        return ret

    def send(self, outData, outMeta):
        if isinstance(outData, Iterable):
            for idx, row in enumerate(outData):
                for key in row:
                    if key in self.outs:
                        package = self.prepareSendPackage(row[key], outMeta[idx])
                        for queue in self.outs[key]:
                            queue.put(package)
                    else:
                        print('out not found - {}'.format(key))

