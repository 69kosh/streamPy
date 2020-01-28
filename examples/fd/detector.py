'''
@author: Kosh
'''
from streampy.units.tf.modelPath import modelPath

from tensorflow.python.keras.layers.convolutional import *
from tensorflow.python.keras.layers.normalization import *
from tensorflow.python.keras.layers.core import *
from tensorflow.python.keras.layers.merge import *
import tensorflow as tf
from tensorflow_core.python.keras.layers.convolutional import Conv2D
from tensorflow_core.python.keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow_core.python.keras.layers.normalization import BatchNormalization
from tensorflow_core.python.keras import regularizers
from tensorflow_core.python.keras.layers.core import Activation, Dropout
from tensorflow_core.python.keras.models import Model
from tensorflow_core.python.keras.layers.merge import Concatenate
from tensorflow_core.python.keras.metrics import MAE, MSE

def iouFunction(y_true, y_pred):
    
    cx_true = y_true[:,:,:,1]
    cx_pred = y_pred[:,:,:,1]
       
    cy_true = y_true[:,:,:,2]
    cy_pred = y_pred[:,:,:,2]
       
    width_true = y_true[:,:,:,3]
    width_pred = y_pred[:,:,:,3]
       
    height_true = y_true[:,:,:,4]
    height_pred = y_pred[:,:,:,4]
    
    area_true = width_true * height_true
    area_pred = width_pred * height_pred
    
    xA = tf.maximum(cx_true, cx_pred)
    yA = tf.maximum(cy_true, cy_pred)
    xB = tf.minimum(cx_true + width_true, cx_pred + width_pred)
    yB = tf.minimum(cy_true + height_true, cy_pred + height_pred)
    
    interArea = tf.maximum((xB - xA), 0) * tf.maximum((yB - yA), 0)
    iou = interArea / (area_true + area_pred - interArea)

    return iou

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

        baseNeurons = 128
        dropout = 0.25

        out28 = baseModel.get_layer('block_6_expand_BN').output

        out = Conv2D(baseNeurons, (1, 1), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out28)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons * 2, (3, 3), strides=(2, 2), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons, (1, 1), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons * 2, (3, 3), strides=(2, 2), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out72 = Activation('relu')(out)


        out14 = baseModel.get_layer('block_13_expand_BN').output

        out = Conv2D(baseNeurons, (1, 1), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out14)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Conv2D(baseNeurons * 2, (3, 3), strides=(2, 2), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out7 = Activation('relu')(out)

        
        out = baseModel.get_layer('block_16_project_BN').output
#         out = baseModel.get_layer('out_relu').output

        out = Concatenate(axis=3)([out, out7, out72])

        out = Conv2D(baseNeurons * 1, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        
        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons * 2, (3, 3), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)
        
        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons * 1, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Dropout(dropout)(out)

        out = Conv2D(baseNeurons * 2, (3, 3), padding='same', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
        out = BatchNormalization()(out)
        out = Activation('relu')(out)

        out = Conv2D(5, (1, 1), padding='valid', 
                      activity_regularizer=regularizers.l1_l2(l1, l2))(out)
     
        model = Model(inputs=baseModel.input, outputs=out)
    
        for layer in baseModel.layers:
            layer.trainable = False
#              
        model.summary()
#         baseModel.summary()
        return model
    
    def load(self):
        model = super().load()
        if None != model:
            modelShape = list(model.layers[0].input_shape[0])[1:4]
#         print(modelShape)
#         print(self.inputShape)
#         print(modelShape == self.inputShape)
        
        
            
            if modelShape != self.inputShape:
                model.save_weights('temp_weights.h5')
                model = self.create()
                model.load_weights('temp_weights.h5')
        
        
        
            for layer in model.layers:
                layer.trainable = True
        
        return model
    

    
    def createMetrics(self):            
        def iouNorm(y_true, y_pred):

            object_true = y_true[:,:,:,0]
            object_pred = y_pred[:,:,:,0]
            
            iou = iouFunction(y_true, y_pred)
            
            object_true_sum = tf.clip_by_value(tf.reduce_sum(
                    object_true
                    , [1, 2])
                , 1e-10, 100000)
            
            iou_sum = tf.reduce_sum(
                tf.multiply(object_true, iou )
                , [1, 2]) #*object_pred
                 
            return iou_sum / object_true_sum
 
        def predNorm(y_true, y_pred):

            object_true = y_true[:,:,:,0]
            object_pred = y_pred[:,:,:,0]
            
            iou = iouFunction(y_true, y_pred)
            
            object_true_sum = tf.clip_by_value(tf.reduce_sum(
                    object_true
                    , [1, 2])
                , 1e-10, 100000)
            
            iou_sum = tf.reduce_sum(
                tf.multiply(object_true, object_pred )
                , [1, 2]) #*object_pred
                 
            return iou_sum / object_true_sum
               
        return [iouNorm, predNorm]
    
    def createLoss(self):
        
        def loss(y_true, y_pred):

            object_true = y_true[:,:,:,0]
            object_pred = y_pred[:,:,:,0]
             
            cx_true = y_true[:,:,:,1]
            cx_pred = y_pred[:,:,:,1]
              
            cy_true = y_true[:,:,:,2]
            cy_pred = y_pred[:,:,:,2]
              
            width_true = y_true[:,:,:,3]
            width_pred = y_pred[:,:,:,3]
              
            height_true = y_true[:,:,:,4]
            height_pred =y_pred[:,:,:,4]

#             loss1 = tf.reduce_sum(
#                 tf.multiply(object_true, (
#                     tf.math.squared_difference(cx_pred, cx_true) + 
#                     tf.math.squared_difference(cy_pred, cy_true)
#                     ))
#                 , [1, 2]
#                 )

            loss1 = tf.reduce_sum(
                tf.multiply(object_true, (
                    tf.math.abs(cx_pred - cx_true) + 
                    tf.math.abs(cy_pred - cy_true)
                    ))
                , [1, 2]
                )
              
#             loss2 = tf.reduce_sum(
#                 tf.math.multiply(object_true, (
#                     tf.math.squared_difference(tf.sqrt(tf.clip_by_value(width_pred, 1e-5, 100)), 
#                                                tf.sqrt(tf.clip_by_value(width_true, 1e-5, 100))) + 
#                     tf.math.squared_difference(tf.sqrt(tf.clip_by_value(height_pred, 1e-5, 100)), 
#                                                tf.sqrt(tf.clip_by_value(height_true, 1e-5, 100)))
#                     ))
#                 , [1, 2]
#                 )

            loss2 = tf.reduce_sum(
                tf.math.multiply(object_true, (
                    tf.math.abs(width_pred - width_true) + 
                    tf.math.abs(height_pred - height_true)
                    ))
                , [1, 2]
                )
                
            iou = iouFunction(y_true, y_pred)
            loss3 = tf.reduce_sum(
                tf.multiply(object_true, (
                    tf.math.squared_difference(object_pred, iou)
                    ))
                , [1, 2]
                )

            loss4 = tf.reduce_sum(
                tf.multiply(object_true, (
                    tf.math.squared_difference(object_pred, object_true)
                    ))
                , [1, 2]
                )
                             
            loss5 = tf.reduce_sum(
                tf.multiply(((object_true*-1)+1), (
                    tf.math.squared_difference(object_pred, object_true)
                    ))
                , [1, 2]
                )
#             
#             loss6 = tf.reduce_sum(
#                     tf.math.squared_difference(object_pred, object_true)
#                 , [1, 2]
#                 )
             
            return loss1 + loss2 + loss3 + loss4 + 0.2*loss5# loss1 + loss2 + loss3 + loss4#
        
        
        return loss    
    