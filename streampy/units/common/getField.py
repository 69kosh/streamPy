'''
Набор общих юнитов
@author: Kosh
'''
from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Извлекаем заданное поле и добавляем к нему постфикс и префикс
    '''
    
    def process(self, inData, inMeta):
        
        config = self.config
        
        value = inData['row'][config.get('field', 0)]

        if isinstance(value, str):
            value = config.get('prefix', '') + value + config.get('postfix', '')

#         print(value)
        return [{'field':value}]


        