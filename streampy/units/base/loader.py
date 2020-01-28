'''
Загрузчик юнитов

'''
import importlib

def getClass(moduleName, className):
    module = importlib.import_module(moduleName)
    return getattr(module, className)

