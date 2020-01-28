'''
@author: Kosh
'''
import tensorflow as tf

from streampy.units.base.loader import getClass

from streampy.units.base.pooled import Pool, Worker as Base
from tensorflow.keras.optimizers import Adam
from tensorflow_core.python.keras.losses import MAE

class Worker(Base):
    '''
    Учим сетку
    В данной реализации мы не используем процедуру подготовки 
    для получения данных, а инициируем два генератора,
    достающих каждый из сввоей очереди трейновую и валидационную выборку
    И периодически работающего обучения, останавливающегося каждую эпоху.
    '''
    def trainGenerator(self):
        while True:

            package = self.ins['train'].get()
#             print(package['data']['image'], package['data']['predict'])
            yield package['data']['image'], package['data']['predict']

    def validGenerator(self):
        while True:

            package = self.ins['valid'].get()
            yield (package['data']['image'], package['data']['predict'])

        
    def init(self):
        config = self.config
        shape = config.get('inputShape', [224, 224, 3])
        outputShape = config.get('outputShape', 1)

        loss = config.get('loss', None)
        optimizer = config.get('optimizer', Adam(lr=0.001,))
        metrics = config.get('metrics', None)#['mae']
        
        modelConfig = config.get('model', {})
        moduleName = modelConfig.get('module', None)
        className = modelConfig.get('class', None)
        modelModelConfig = modelConfig.get('config', {})
        print(config)
        modelManagerClass = getClass(moduleName, className)
        self.modelManager = modelManagerClass(modelModelConfig)
        
        self.model = self.modelManager.load()
        if None == self.model:
            self.model = self.modelManager.create()

        if None == loss:
            loss = self.modelManager.createLoss()

        if None == metrics:
            metrics = self.modelManager.createMetrics()

        self.model.compile(
                  loss=loss, #'mean_absolute_error', #'binary_crossentropy', #'mean_squared_error',
                  optimizer=optimizer, #Adam(lr=0.001,),#RMSprop(lr=0.1),
                  metrics=metrics) #'accuracy', 'mse',
        
        
        batch = config.get('batch', 8)
        self.trainDataset = tf.data.Dataset.from_generator(
                generator = self.trainGenerator,
                output_types = (tf.float16, tf.float16),
                output_shapes = ((shape), (outputShape))
            )
        self.trainDataset = self.trainDataset.batch(batch)

        self.validDataset = tf.data.Dataset.from_generator(
                generator=self.validGenerator,
                output_types=(tf.float16, tf.float16),
                output_shapes = (shape, outputShape)
            )
        self.validDataset = self.validDataset.batch(batch)
 

    
    '''
    Ничего не готовим
    '''
    def prepare(self):
        return (None, {})
    
    def process(self, inData, inMeta):
        config = self.config
        epochs = config.get('epochs', 10)
        trainSteps = config.get('trainSteps', 100)
#         batch = config.get('batch', 8)
        validationSteps = config.get('validSteps', 10)
        
        result = self.model.fit(
                        x=self.trainDataset, 
                        steps_per_epoch = trainSteps,
                        validation_data=self.validDataset,
                        validation_steps = validationSteps,
                        epochs = epochs,
                        callbacks=[self.modelManager.getCheckpointCallback()]
                        )

        print(result)


