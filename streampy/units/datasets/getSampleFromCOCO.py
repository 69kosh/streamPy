'''
@author: Kosh
'''
import json
from random import shuffle, randint

from pprint import pprint 

from streampy.units.base.pooled import Pool, Worker as Base
class Worker(Base):
    '''
    Считываем csv файл мешаем его, делаем выборку
    '''

    def init(self):
        self.fullData = []
        self.categories = {}
        samples = {}
        categories = {}
        config = self.config
        for filename in config['samplesFiles']:
            print('Loading file {}...'.format(filename))
            with open(filename, 'r') as file:
                data = json.load(file)
                # категории
                added = 0
                
                for category in data['categories']:
                    if not categories.get(category['id'], False):
                        added += 1
                        categories[category['id']] = category

                print ('loaded {} categories, added {} categories'.format(len(data['categories']), added))
                
                
                # добавляем картинки, которых не было в сэмплы
                added = 0
                
                for image in data['images']:
                    if not samples.get(image['id'], False):
                        added += 1
                        samples[image['id']] = {
                            'id': image['id'],
                            'filename': config['imagesPath'] + image['file_name'],
                            }
                        if config.get('withBboxes', False):
                            samples[image['id']]['bboxes'] = []
                            
                        if config.get('withSourcesUrls', False):
                            samples[image['id']]['sources'] = [image['coco_url'], 
                                                             image['flickr_url']]

                print ('loaded {} images, added {} images'.format(len(data['images']), added))

                bboxes = 0
                for ann in data.get('annotations'):
                        
                    if config.get('withBboxes', False):
                        
                        segments = ann.get('segments_info', False)
                        if not segments:
                            bbox = ann.get('bbox', False)
                            if bbox:
                                segments = [ann]

                        if segments:
                            for segment in segments:
                                bbox = segment.get('bbox', False)
                                bbox.append(segment['category_id'])
                                if config.get('withTextCategory', False):
                                    bbox.append(categories[segment['category_id']]['name'])
                                if not (config.get('withOnlyThings', False) 
                                    and not categories[segment['category_id']].get('isthing', True)):
# 0 0 = 1
# 0 1 = 1
# 1 0 = 0
# 1 1 = 1                                    
                                    samples[ann['image_id']]['bboxes'].append(bbox)
                                    bboxes += 1
                                
                            
                print ('loaded {} annotations'.format(len(data['annotations'])))
                print ('added {} bboxes'.format(bboxes))
               
#                 pprint(data['categories'])
#                 pprint(data['annotations'][0:10])
               
        for key in samples:
            self.fullData.append(samples[key])
            
#         pprint(self.fullData[0:10])
#                 print(data.keys())
#                 pprint(data['info'])
#                 pprint(data['licenses'])
#                 pprint(data['categories'])
#                 print(len(data['images']))
#                 print(len(data['annotations']))
#                 
#                 pprint(data['images'][0:2])
                    
#             for row in reader:
#                 self.fullData.append(row)
#         
#         if config['shuffle']:
#             shuffle(self.fullData)

    def process(self, inData, inMeta):
        data = []
        config = self.config
        count = len(self.fullData)
        offset = randint(count * config['from'], count * config['to'] - 1)
        data.append({'sample':self.fullData[offset]})
        return data
    
    def send(self, outData, outMeta):
        config = self.config
        # если надо внедрять идентификатор 
        # то для каждого куска данных делаем отправку отдельно
        for data in outData:
            outMeta.update({'id':data['sample']['id']})
            super().send([data], outMeta)

            