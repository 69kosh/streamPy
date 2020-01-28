'''
Набор общих юнитов
@author: Kosh
'''
from PIL import Image
import numpy as np

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    classdocs
    '''
    def process(self, inData, inMeta):
        try:
#             image = Image.open(inData['filename'])
            image = np.asarray(Image.open(inData['filename']))
#             print(image.shape[0], image.shape[1])
            if not hasattr(image, 'shape'):
                print('Something wrong with file {}'.format(inData['filename']))  
                return []
        except Exception:
            print('Something wrong with file {}'.format(inData['filename']))  
            return []

        return [{'image':image}]
#         if (self.cnt % 10 == 0): 
#             print(self.cnt)
#         self.cnt += 1
#        print(image.shape[0], image.shape[1])
#         return [{'image':image}]
#         return []
    
#     cnt = 0