import math, os

def compute(x,y):
    return x* y+math.sqrt(x)  

def normalize(data):
    result=[]
    for v in data:
        if v>0:
            result.append(v/ max(data))
    return result

class Greeter:
    def __init__(self,name):
        self.name=name
    def greet(self):
        return "Hello, "+self.name


