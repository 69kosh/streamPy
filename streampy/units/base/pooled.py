'''
Часть юнита отвечающая за организацю его в виде пула воркеров,
и его воркер
'''
#from threading import Thread
# import importlib

# def getClass(moduleName, className):
#     module = importlib.import_module(moduleName)
#     return getattr(module, className)

from streampy.units.base.loader import getClass
from threading import Thread
import queue
from typing import Iterable

class Worker (Thread):

    def __init__(self, ins, outs, config):
        '''
        Constructor
        '''
        Thread.__init__(self)
        
        self.ins = ins
        self.outs = outs
        self.config = config.get('config', {})
    
        self.init()
    
    def init(self):
        pass
    
    def run(self):
#         print(self.__class__)
#         print(self)
        # инициируем
        # запускаем цикл
        # В цикле
        while True:
            # формируем входной пакет: свои правила 
            # или один к одному или собираем из нескоьких очередей, или пакетом
#             print('before prepare {}'.format(self.__class__.__name__))
            (data, meta) = self.prepare()
#             print('before process {}'.format(self.__class__.__name__))
            # вызываем основную функцию
            result = self.process(data, meta)
            # раскидываем данные по выходам
#             print('before send {}'.format(self.__class__.__name__))
            self.send(result, meta)
            # проверяем - а не пора ли спать
            
            
    def prepare(self):
        data = {}
        meta = {}
#         print('ins:')
#         print(self.ins)
        # срезаем из каждой очереди по одной записи
        # сливаем мету вместе, а данные прокидываем дальше
        for key in self.ins:
            package = self.ins[key].get()
            data[key] = package['data']
            if None != package['meta']:
                meta.update(package['meta'])
            
#         print('data:')
#         print(data)
        return (data, meta)
    
    def process(self, inData, inMeta):
        print('Abstract method in {} not implemented'.format(self.__class__.__name__))
        return []
    
    def prepareSendPackage (self, outData, outMeta):
        return {'data':outData, 'meta':outMeta} 
         
    def send(self, outData, outMeta):
        if isinstance(outData, Iterable):
            for row in outData:
                for key in row:
                    if key in self.outs:
                        package = self.prepareSendPackage(row[key], outMeta)
                        for queue in self.outs[key]:
                            queue.put(package)
    #                         self.outs[key][queue].put(package)
    #                     print('putted')
    #                     print(package)
                    else:
                        print('out not found - {}'.format(key))
                        pass

class Pool(Thread):

#     threadsCount = 1
#     threads = []
    
#     config = {}
#     
#     inQueues = {}
#     outQueues = {}
     

    def __init__(self, config, inQueues, outQueues):
        '''
        Constructor
        '''
        
        Thread.__init__(self)
        
        if 'threads' in config:
            self.threadsCount = config['threads']
        else:
            self.threadsCount = 1
            
        self.config = config;
        self.inQueues = inQueues;
        self.outQueues = outQueues;
        self.threads = [];
        
#         self.update()
        
#     def start(self):
#         for thread in self.threads:
#             thread.start()
#         
    def run(self):
        
        count = self.threadsCount - len(self.threads) 
        
        if count == 0:
            return
        
        if count < 0:
            # надо убить несколько элементов 
            pass
        else:
            # надо добавить
            for i in range(0, count):
                cls = getClass(self.config['module'], 'Worker')#self.config['class'])
                thread = cls(self.inQueues, self.outQueues, self.config)
                thread.setDaemon(True)
                thread.start()
                self.threads.append(thread)
                print(thread)
                
            
            
            