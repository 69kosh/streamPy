'''
Сервер запускающий потоки для обслуживания сокета, и базовый воркер

'''

from streampy.units.base.loader import getClass
from threading import Thread
import queue
from typing import Iterable

import socket

class Worker (Thread):

    def __init__(self, connect, outs, config):
        '''
        Constructor
        '''
        Thread.__init__(self)
        
        self.connect = connect
        self.outs = outs
        self.config = config.get('config', {})
    
        self.init()
    
    def init(self):
        pass
    
    def run(self):
        # инициируем
        # запускаем цикл
        # В цикле
        while True:
            # формируем входной пакет: свои правила 
            # или один к одному или собираем из нескоьких очередей, или пакетом
#             print('before prepare {}'.format(self.__class__.__name__))
            result = self.prepare()
            
            if not result: 
                break
            # раскидываем данные по выходам
#             print('before send {}'.format(self.__class__.__name__))
            self.send(result[0], result[1])
            # проверяем - а не пора ли спать
            
    def prepare(self):
        print('Abstract method in {} not implemented'.format(self.__class__.__name__))
        return [] 
    
    def send(self, outData, outMeta):
        if isinstance(outData, Iterable):
            for row in outData:
                for key in row:
                    if key in self.outs:
                        package = {'data':row[key], 'meta':outMeta}
                        for queue in self.outs[key]:
                            queue.put(package)
    #                         self.outs[key][queue].put(package)
    #                     print('putted')
    #                     print(package)
                    else:
                        print('out not found - {}'.format(key))

class Pool(Thread):
 

    def __init__(self, config, inQueues, outQueues):
        '''
        Constructor
        '''
        Thread.__init__(self)
        
        self.config = config;
        self.inQueues = inQueues;
        self.outQueues = outQueues;
        self.threadsCount = config.get('threads', 1)  
        # инициируем массив потоков
        # мы будем заполнять от 0 до threadsCount их, 
        # выкидывая нерабочие, но если закончатся те что есть 
        # то новых соединений принимать не будем.
        self.threads = {};
        
        socketPort = config.get('port', 9090)
        socketListen = config.get('listen', 1)
        
        
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.socket.bind(('', socketPort))
        self.socket.listen(socketListen)
        

    def run(self):
        cls = getClass(self.config['module'], 'Worker')
        
        while True:
            # ждем очередной коннект
            connect, addr = self.socket.accept()
            # ищем место для него
            index = None
            # пробегаем по всем трендам 
            for i in range(0, self.threadsCount):
                if self.threads.get(i, None) == None:
                    index = i
                    break
                
                self.threads[i].join(timeout=0.0)
                if not self.threads[i].is_alive():
                    index = i
                    break

            if index == None:
                # не нашли свободного места
                connect.close()
            else:    
                # создаем для него поток и обрабатываем там
                thread = cls(connect, self.outQueues, self.config)
                thread.setDaemon(True)
                thread.start()
                # добавляем в реестр тредов
                self.threads[index] = thread
                print(thread)
        
                
            
            
            