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
        Вырезаем Н-картинок по ббоксам, сортировканным по уверенности, 
        преобразуем в квадраты и расширяем
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['sample']['image']
        bboxes = []
        for predict in inData['sample']['predict']:
            bboxes.append(copy.copy(predict))
        
        sortBy = config.get('sortBy', 6)
        bboxes = sorted(bboxes, key=lambda x: -float(x[sortBy]))
    
        yMax = image.shape[0]
        xMax = image.shape[1]

        images = []
        limit = config.get('limit', 1)
        squareBbox = config.get('squareBbox', True)
        expandBbox = config.get('expandBbox', 1.0)
        for bbox in bboxes:
            if limit == 0:
                break
            limit -= 1
            
            l = float(bbox[0])
            t = float(bbox[1])
            w = float(bbox[2])
            h = float(bbox[3])
            cx = l + w//2
            cy = t + h//2
            if squareBbox:
                w = h = max(w, h) * expandBbox
            
            l = int(cx - w//2)
            t = int(cy - h//2)
            
            r = int(l + w)
            b = int(t + h)
            
            if l < 0:
                r = min(xMax, r - l)
                l = 0
            if r > xMax:
                l = max(0, l - r + xMax)
                r = xMax
                
            if t < 0:
                b = min(yMax, b - t)
                t = 0
            if b > yMax:
                t = max(0, t - b + yMax)
                b = yMax
            
            images.append({'image':image[t:b,l:r]})
 
        return images
