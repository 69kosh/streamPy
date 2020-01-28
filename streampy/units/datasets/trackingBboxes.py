'''
Набор общих юнитов
@author: Kosh
'''
import cv2
import numpy as np
from streampy.units.base.pooled import Pool, Worker as Base
import math
import tensorflow as tf

class Obj:
    def __init__(self):
        self.trackers = []
        self.bboxes = []
        
    def addTracker(self, tracker):
        self.trackers.append(tracker)
#        self.track[tracker] = index
        
    def removeTracker(self, tracker):
        if self.isTracked(tracker):
            self.trackers.remove(tracker)
#        self.track.remove(tracker)
        return not len(self.trackers)
    
    def isTracked(self, tracker):
        return tracker in self.trackers
    
    def resetBboxes(self):
        self.bboxes = []
        
    def appendBbox(self, bbox):
        self.bboxes.append(bbox)
    
    def getBbox(self):
        if len(self.bboxes):
            return np.mean(self.bboxes, axis = 0)
        else:
            return None
    
class Multitrackers:
    def __init__(self, skipSteps = 10, count = 3, newObjectThreshold = 0.1):
        self.fifo = []
        self.current = None
        self.skipped = skipSteps
        self.skipSteps = skipSteps
        self.multitrackersCount = count
        self.image = None
        self.objects = {}
        self.objectKey = 0
        self.trackObjects = {}
        
        self.newObjectThreshold = newObjectThreshold

    def getObjects(self):
        return self.objects
    
    def iouFunction(self, y_true, y_pred):
    
        if len(y_true) == 0 or len(y_pred) == 0:
            return []
    
        cx_true = y_true[:,0]
        cx_pred = y_pred[:,0]
           
        cy_true = y_true[:,1]
        cy_pred = y_pred[:,1]
           
        width_true = y_true[:,2]
        width_pred = y_pred[:,2]
           
        height_true = y_true[:,3]
        height_pred = y_pred[:,3]
        
        area_true = width_true * height_true
        area_pred = width_pred * height_pred
        
        xA = np.maximum(cx_true, cx_pred)
        yA = np.maximum(cy_true, cy_pred)
        xB = np.minimum(cx_true + width_true, cx_pred + width_pred)
        yB = np.minimum(cy_true + height_true, cy_pred + height_pred)
        
        interArea = np.maximum((xB - xA), 0) * np.maximum((yB - yA), 0)
        iou = interArea / (area_true + area_pred - interArea)
    
        return iou
    
    def update(self, image):
        self.image = image
        self.skipped -= 1
        if self.skipped == 0:
            # удаляем объекты, если не соталось связей
            if len(self.fifo) >= self.multitrackersCount:
                old = self.fifo.pop()
                for i in self.objects.copy():
                    obj = self.objects[i]
                    if obj.removeTracker(old):
                        # удаляем и сам объект из списка если это был последний трекер
                        del self.objects[i]
                
                if old in self.trackObjects:
                    del self.trackObjects[old]
                
            self.current = None
            self.skipped = self.skipSteps
            
            
        if self.current == None:
            self.current = cv2.MultiTracker_create()
            self.fifo.insert(0, self.current)


        for i in self.objects:
            self.objects[i].resetBboxes()
            
        for tracker in self.fifo:
            tracked, bboxes = tracker.update(self.image)
            # расписываем ббоксы на каждый объект
            for i, bbox in enumerate(bboxes):
                if i in self.trackObjects[tracker]:
                    self.trackObjects[tracker][i].appendBbox(bbox)
    
    def updateBboxes(self, bboxes):
        
        for detectedBbox in bboxes:
            m1 = []
            m2 = []
            keys = []
            objects = self.getObjects()
            for key in objects:
                obj = objects[key]
                bbox = obj.getBbox()
                if bbox is not None:
                    m1.append(detectedBbox[0:4])
                    m2.append(bbox)
                    keys.append(key)
            
#             print(objects)
#             print(np.array(m1), np.array(m2))
            res = self.iouFunction(np.array(m1), np.array(m2))
#             print(res)
            maxRes = 0
            obj = None
            if len(res) > 0:
                
                for i, val in enumerate(res):
                    if val > maxRes:
                        maxRes = val
                        obj = objects[keys[i]]
            
            if (maxRes < self.newObjectThreshold):
                '''
                Если малое наложение или его совсем нет - добавляем новый объект
                '''
#                 print('b1')
                self.addObject(detectedBbox[0:4])
#                 print('a1')
            else:
#                 print('b2')
                # если совпаденение меньше - обновляем этот объект
                self.updateObject(obj, detectedBbox[0:4])
