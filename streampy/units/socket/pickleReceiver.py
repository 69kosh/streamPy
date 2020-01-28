'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.socketServer import Pool, Worker as Base
import pickle
from io import BytesIO

class Worker(Base):
    
    def init(self):
        self.buffer = BytesIO()
            
    def prepare(self):
        '''
        Реализация работы с сокетом для получения pickle-пакетов
        '''
        result = None
        # цель - получить полный пакет, который может 
        # быть передан в несколько пакетов передачи данных
        while True:
            try:
                # пытаемся достать пакет
                picklePos = self.buffer.tell()
                result = pickle.load(self.buffer)
#                 print(('data!', len(result)))
                
                
                self.buffer = BytesIO(self.buffer.read())
                
                # если получилось, то пытаемся обнулить буфер, 
                # в случае если это последний пакет в буфере
#                 pos = self.buffer.tell()
#                 size = self.buffer.seek(0, 2)
#                 if pos == size:
#                     self.buffer.close()
#                     self.buffer = BytesIO()
#                 else:
#                     print((pos, size))
#                     self.buffer.seek(pos, 0)
                    
                break
            except:
                # восстанавливаем позицию
                self.buffer.seek(picklePos, 0)
                
                # если не удалось достать пакет, то пробуем 
                # добавить информации в буфер из сокета
                try:
                    received = self.connect.recv(self.config.get('bufferSize', 128*1024))
                except:
                    break
                
#                 print(('received!', len(received)))
                if not received: 
                    break
                # если получили данные - добавляем их в буфер, восстанавливая позицию
                pos = self.buffer.tell()
#                 print(('pos!', pos))
                self.buffer.seek(0, 2)
                pos2 = self.buffer.tell()
#                 print(('pos2!', pos2))
                self.buffer.write(received)
                self.buffer.seek(pos, 0)
                pos = self.buffer.tell()
#                 print(('pos2!', pos))
        
        return result
    