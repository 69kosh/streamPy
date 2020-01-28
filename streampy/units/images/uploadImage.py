'''
Набор общих юнитов
@author: Kosh
'''
import cv2
import os.path

from streampy.units.base.pooled import Pool, Worker as Base
import urllib3

class Worker(Base):
    '''
    classdocs
    '''
    
    def init(self):
        self.http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=1.0, read=10.0))
        
        
    def process(self, inData, inMeta):
        
        
        if os.path.exists(inData['sample']['filename']):
            return [{'filename':inData['sample']['filename']}]
    
        
        for source in inData['sample']['sources']:
            r = self.http.request('GET', source)
            if r.status == 200:
                out = open(inData['sample']['filename'], 'wb')
                out.write(r.data)
                out.close()
                return [{'filename':inData['sample']['filename']}] 