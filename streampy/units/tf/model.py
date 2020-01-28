'''
@author: Kosh
'''

class model:
    '''
    Базовый класс работы с моделью 
    Нужно уметь создать модель с нуля
    Проверить есть ли уже обученная модель и загрузить её
    Сохранить обученную модель
    
    Используется в юнитах фита и предикта
    '''


    def __init__(self, config):
        '''
        Constructor
        '''
        self.config = config

    def load(self):
        pass
    
    def save(self, model):
        pass
    
    def create(self):
        pass

    def createLoss(self):
        return 'mse'