'''
Created on 29 окт. 2019 г.

@author: Kosh
'''
# from streampy.units.base.pooled import Pool
from queue import Queue
from streampy.units.base.loader import getClass

class Segment(object):
    '''
    Создаём сегмент обработки данных
    Создаём его из конфвы
    '''


    def __init__(self, config):
        self.config = config
        '''
        Constructor
        '''
    def start(self):
        
        config = self.config
        
        self.units = {}
        units = {}
        outs = {}
        ins = {}
    
        for name in config['units']:
            print(name)
            unitConfig = config['units'][name]
    
            if name not in ins:
                ins[name] = {}
                
            if name not in outs:
                outs[name] = {}   
            
            if 'in' in unitConfig: 
                for key in unitConfig['in']:
                    outUnit = unitConfig['in'][key]['from']
                                        
                    if outUnit in units:
                        if 'out' in unitConfig['in'][key]:
                            # если указан аут явно - используем его
                            outName = unitConfig['in'][key]['out']
                        else:
                            #иначе используем имя входа
                            outName = key
    
                        if 'size' in unitConfig['in'][key]:
                            queueSize = unitConfig['in'][key]['size']
                        else:
                            queueSize = 1
                        
    #                     print('create queue from {}.{} to {}.{} size {}'
    #                           .format(outUnit, outName, name, key, queueSize))
    
                        q = Queue(queueSize)
                                            
    #                   if outUnit not in queues:
    #                       queues[outUnit] = {}
                            
                        if outUnit not in outs:
                            outs[outUnit] = {}   
                        if outName not in outs[outUnit]:
                            outs[outUnit][outName] = []                        
    
    #                    queues[outUnit][name] = q
                        ins[name][key] = q
                        
      
                        outs[outUnit][outName].append(q) # 
                        
    #                    print('{} - {} -> {} - {}'.format(name, key, outUnit, outName))
                        
                    else:
                        print('unit not found: ' + outUnit)
     
            units[name] = unitConfig
            
            
            
        for name in config['units']:
            cls = getClass(units[name]['module'], 'Pool')
            thread = cls(units[name], ins[name], outs[name])
            thread.setDaemon(True)
            thread.start()
            
            self.units[name] = thread   
#             self.units[name] = Pool(units[name], ins[name], outs[name])

    def stop(self):
        pass
        