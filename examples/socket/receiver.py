import sys
sys.path.append('../..')

import yaml

from time import sleep
from streampy.segment import Segment

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        configName = sys.argv[1]
    else:
        configName = "receiver.yaml"
    
    with open(configName, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            exit()

    print(config['name'])

    segment = Segment(config)
    segment.start() 

    i = 120*5
    while (i > 0):
        i-=1
        sleep(1)
        pass    

    segment.stop() 