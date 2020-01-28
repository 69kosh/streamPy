'''
Набор общих юнитов
@author: Kosh
'''
# import cv2
import random
import tensorflow as tf

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Аугментируем и ресайзим картинку до нужного размера
    '''
    def process(self, inData, inMeta):
        config = self.config
        image = inData['image']
        
        size = (image.shape[0], image.shape[1])
        
        w = random.randint(int(size[1] * config['augment']), size[1])
        h = random.randint(int(size[0] * config['augment']), size[0])
        
        image = tf.image.random_crop(image, size=[h, w, 3])
        
        image = tf.image.resize_with_pad(image, config['height'], config['width'])
        
#        image = tf.image.per_image_standardization(image)

        
        if ('toFloat' in config) and config['toFloat']:
            image = tf.cast(image, dtype=tf.float16)
            
        if 'multiply' in config:
            image *= config['multiply']

        #         if (self.cnt % 10 == 0): 
#             print(self.cnt)
#         self.cnt += 1
#        print(image.shape[0], image.shape[1])
        return [{'image':image}]
#         return []
    
    cnt = 0