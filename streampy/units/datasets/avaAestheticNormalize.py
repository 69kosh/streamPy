'''
Набор общих юнитов
@author: Kosh
'''
import numpy as np

def normalize(x):
    return x / np.max(x, axis=0)

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):

    '''
    classdocs
    '''
    def init(self):
        self.sumData = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype='float')
        self.weights = np.array([-0.5, -0.25, -0.15, -0.07, -0.03, 0.03, 0.06, 0.15, 0.25, 0.5], dtype='float')
#          print('aestheticNormalize.init')
    
#     def prepare(self):
# #         print('aestheticNormalize.prepare')
#         return super().prepare()
        
    def process(self, inData, inMeta):
#         print('aestheticNormalize.process')
#         print(inData)
        y = np.array(list(map( int, inData['row'][2:12])), dtype='float');
        self.sumData += y
        
        y /= self.sumData
        
        y = normalize(y) #normalize(row[1])
#         print(row[1])
        y *= self.weights
#         print(row[1])
        y = np.array([(np.sum(y)+1)*0.5], dtype='float')
        
        return [{'predict':y}]
