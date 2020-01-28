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
                
        # аугментируем путём использования 90% кадра, случано его вырезая из полного
        
        resize = random.uniform(config.get('augment', 1), 1)
        
        if config.get('toSquare', False):
            if (size[1] > size[0]):
                ax = int(size[1] * resize)
                ay = min(int(size[1] * resize), size[0])
            else:
                ax = min(int(size[0] * resize), size[1])
                ay = int(size[0] * resize)
        else:
            ax = int(size[1] * resize)
            ay = int(size[0] * resize)
            
        al = random.randint(0, size[1] - ax)
        ar = ax + al

        at = random.randint(0, size[0] - ay)
        ab = ay + at
                
        image = image[at:ab, al:ar]
        
#         print(('al', al, 'at', at))
        bboxes2 = []
        for predict in bboxes:
            predict[0] = float(predict[0]) - al
            predict[1] = float(predict[1]) - at
            predict[2] = float(predict[2])
            predict[3] = float(predict[3])
            
            cx = predict[0] + predict[2]//2
            cy = predict[1] + predict[3]//2
            
            if (cx > 0 and cy > 0 and cx < ax and cy < ay):
                if predict[0] < 0:
                    predict[2] += predict[0]
                    predict[0] = 0
                if predict[0] + predict[2] > ax:
                    predict[2] = ax - predict[0] 
                if predict[1] < 0:
                    predict[3] += predict[1]
                    predict[3] = 0
                if predict[1] + predict[3] > ay:
                    predict[3] = ay - predict[1] 
                    
                bboxes2.append(predict)
        
 
        return [{'sample':{'image':image, 'predict': bboxes2}}]
    
    cnt = 0
