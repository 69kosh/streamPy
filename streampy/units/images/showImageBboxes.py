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
        image = inData['sample']['image']
        
        for bbox in inData['sample']['predict']:
#             bbox = inData['image']['predict'][i]
            x = int(bbox[0])
            y = int(bbox[1])
            w = int(bbox[2])
            h = int(bbox[3])
            
            cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(image, str(bbox[4:]) , (x + 5, y + h - 8), 0, 0.4, (0,255,0))
        
        zoom = self.config.get('zoom', 1.0)
        if zoom != 1.0:
            image = cv2.resize(image, 
                               (int(image.shape[1] * zoom), int(image.shape[0] * zoom)))
        
        cv2.imshow(self.config.get('window', 'frame'), image)
        cv2.waitKey(self.config.get('wait', 0))
        return []