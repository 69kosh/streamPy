'''
Набор общих юнитов
@author: Kosh
'''
# import pickle;

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Синкаем данные из несколько труб, маркированных в мета одним значением 
    Вариант с буфером:
    Делаем буфер (словарь по значениюю), где раскладываем по каждому 
    значению наборы. Трубу из которой доставать данные определяем по счетчику 
    где меньше всего пытались брали ранее + сколько реально достали 
    (пытались - это чтобы было движение, если в одной пусто то берём в другой, 
    протолкнём рассинхронизирванные выше очереди)
    данные обратно не возвращаем пока, считаем что однопоточно работаем с трубами
    TODO: запилить возврат в трубы старых данных, чтоб другой поток их мог использовать
    TODO: бывает рассинхрон из-за того что картинка например не нашлась 
        и сообщение похерилось, а его пара в буфере висит... надо придумать что-нить
    '''
    def init(self):
        self.buffer = {}
        self.counts = {}
        self.tries = {}
        for key in self.ins:
            self.counts[key] = 0
            self.tries[key] = 0
    
    def next(self):
        arr = {}
        for key in self.ins:
            arr[key] = self.counts[key] + self.tries[key]
        return min(arr, key=arr.get)
    
    def prepare(self):

        mergeIdField = self.config.get('field', 'id')
        mergeId = None
        foundData = None
        while True:
            # пытаемся достать очередной элемент
            key = min(self.tries, key=self.tries.get)
            self.tries[key] += 1
            try:
                package = self.ins[key].get(block=True, timeout=0.001)
                self.counts[key] += 1
#                 print(self.tries)
                
                mergeId = package['meta'][mergeIdField]
                # получили, укладываем в буфер
                if mergeId not in self.buffer:
                    self.buffer[mergeId] = {}
                    
                self.buffer[mergeId][key] = package
                
#                 print(len(self.buffer[mergeId]))
                # все ли данные найдены
                if len(self.buffer[mergeId]) == len(self.ins):
                    # настало счастье, надо стопорнуть цикл и отдать их
                    # исключив из буфера
                    foundData =  self.buffer[mergeId]
                    del self.buffer[mergeId]
                    for key in self.counts:
                        self.counts[key] -= 1
                        self.tries[key] -= 1
                        
#                     print(len(self.buffer))
                    break
                
                
            except Exception:
                pass

#         print(foundData)
        # обрабатываем кортэж
        data = {}
        meta = {}
        for key in foundData:
            package = foundData[key]
            data[key] = package['data']
            meta.update(package['meta'])
            
#         print('data:')
#         print(data, meta)
#         print(pickle.dumps((data, meta)))
        return (data, meta)


    def process(self, inData, inMeta):
        if (self.cnt % 100 == 0): 
            print(self.cnt)
        self.cnt += 1
#         print(inData)
        return [{'out':inData}]
    
    cnt = 0
    