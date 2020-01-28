'''
Набор общих юнитов
@author: Kosh
'''

import random
import numpy as np

from streampy.units.base.pooled import Pool, Worker as Base
from numpy import uint8
class Worker(Base):
    '''
    Добавляем шум с яркостью, немного уводим цвет
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['image']
        size = (image.shape[0], image.shape[1])
        
        noiseRange = random.randint(1, int(float(config.get('noise', 0.1)) * 255))
        
        temp = np.random.randint(low = -noiseRange, high = noiseRange, 
                                  size = (image.shape[0], image.shape[1], 3), 
                                  dtype = 'int16')
        temp += image
        
        bias = int(float(config.get('rgbBias', 0.1))*255)
        bias2 = int(float(config.get('brightnessBias', 0.1))*255)
        bias2 = random.randint(-bias2, bias2)
        
        rgbBias = [random.randint(-bias, bias) + bias2,
                   random.randint(-bias, bias) + bias2,
                   random.randint(-bias, bias) + bias2]
        
        temp += rgbBias
        
        image = temp
        
        lessThen0 = image < 0
        moreThen255 = image > 255
        image[lessThen0] = 0
        image[moreThen255] = 255

        return [{'image':image.astype(uint8)}]
    
