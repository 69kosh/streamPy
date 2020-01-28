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
        cellSizeConfig = config.get('cellSize', [32, 32])
#         print(inData)
        image = inData['sample']['image']
        size = (image.shape[0], image.shape[1])
        cells = inData['sample']['predict']

        # вычисляем ольшую грань, по ней будем масштабировать 
        # из малого исходного размера
        # TODO: работает тока для квадратов :(
        edge = max(size)
        cellEdge = cellsConfig[0]*cellSizeConfig[0]
        ratio = edge/cellEdge
        px = py = 0
        # надо вычислить паддинги которые на короткой грани смещают ббоксы
        if edge == size[0]:
            px = (edge - size[1]) // 2
        else:
            py = (edge - size[0]) // 2
            
        bboxes = []
        for y in range(0, cellsConfig[0]):
            for x in range(0, cellsConfig[1]):
                cell = cells[y][x]
                if (cell[0] >= config.get('threshold', 0.5)):
                    w = cell[3] * cellSizeConfig[1]# * ratio
                    h = cell[4] * cellSizeConfig[0]# * ratio
                    
                    cx = (x + cell[1]) * cellSizeConfig[1]# * ratio
                    cy = (y + cell[2]) * cellSizeConfig[0]# * ratio
                    
                    l = cx - (w/2)# - px
                    t = cy - (h/2)# - py

                    
                    bboxes.append( [l, t, w, h,  str(x), str(y), str(cell[0])] )

        return [{'sample':{'image': image, 'predict':bboxes}}]
