```python
import math  # Fixed: E401 (split imports) Removed: F401 ('os' unused)


def compute(x, y):  # Fixed: E302 (two blank lines before function), E231 (whitespace after ',')
    return x * y + math.sqrt(x)  # Fixed: E225 (whitespace around operator)


def normalize(data):  # Fixed: E302 (two blank lines before function)
    result = []
    for v in data:
        if v > 0:  # Fixed: E225 (whitespace around operator)
            result.append(v / max(data))  # Fixed: E225 (whitespace around operator)
    return result


class Greeter:  # Fixed: E302 (two blank lines before class)
    def __init__(self, name):  # Fixed: E231 (whitespace after ',')
        self.name = name  # Fixed: E225 (whitespace around operator)

    def greet(self):  # Fixed: E301 (one blank line between methods)
        return "Hello, " + self.name  # Fixed: E225 (whitespace around operator)

# Removed: W391 (blank line at end of file)
```



