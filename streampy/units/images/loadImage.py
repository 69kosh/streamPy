'''
Набор общих юнитов
@author: Kosh
'''
import cv2

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    classdocs
    '''
    def process(self, inData, inMeta):
        try:
#             print(inData['filename'])
            image = cv2.imread(inData['filename'])
#             print(image.shape[0], image.shape[1])
            if not hasattr(image, 'shape'):
                print('Something wrong with file {}'.format(inData['filename']))  
                return []
        except Exception:
            print('Something wrong with file {}'.format(inData['filename']))  
            return []

#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
#         if (self.cnt % 100 == 0): 
#             print(self.cnt)
#         self.cnt += 1
        return [{'image':image}]
     
#     cnt = 0