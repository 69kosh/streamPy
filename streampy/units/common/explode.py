'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
from typing import Iterable
import copy
class Worker(Base):
    '''
    Собираем несколько частей в одну, для этого устраиваем "буфер"
    определённо длины, если не собрали до исчерпания буфера - селяви
    '''

    def process(self, inData, inMeta):
        
        config = self.config
        field = config.get('field', None)
        if field == None:
            value = inData['row']
        elif(field in inData['row']):
            value = inData['row'][field]
        else:
            value = []
            
        data = []

        for i, d in enumerate(value):
            data.append({'row':{'part':value[i], 'partCount':len(value), 'partKey':i}})


        return data


    def prepareSendPackage (self, outData, outMeta):
        data = outData['part']
        meta = copy.deepcopy(outMeta)
        meta['partCount'] = outData['partCount']
        meta['partKey'] = outData['partKey']
        meta['partId'] = str(outMeta['id']) + '_' + str(outData['partKey'])
#         print({'data':data, 'meta':meta} )
        return {'data':data, 'meta':meta} 
        