#                 print('a2')
                    
    def addObject(self, bbox):
        obj = Obj()
        self.objects[self.objectKey] = obj
        self.objectKey += 1
        
        tracker = cv2.TrackerMedianFlow_create()
#         tracker = cv2.TrackerKCF_create()
        bbox = (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
        self.current.add(tracker, self.image, bbox)
        
        objects = self.current.getObjects()
        index = np.where(objects == bbox)[0][0]
        
        obj.addTracker(self.current)#, index)
        obj.appendBbox(bbox)
        if self.current not in self.trackObjects:
            self.trackObjects[self.current] = {}
        self.trackObjects[self.current][index] = obj

    def updateObject(self, obj, bbox):
        '''
        если посчитали что новые координаты важны для уже существующего объекта - добавляем его, 
        если он не отслеживался в текущем трекере
        '''
        if not obj.isTracked(self.current):
            
            tracker = cv2.TrackerMedianFlow_create()
#             tracker = cv2.TrackerKCF_create()
            bbox = (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
            self.current.add(tracker, self.image, bbox)
            
            objects = self.current.getObjects()
            index = np.where(objects == bbox)[0][0]
            
            obj.addTracker(self.current)#, index)
            obj.appendBbox(bbox)
            
            if self.current not in self.trackObjects:
                self.trackObjects[self.current] = {}
            self.trackObjects[self.current][index] = obj
            
    
class Tracker:
    def __init__(self, newObjectThreshold = 0.2):
        self.multitracker = cv2.MultiTracker_create()#'MEDIANFLOW')
        self.objects = []
        self.tracked = []
        self.bboxes = []
        self.newObjectThreshold = newObjectThreshold
        self.step = 0
        self.retrackTime = 10
        
        
    def iouFunction(self, y_true, y_pred):
    
        if len(y_true) == 0 or len(y_pred) == 0:
            return []
    
        cx_true = y_true[:,0]
        cx_pred = y_pred[:,0]
           
        cy_true = y_true[:,1]
        cy_pred = y_pred[:,1]
           
        width_true = y_true[:,2]
        width_pred = y_pred[:,2]
           
        height_true = y_true[:,3]
        height_pred = y_pred[:,3]
        
        area_true = width_true * height_true
        area_pred = width_pred * height_pred
        
        xA = np.maximum(cx_true, cx_pred)
        yA = np.maximum(cy_true, cy_pred)
        xB = np.minimum(cx_true + width_true, cx_pred + width_pred)
        yB = np.minimum(cy_true + height_true, cy_pred + height_pred)
        
        interArea = np.maximum((xB - xA), 0) * np.maximum((yB - yA), 0)
        iou = interArea / (area_true + area_pred - interArea)
    
        return iou
    
    def update(self, image, bboxes):
        '''
        Для каждого нового ищем треки, если не нашли - 
        добавляем, но с учетм ранее добавленного
        '''
        self.image = image
        self.tracked, self.bboxes = self.multitracker.update(image)
        self.bboxes = list(self.bboxes)
#         print(self.tracked)
        bboxes = sorted(bboxes, key=lambda x: -x[6])

        for detectedBbox in bboxes:
            m1 = []
            m2 = []
            for j, bbox in enumerate(self.bboxes):
                m1.append(detectedBbox)
                m2.append(bbox)
            res = self.iouFunction(np.array(m1), np.array(m2))
            if len(res) > 0:
                maxRes = max(res)
            else: 
                maxRes = 0
            
            if (maxRes < self.newObjectThreshold):
                '''
                Если малое наложение или его совсем нет - добавляем новый объект
                '''
                self.add(detectedBbox)

    def add(self, bbox):
        tracker = cv2.TrackerMedianFlow_create()
        bb = (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))
        self.multitracker.add(tracker, self.image, bb)
        self.bboxes.append(bbox[0:4])
        objcts = self.multitracker.getObjects()
        print('getobj')
        print(objcts)
        print(np.where(objcts == bb)[0][0])
        

    def getBboxes(self):
        return self.bboxes
    
class Worker(Base):
    '''
    Отслеживаем по первичным ббоксам объекты.
    Для того, чтобы не путать объекты - нужно вычислять их дескрипторы, 
    и сравнивать вновь появившиеся ббоксы с имеющимися привязанными,
    а вслучае если объект сильно мутировал, но трекается - добавлять 
    новые дескрипторы к описанию объекта
    
    Объект содержит:
        - текущий ббокс, который может быть как ббоксом 
            от прошлого кадра, так и ббоксом от трекера на основе других 
            алгоритмов, иницииализированных ранее для этого объекта.
        
        - набор дескрипторов, которые описывают изображение объекта, 
            детектировавшегося рянее
        
        - для плавного тректинга - набор трекеров на основнаии которых 
            вычисляется текущий ббокс, можно использовать 
            например среднее арифметическое от них. Их нужно периодически 
            сбрасывать и следить, чтобы они не расходились сильно
            
    На первом этапе делаю только привязку ббоксов к объектам по дкскриптору
    
    upd:
    На каждом цикле мы имеем набор достоверных ббоксов, найденных сейчас.
    Так же мы имеем некоторый набор объектов, отслеживаемых с прошлого раза,
    в них есть один или больше трекер, предсказывающих положение каждого объекта, 
    причем с определённой достоверностью. 
    Поэтому на каждом шагу вычисляем прогноз для каждого из существующих объектов, 
    ищем детекченные ббоксы, попадающие в каждый из прогнозов, если находим - 
    считаем точный ббокс, иначе используем ббокс прогноза. Для оставшихся ббоксов 
    в порядке уверенности создаём объект, и делаем вышеописанные шаги.
    
    
    Третья попытка:
    используем мультитрекер, добавляем ббоксы по мере появления новых объектов.
    новые объекты - это те, которые не смогли покрыть iou < 0.5 существующие треки.
    так же добавляем новый трек если вписались но плохо, iou > 0.5 и iou < 0.8
    Для каждого трека ведём достоверность, которая есть произведение iou на 
    достоверность найденного ббокса (используем экспоненциальным скользящим средним 
    для сглаживания). Для выбора ббокса объекта используем среднее взвешенных ббоксов.
    Заводим новый мультитрекер каждый n кадров, одновременно существует m трекеров.
    '''
    
    def init(self):
        Base.init(self)
        
#         self.tracker = Tracker(0.2)
        self.multitrackers = Multitrackers(
            skipSteps = 5, count = 3, newObjectThreshold=0.2)

    def process(self, inData, inMeta):
        
#         config = self.config

        image = inData['sample']['image']
        bboxes = np.array(inData['sample']['predict'], dtype=float)

#         if len(bboxes):
#             tensor = tf.dtypes.cast(bboxes, tf.float32)
#             result = tf.image.non_max_suppression(
#                 tensor[:,0:4],
#                 tensor[:,6],
#                 100,
#                 iou_threshold=0.2,
#                 score_threshold=float('-inf'),
#                 name=None
#             )
#             print(result)
#             print(len(bboxes), len(result))
#             bboxes = np.array(bboxes)[result, 0:7]
        
        bboxes = sorted(bboxes, key=lambda x: -x[6]) # вес вынести более лучше или сортировать снаружи например
#        self.tracker.update(image, bboxes)
         
#         iou = self.tracker.find(bboxes)
#          
#         for i in iou:
#             if iou[i] < 0.3:
#                 self.tracker.add(bboxes[i])
#                 print('added')
             
#        bboxes = self.tracker.getBboxes()
#        print(len(bboxes))


        self.multitrackers.update(image)
        self.multitrackers.updateBboxes(bboxes)
        
        objects = self.multitrackers.getObjects()
        bboxes = []
        for i in objects:
            obj = objects[i]
            bbox = obj.getBbox()
            if bbox is not None:
                bbox = np.append(bbox, i)
                bboxes.append(bbox)
        
#         descriptors = []
#         for bbox in bboxes:
#             descriptors.append(self.getDescriptor(image, bbox))
#         
# #         print(len(descriptors))
# #         
#         for desc1 in descriptors:
#             for desc2 in descriptors:
#                 sub = self.subDescriptors(desc1, desc2)
#                 if sub > 0:
#                     print(sub)
#                     
#                     
#         for bbox in bboxes:
#             descriptor = self.getDescriptor(image, bbox)
#             obj = self.findObject(descriptor, bbox)
#             if not obj:
#                 obj = self.createObject(descriptor, bbox)
#               
#             obj.addDescriptor(descriptor)
# 
#         print(self.objectKey)
#         resultBboxes = {}
#         for obj in self.objects:    
#             # добавляем по ключу, чтобы убрать дубли найденных объектов
#             if obj.isVisible():
#                 resultBboxes[obj.getKey()] = obj.getBbox()
#                 resultBboxes[obj.getKey()][6] = obj.getKey() 
#         bboxes = resultBboxes.values()
#         print(bboxes)
        return [{'sample':{'image': image, 'predict':bboxes}}]
