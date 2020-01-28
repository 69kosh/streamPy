'''
Набор общих юнитов
@author: Kosh
'''
import cv2

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Захватываем кадры с устройства или видео-файла
    '''    
    def init(self):
        self.source = cv2.VideoCapture(self.config.get('source', 0))
        
        self.source.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.config.get('width', 640)))
        self.source.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.config.get('height', 480)))
#         self.source.set(cv2.CAP_PROP_FPS, 15)

        self.counter = 0
        self.frame_counter = 0
    

    def process(self, inData, inMeta):
        try:
            ret, image = self.source.read()
#             cv2.imshow('capframe', image)
#             cv2.waitKey(1)
            self.frame_counter += 1
#             print(self.source.get(cv2.CAP_PROP_FRAME_COUNT))
            if self.frame_counter == self.source.get(cv2.CAP_PROP_FRAME_COUNT):
                self.source.release()
                self.init()
                
            if not ret:
                raise Exception
            
        except:
            print('Something wrong with source {}', self.config.get('source', 0))  
            return []

#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return [{'image':image}]

    def send(self, outData, outMeta):
        config = self.config
        # если надо внедрять идентификатор 
        # то для каждого куска данных делаем отправку отдельно
        for data in outData:
            outMeta.update({'id':self.counter})
            self.counter += 1
#                 print('putting')
#                 print(data)
#                 print(self.outs)
            super().send([data], outMeta)
