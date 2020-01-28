'''
Набор общих юнитов
@author: Kosh
'''

import cv2
import random
import numpy as np

from streampy.units.base.pooled import Pool, Worker as Base
import copy
class Worker(Base):
    '''
    Аугментируем и ресайзим картинку до нужного размера
    Так же преобразуем боксы, отбрасываем не поместившиеся и слишком маленькие
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['sample']['image']
        bboxes = []
        for predict in inData['sample']['predict']:
            bboxes.append(copy.copy(predict))
             

        size = (image.shape[0], image.shape[1])        
        
        # ресайзим
        ratio = min([float(config['height'] / size[0]), float(config['width'] / size[1])])
        x = int(size[1] * ratio);
        y = int(size[0] * ratio);

        image = cv2.resize(image, (x, y), interpolation = cv2.INTER_AREA )        
        bboxes2 = []
        for predict in bboxes:
            predict[0] = float(predict[0]) * ratio
            predict[1] = float(predict[1]) * ratio
            predict[2] = float(predict[2]) * ratio
            predict[3] = float(predict[3]) * ratio
            
            if ((predict[2] / 2 + predict[0] > 0) 
                and (predict[2] /2 + predict[0] < x) 
                and (predict[3] / 2 + predict[1] > 0)  
                and (predict[3] / 2 + predict[1] < y)
                and (predict[2] > config.get('minWidth', 10))
                and (predict[3] > config.get('minHeigth', 10))
                ):
                bboxes2.append(predict)        
        
#         print(('ratio', ratio, 'bboxes', bboxes))
        # фитим
        w = config['width'] - x
        h = config['height'] - y
        
        top = h // 2
        bottom = h - top
         
        left = w // 2
        right = w - left

        image = cv2.copyMakeBorder(image, top, bottom, left, right, 
                                   cv2.BORDER_CONSTANT, value=[0, 0, 0])
        
        bboxes = []
        for predict in bboxes2:
            predict[0] = float(predict[0]) + left
            predict[1] = float(predict[1]) + top
            
            bboxes.append(predict) 
        
#         
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         
#         if ('toFloat' in config) and config['toFloat']:
#             image = np.float16(image)
#             
#         if 'multiply' in config:
#             image *= config['multiply']

        return [{'sample':{'image':image, 'predict': bboxes}}]
    
    cnt = 0
