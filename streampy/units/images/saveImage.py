'''
Набор общих юнитов
@author: Kosh
'''
import cv2
import os

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):

    def process(self, inData, inMeta):
        basePath = self.config.get('basePath', '')
        pathMetaField  = self.config.get('pathMetaField', 'id')
        filenameMetaField = self.config.get('filenameMetaField', 'partId')

        path = basePath + str(inMeta.get(pathMetaField, '')) + '\\'
        try:  
            os.makedirs(path)
        except:
            pass
        
        filename = (path + str(inMeta.get(filenameMetaField, 'file')) + '.jpg')
        
        try:        
            cv2.imwrite(filename, inData['image'])
        except Exception:
            print('Something wrong with file {}'.format(filename))  
            return []


        return [{'filename':filename}]
