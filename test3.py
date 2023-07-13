'''
    Test updating class variable for every instance of class
'''
class Test:
    uid = 0

    @classmethod
    def next_id(cls) -> int:
        cls.uid += 1
        return cls.uid
    
    def __init__(self):
        self._id = self.next_id()

    def id(self):
        return self._id

t1 = Test()
t2 = Test()
t3 = Test()

print(t1.id())
print(t2.id())
print(t3._id)
'''

class MyClass:
    var1 = 1

    @classmethod
    def update(cls):
        cls.var1 += 1

    def __init__(self):
        self.update()
        self.my_id = self.var1

a = MyClass()
b = MyClass()
print(MyClass.var1)
print(a.my_id)
print(b.my_id)
'''

