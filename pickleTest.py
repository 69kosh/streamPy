import pickle
from io import BytesIO

obj1 = {'cls': 1, 'other_stuf': '(...)'}

obj2 = {'cls': 2, 'other_stuf': '(...)'}

obj3 = {'cls': 3, 'other_stuf': '(...)'}


pickled = BytesIO(pickle.dumps(obj1) + pickle.dumps(obj2) + pickle.dumps(obj3))



print(pickled.getvalue())
print(pickled.tell())

print(pickle.load(pickled))

print(pickled.tell())
pos = pickled.tell()
pickled.seek(0, 2)
print(pickled.tell())
pickled.write(pickle.dumps(obj1))
pickled.seek(pos, 0)
# print(pickled.getvalue())

print(pickle.load(pickled))

print(pickled.tell())

print(pickle.load(pickled))

print(pickled.tell())

print(pickle.load(pickled))

print(pickled.tell())

print(pickled.)