'''
Набор общих юнитов
@author: Kosh
'''
import numpy as np
from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Преобразуем ббоксы в заполненные ячейки для yolo-подобного детектирования
    пока в примитивном варианте с одним классом
    todo: добить до множества анкоров, возможно в нескольких разрешениях
    '''
    
    def process(self, inData, inMeta):
        
        config = self.config
        cellsConfig = config.get('cells', [7, 7])
        cellsSizeConfig = config.get('cellsSize', [32, 32])
        cells = np.zeros((cellsConfig[0], cellsConfig[1], 5))
#         print(cellsConfig)
        for bbox in inData['bboxes']:
            cx = bbox[2]/2 + bbox[0]
            cy = bbox[3]/2 + bbox[1]
            xCell = int(cx // cellsSizeConfig[0])
            yCell = int(cy // cellsSizeConfig[1])
            dx = (cx % cellsSizeConfig[0]) / cellsSizeConfig[0]
            dy = (cy % cellsSizeConfig[1]) / cellsSizeConfig[1]
            dw = bbox[2] / cellsSizeConfig[0]
            dh = bbox[3] / cellsSizeConfig[1]
            
            cells[yCell][xCell] = [1, dx, dy, dw, dh]
#             print(bbox)
#             print(xCell, yCell)
#             print(cells[yCell][xCell])
#         print(cells)
        return [{'cells':cells}]


        
        