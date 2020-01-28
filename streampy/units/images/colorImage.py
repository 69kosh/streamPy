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
    Перекрашиваем картинку
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['image']
 
        if config.get('toRGB', False):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if ('toFloat' in config) and config['toFloat']:
            image = np.float16(image)
            
        if 'multiply' in config:
            image *= config['multiply']
            
        if ('toByte' in config) and config['toByte']:
            image = np.uint8(image)

        return [{'image':image}]
