# Introduction #

The implementation of PyGoWave Server produces some nice by-products. PyCow is one of them.

PyCow translates Python code to JavaScript code with the "MooTools way of class declaration".

It generally depends on the fact that JavaScript shares almost all of its semantics with Python,
so PyCow just has to change the syntax most of the time.

# Examples #

The behavior of PyCow can be seen at best on some examples.

Note: PyCow currently removes any comments in the code.

## Namespaces ##

PyCow can wrap your Python module in a namespace (commandline: pycow.py -n namespace inputfile.py).
If you do that, PyCow will look for a optional `__all__` variable in your module and make only the specified
classes/functions publicly accessible.

**Python:**
```
__all__ = ["Someclass", "a_function"]

@Class
class Someclass(object):
    def __init__(self, something):
        self.something = something

def a_function():
    print "hello"

def another_function():
    print "test"
```

**Resulting JavaScript:**
```
var namespace = (function () {
    var Someclass = new Class({
        initialize: function (something) {
            this.something = something;
        }
    });

    var a_function = function () {
        alert("hello");
    };

    var another_function = function () {
        alert("test");
    };

    return {
        Someclass: Someclass,
        a_function: a_function
    }
})();
```

## Imports ##

PyCow does not handle imports for now (it will probably in the next release), so import statements are simply ignored.

**Python:**
```
from decorators import Implements, Class
from utils import Events, Options
```

**Resulting JavaScript:**
```
/* from decorators import Implements, Class */;
/* from utils import Events, Options */;
```

## Classes, subclasses and functions ##

**There is an important change since the last release:** I have ported some of MooTools' functionality
to Python in order to keep semantics clean between the two languages. This introduces the "Class" decorator, which
fixes an issue and adds the "implements" method to the class. Note that class decorators are supported in Python 2.6
and later only, please upgrade your installation if neccessary.

**Python:**
```
@Class
class Someclass(object):
    """
    Docstring of class
    """
    def __init__(self, something): # PyCow removes 'self' from method declarations
        """
        Docstring of constructor/method
        """
        self.something = something + "string literal" # PyCow replaces 'self' with 'this'
    
    def a_method(self, otherthing):
        print self.something + otherthing # 'print' is translated to 'alert'
    
    def another_method(self):
        obj = SomeExtension() # PyCow can infer types of callables (even declared later); here it will place 'new', because SomeExtension is a class
        self.member = "test"

@Class
class SomeExtension(Someclass):
    def __init__(self):
        super(SomeExtension, self).__init__("1234") # PyCow correctly treats the 'super' function of Python; here it's the call to the super constructor
    
    def a_method(self, otherthing):
        super(SomeExtension, self).a_method(otherthing) # Here it's a call to the super class' method
        print otherthing, self.something

def a_function():
    """
    Docstring of function
    
    Note that PyCow removes
            whitespaces.
    
    
    
    And normalizes newlines.
    """
    test = 2 # PyCow automatically declares local variables
    test = 4 # once
    print test+     2 # Because PyCow parses semantics only, it will ignore whitespaces (but avoid to do something like that anyways)

obj = Someclass("a lengthy ")

obj.a_method("test") # PyCow's type inference does not include types of variables (atm)

a_function() # PyCow does not put "new" here, because a_function is a simple function
```

**Resulting JavaScript:**
```
/**
 * Docstring of class
 */
var Someclass = new Class({
    /**
     * Docstring of constructor/method
     */
    initialize: function (something) {
        this.something = something + "string literal";
    },
    a_method: function (otherthing) {
        alert(this.something + otherthing);
    },
    another_method: function () {
        var obj = new SomeExtension();
        this.member = "test";
    }
});

var SomeExtension = new Class({
    Extends: Someclass,
    initialize: function () {
        this.parent("1234");
    },
    a_method: function (otherthing) {
        this.parent.a_method(otherthing);
        alert(otherthing + " " + this.something);
    }
});

/**
 * Docstring of function
 *
 * Note that PyCow removes
 * whitespaces.
 *
 * And normalizes newlines.
 */
var a_function = function () {
    var test = 2;
    test = 4;
    alert(test + 2);
};

var obj = new Someclass("a lengthy ");

/* Warning: Cannot infer type of -> */ obj.a_method("test");

a_function();
```

## The "Implements" decorator ##

There is another feature in MooTools besides the Extends property of classes: The Implements property.

From the MooTools documentation:
> Implements is similar to Extends, except that it overrides properties without inheritance. Useful when
> implementing a default set of properties in multiple Classes.

