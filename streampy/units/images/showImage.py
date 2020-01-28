'''
Набор общих юнитов
@author: Kosh
'''

import cv2

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Выводим картинку в окно
    '''
    def process(self, inData, inMeta):
#         print(123)
        image = inData['image']
        zoom = self.config.get('zoom', 1.0)
        if zoom != 1.0:
            image = cv2.resize(image, 
                               (int(image.shape[1] * zoom), int(image.shape[0] * zoom)))

        cv2.imshow('frame', image)
        cv2.waitKey(self.config.get('wait', 0))
        return []