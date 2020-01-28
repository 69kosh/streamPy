'''
@author: Kosh
'''
from streampy.units.tf.modelPath import modelPath

from tensorflow.python.keras.layers.convolutional import *
from tensorflow.python.keras.layers.normalization import *
from tensorflow.python.keras.layers.core import *
from tensorflow.python.keras.layers.merge import *
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import *
from tensorflow.python.keras.applications.mobilenet_v2 import MobileNetV2

class MNV2(modelPath):
    '''
    Класс работы с моделью MobileNetV2
    '''

    def __init__(self, config):

        self.inputShape = config.get('inputShape', [224, 224])
        self.outputShape = config.get('outputShape', 1)
        
        return super().__init__(config)
    
    def create(self):

        inputShape = self.inputShape
        outputShape = self.outputShape

        baseModel = MobileNetV2(include_top=False,# weights=None,
            alpha=1.0,
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
    
#         out = Conv2D(512, (1, 1), padding='valid', 
#                       activity_regularizer=regularizers.l1_l2(l1, l2))(out)
#         out = BatchNormalization()(out)
#         out = Activation('relu')(out)
#         out = Dropout(dropout)(out)
        
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
    
        for layer in baseModel.layers:
            layer.trainable = False
            
        model.summary()
        return model