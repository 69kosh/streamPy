'''
Набор общих юнитов
@author: Kosh
'''

import cv2
import random
import numpy as np

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Аугментируем и ресайзим картинку до нужного размера
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['image']
        size = (image.shape[0], image.shape[1])     
        
        # ресайзим 
        ration = min([float(config['height'] / size[0]), float(config['width'] / size[1])])
        x = int(size[1] * ration);
        y = int(size[0] * ration);

        image = cv2.resize(image, (x, y), interpolation = cv2.INTER_AREA )        
        
        # фитим
        w = config['width'] - x
        h = config['height'] - y
        
        top = h // 2
        bottom = h - top
         
        left = w // 2
        right = w - left

        image = cv2.copyMakeBorder(image, top, bottom, left, right, 
                                   cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
#         if ('toFloat' in config) and config['toFloat']:
#             image = np.float16(image)
#             
#         if 'multiply' in config:
#             image *= config['multiply']

        #         if (self.cnt % 10 == 0): 
#             print(self.cnt)
#         self.cnt += 1
#        print(image.shape[0], image.shape[1])
        return [{'image':image}]
#         return []
    
    cnt = 0