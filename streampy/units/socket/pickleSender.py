'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
from typing import Iterable
import pickle
import time
import socket

class Worker(Base):
    '''
    Воркер для отправки данных по сокету с упаковкой pickle
    '''
    def process(self, inData, inMeta):
        return [inData]

    def init(self):
        self.connect = None
#         self.i = 0

    def send(self, outData, outMeta):
        
#         self.i += 1
        data = pickle.dumps((outData, outMeta))
                
        while True:
            
            connect = self.getConnect()
            
            try:
                connect.sendall(data)
                print('sent!')
                break

            except:
                print('reconnect!')
                self.reconnect()
                time.sleep(self.config.get('retryDelay', 1.0))
            
    def reconnect(self):
        self.connect = None
        
    def getConnect(self):
        # проверяем текущий, если не годен - создаём новый
        if (self.connect and (self.connect.fileno() > 0)):
#             print(('retcon:', self.connect.fileno(), self.connect))
            return self.connect;
        
        while True:
            try:
                connect = socket.create_connection((
                    self.config.get('host', 'localhost'), 
                    self.config.get('port', 9090)),
                    timeout = 5.0 #self.config.get('timeout', 1.0)
                )
                break
            except:
                print('reconnecting...')
                time.sleep(self.config.get('retryDelay', 1.0))

        self.connect = connect
#         print(('retcon2:', self.connect))
        return self.connect
    