This is often used in conjunction with the "Options" and "Events" utility classes of MooTools. I have
ported them to Python for your convenience. The following example also explains what is fixed by the
"Class" decorator.

**Python:**
```
@Implements(Options)
@Class
class ClassWithOptions(object):
    """
    A class with implements Options using the `Implements` decorator.
    This is MooTools functionality ported to Python.
    """
    
    # Note: In Python semantics, this declares a class-bound member, but MooTools
    # sees this as object-bound members. The Class decorator will convert all
    # class-bound members to object-bound members on instantiation.
    options = {
        "name": "value",
        "foo": "bar",
    }
    
    def __init__(self, options):
        self.setOptions(options)
        print self.options["foo"], self.options["name"]
    
    # Static methods supported
    @staticmethod
    def somestatic(input):
        print "Static " + input
```

**Resulting JavaScript:**
```
/**
 * A class with implements Options using the `Implements` decorator.
 * This is MooTools functionality ported to Python.
 */
var ClassWithOptions = new Class({
    Implements: Options,
    options: {
        name: "value",
        foo: "bar"
    },
    initialize: function (options) {
        /* Warning: Cannot infer type of -> */ this.setOptions(options);
        alert(this.options.foo + " " + this.options.name);
    }
});
ClassWithOptions.somestatic = function (input) {
    alert("Static " + input);
};
```

## Variable scope ##

**Python:**
```
global x # Because of the 'global' statement
x = "hello again" # PyCow does not declare x as local here

def another_function():
    global x
    x = "go ahead" # and here
    return x
```

**Resulting JavaScript:**
```
x = "hello again";

var another_function = function () {
    x = "go ahead";
    return x;
};
```

## If/else statement ##

**Python:**
```
if True:
    print "Welcome"
    if False:
        pass
    else:
        print "Nested if"
else:
    print "You're not welcome..."
```

**Resulting JavaScript:**
```
if (true) {
    alert("Welcome");
    if (false)
        /* pass */;
    else
        alert("Nested if");
}
else
    alert("You're not welcome...");
```

## While statement ##

**Python:**
```
i = 0
while i < 3 and not False: # While statement
    print i
    i += 1 # Assignment operator
```

**Resulting JavaScript:**
```
var i = 0;
while (i < 3 && !false) {
    alert(i);
    i += 1;
}
```

## For statement ##

**Python:**
```
for j in xrange(3): # For statement (xrange)
    print j

for j in xrange(1,4): # For statement (xrange; with start)
    print j

for j in xrange(1,4,2): # For statement (xrange; with start and step)
    print j

for j in xrange(4,1,-1): # For statement (xrange; with start and step backwards)
    print j

i = [1,2,3]
for j in i: # For statement (simple variable)
    print j

for j in ["a","b","c"+"d"]: # For statement (arbitrary expression)
    print j
```

**Resulting JavaScript:**
```
for (var j = 0; j < 3; j++)
    alert(j);

for (j = 1; j < 4; j++)
    alert(j);

for (j = 1; j < 4; j += 2)
    alert(j);

for (j = 4; j > 1; j--)
    alert(j);

for (j in i) {
    j = i[j];
    alert(j);
}

var __tmp_iter0_ = ["a", "b", "c" + "d"];
for (j in __tmp_iter0_) {
    j = __tmp_iter0_[j];
    alert(j);
}
delete __tmp_iter0_;
```

## Lists and dictionaries ##

**Python:**
```
f = lambda x: x*2 # Lambda functions

a = [1,2,3,f(2)] # List expression

print a[1:3] # Slicing

b = {} # Empty dictionary

# Dictionary with strings and numbers as indices
b = {"a": 1, "b": 2,
     1: "x", 2: "y",
     "-test-": 1+2, "0HAY0": "a"+"B"}

# Accessing subscript (simple string)
print b["a"]

# Accessing subscript (other string; assignment)
b["-test-"] = 3

# Accessing subscript (number)
print b[1]

# Deleting from map
del b["a"]
```

**Resulting JavaScript:**
```
var f = function (x) {return x * 2;};

var a = [1, 2, 3, /* Warning: Cannot infer type of -> */ f(2)];

alert(a.slice(1, 3));

var b = {};

b = {
    a: 1,
    b: 2,
    1: "x",
    2: "y",
    "-test-": 1 + 2,
    "0HAY0": "a" + "B"
};

alert(b.a);

b["-test-"] = 3;

alert(b[1]);

delete b.a;
```