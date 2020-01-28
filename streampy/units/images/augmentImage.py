'''
Набор общих юнитов
@author: Kosh
'''

import random

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Кропаньем случайный куска изображения, случайность задаётся параметром
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['image']
        size = (image.shape[0], image.shape[1])
                
        # аугментируем путём использования 90% кадра, случано его вырезая из полного
        
        ax = random.randint(int(size[1] * config.get('augment', 1)), size[1])
        ay = random.randint(int(size[0] * config.get('augment', 1)), size[0])
        
        al = random.randint(0, size[1] - ax)
        ar = ax + al

        at = random.randint(0, size[0] - ay)
        ab = ay + at
                
        image = image[at:ab, al:ar]

        return [{'image':image}]
    
