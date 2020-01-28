'''
Набор общих юнитов
@author: Kosh
'''
from tensorflow.python.keras.layers.convolutional import *
from tensorflow.python.keras.layers.normalization import *
from tensorflow.python.keras.layers.core import *
from tensorflow.python.keras.layers.merge import *
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import *

import os
from tensorflow.python.keras.applications.vgg16 import VGG16
from tensorflow.python.keras.applications.mobilenet_v2 import MobileNetV2

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Учим сетку
    '''
    
    def init(self):
        config = self.config['config']
        shape = config['shape']
        loss = config['loss']
        optimizer = config['optimizer']
        metrics = config['metrics']
        self.model = self.createModelMNV24(shape, 1)
        self.model.compile(
                  loss=loss, #'mean_absolute_error', #'binary_crossentropy', #'mean_squared_error',
                  optimizer=optimizer, #Adam(lr=0.001,),#RMSprop(lr=0.1),
                  metrics=metrics) #'accuracy', 'mse',

        
    '''
    Компануем данные из очереди в минибатч
    '''
    def prepare(self):
        config = self.config['config']
        batch = config['batch']
        dataInput = []
        dataPredict = []
        meta = {}
        key = 'train'
        while batch > 0:
            package = self.ins[key].get()
            dataInput.append(package['data']['image'])
            dataPredict.append(package['data']['predict'])
            meta.update(package['meta'])
            batch -= 1
        
        return ({'input':np.array(dataInput), 'predict':np.array(dataPredict)}, meta)
    
    def process(self, inData, inMeta):
        config = self.config['config']
        inp = inData['input']
        predict = inData['predict']
        result = self.model.train_on_batch(x=inp, y=predict)
        print(result)


    def createModelVGG16(self, inputShape = (320, 320), outputShape = 1):

        baseModel = VGG16(include_top=False, #weights ='imagenet',#weights=None,
            input_shape = (inputShape[0], inputShape[1], 3))    
#         baseModel.summary()
        l1 = 0#.001
        l2 = 0#.001#.0001
        
        dropout = 0.25

        
        out = baseModel.get_layer('block5_pool').output
        
        out = Conv2D(128, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)

        out = Flatten()(out)
    #    out = GlobalMaxPool2D()(out)
        
    #     out = baseModel.output
        
        out = Dense(256, activity_regularizer=regularizers.l1_l2(l1, l2) )(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)
        
        out = Dense(256, activity_regularizer=regularizers.l1_l2(l1, l2) )(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)
        
        out = Dense(outputShape)(out)
        out = Activation('sigmoid')(out)
     
        model = Model(inputs=baseModel.input, outputs=out)
    
    #     for layer in baseModel.layers:
    #         layer.trainable = False
            
        model.summary()
        return model
    
    def createModelMNV24(self, inputShape = (320, 320), outputShape = 1):

        baseModel = MobileNetV2(include_top=False, weights=None,
            alpha=1,
            input_shape = (inputShape[0], inputShape[1], 3))    
    
        l1 = 0#.001
        l2 = 0#.001#.0001
        
        dropout = 0.25
        
        
        out1 = baseModel.get_layer('block_3_expand_relu').output
        
        out1 = Conv2D(128, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out1)
        out1 = BatchNormalization()(out1)
        out1 = Activation('relu')(out1)
        
        out1 = MaxPooling2D((8, 8))(out1)
        out1 = Dropout(dropout)(out1)
    
        out2 = baseModel.get_layer('block_6_expand_relu').output
    
        out2 = Conv2D(128, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out2)
        out2 = BatchNormalization()(out2)
        out2 = Activation('relu')(out2)
       
        out2 = MaxPooling2D((4, 4))(out2)
        out2 = Dropout(dropout)(out2)
    
        out3 = baseModel.get_layer('block_13_expand_relu').output
    
        out3 = Conv2D(256, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out3)
        out3 = BatchNormalization()(out3)
        out3 = Activation('relu')(out3)
        
        out3 = MaxPooling2D((2, 2))(out3)
        out3 = Dropout(dropout)(out3)
        
        
        out4 = baseModel.get_layer('out_relu').output
    
        out4 = Conv2D(512, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out4)
        out4 = BatchNormalization()(out4)
        out4 = Activation('relu')(out4)
        
        out4 = Dropout(dropout)(out4)
    
        out = Concatenate(axis=3)([out1, out2, out3, out4])
    
    #     out = Conv2D(512, (1, 1), padding='valid', 
    #                   activity_regularizer=regularizers.l1_l2(l1, l2))(out)
    #     out = BatchNormalization()(out)
    #     out = Activation('relu')(out)
    #     out = Dropout(dropout)(out)
        
        out = Conv2D(256, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)
        
        out = MaxPooling2D((2, 2))(out)
        out = Flatten()(out)
    #    out = GlobalMaxPool2D()(out)
        
    #     out = baseModel.output
        
        out = Dense(256, activity_regularizer=regularizers.l1_l2(l1, l2) )(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)
        
        out = Dense(256, activity_regularizer=regularizers.l1_l2(l1, l2) )(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        out = Dropout(dropout)(out)
        
        out = Dense(outputShape)(out)
        out = Activation('sigmoid')(out)
     
        model = Model(inputs=baseModel.input, outputs=out)
    
    #     for layer in baseModel.layers:
    #         layer.trainable = False
            
        model.summary()
        return model