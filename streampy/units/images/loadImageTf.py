'''
Набор общих юнитов
@author: Kosh
'''
import tensorflow as tf
import cv2
# from PIL import Image
# import numpy as np

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    classdocs
    '''
    def process(self, inData, inMeta):
        try:
            image_data = tf.io.read_file(inData['filename'])
#             print(inData['filename'])
            image = tf.image.decode_jpeg(image_data, channels=3)
#             image = cv2.imread(inData['filename'])
#             print(image.shape[0], image.shape[1])
            if not hasattr(image, 'shape'):
                print('Something wrong with file shape {}'.format(inData['filename']))  
                return []
        except Exception:
            print('Something wrong with file {}'.format(inData['filename']))  
            return []

#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return [{'image':image}]
#         if (self.cnt % 10 == 0): 
#             print(self.cnt)
#         self.cnt += 1
#        print(image.shape[0], image.shape[1])
#         return [{'image':image}]
#         return []
    
#     cnt = 0