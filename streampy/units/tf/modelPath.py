'''
@author: Kosh
'''

from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.models import Model, load_model
from streampy.units.tf.model import model
from datetime import datetime
import os
# from tensorflow.python.platform import tf_logging as logging

class modelPath(model):
    '''
    Базовый класс работы с моделью 
    реализуется механизм хранения в выделенной папке 
    в виде файлов с ротацией
    
    сохраняются веса и сама модель сети

    имя файла формируем и используем потом для сохранения
    Имя состоит из даты/времени старта обучения конкретной модели, 
    глобального счетчика эпох, локального счетчика эпохи, 
    лоса на валидации
    дату, глобальный счетчик используем повторно
    
    При попытке загрузки - ищем последнюю стартовавшую модель, 
    последнее её сохранение, тупо сортируя по имени файла.

    '''

    def __init__(self, config):
        now = datetime.now()
        self.time = now.strftime("%Y%m%d%H%M")
        self.epoch = 0
        
        return super().__init__(config)
        
    def load(self):
        filepath = self.config.get('path', '')
        filenames = os.listdir(filepath)
        filenames = filter(lambda name: '.h5' in name, filenames)
        filenames = sorted(filenames, reverse = True)
        if len(filenames) > 0:
            
            filename = filenames[0]
            lst = filename.split('-')
            self.time = lst[0]
            self.epoch = int(lst[1])
            model = load_model(filepath + filename, compile = False)
            model.summary()
            
            return model
        else:
            return None
    
    def save(self, model, epoch, loss):
        filepath = self.config.get('path', '')
        globalEpoch = self.epoch + epoch + 1

        filepath += '{time}-{globalEpoch:03d}-{epoch:03d}-{loss:.4f}.h5'.format(
            time = self.time,
            epoch = epoch + 1, 
            globalEpoch = globalEpoch, 
            loss=loss)
        print(filepath)
        model.save(filepath, overwrite=True, include_optimizer = False)
    
    
    '''
        Используем калбэк для сохранения актуальных версий
    '''
    def getCheckpointCallback(self):
        return MyModelCheckpoint(filepath=self, # вместо имени файла подставляем текущий сейвер
                                 verbose=1, 
                                 save_best_only=True, 
                                 save_weights_only=False)
    
class MyModelCheckpoint(ModelCheckpoint):
#     def __init__(self,
#                filepath,
#                monitor='val_loss',
#                verbose=0,
#                save_best_only=False,
#                save_weights_only=False,
#                mode='auto',
#                save_freq='epoch',
#                load_weights_on_restart=False,
#                **kwargs):
#         super(ModelCheckpoint, self).__init__(               filepath,
#                monitor,
#                verbose,
#                save_best_only,
#                save_weights_only,
#                mode,
#                save_freq,
#                load_weights_on_restart,
#                **kwargs)
        
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.epochs_since_last_save += 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
#             filepath = self.filepath.format(epoch=epoch + 1, **logs)
            saver = self.filepath
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    print('Can save best model only with %s available, '
                                  'skipping.', self.monitor)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s improved from %0.5f to %0.5f,'
                                ' saving model' % (epoch + 1, self.monitor, self.best,
                                                         current))
                        self.best = current
                        saver.save(model = self.model, epoch = epoch, loss=logs['val_loss'])
#                         self.model.save(filepath, overwrite=True, include_optimizer = False)
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' % 
                                  (epoch + 1, self.monitor, self.best))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving model' % (epoch + 1))
#                 self.model.save(filepath, overwrite=True, include_optimizer = False)  
                saver.save(model = self.model, epoch = epoch, loss=logs['val_loss'])
