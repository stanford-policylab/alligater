# CrocoDSL

CrocoDSL is a boolean expression DSL that was originally written to simplify defining populations for `Alligater`.

Examples:

```
1 Eq 1

1 Lt 2

$id Eq 'foo'

(1 Eq 1) And ($id Eq 'foo')

Hash($id) < 0.5

Not($id Eq 'bar')

Hash(Concat('salt', $id)) < 0.5
```

### Functions

It's easy to extend `CrocoDSL` with more functions.
Just add them to `func.py`.

### Fields

Each expression is evaluated against an `entity` and, optionally, a `context`.
Properties in the expression begin with the `$` sign, such as `$id`.
This will extract the relevant property from `entity`.

We do not distinguish between Python items and properties.
So for example the following assertion passes:

```py
from crocodsl import parse


item_ent = {
    'id': 'foo',
}

class MyEnt:
    def __init__(self, id_):
        self.id = id_

prop_ent = MyEnt('foo')

# Expression that extracts the `id` field.
expr = parse('$id')

assert expr(item_ent) == expr(prop_ent)
```

#### Nesting

You can reference nested fields with dot syntax.
Missing fields are not errors; they simply evaluate to `None`.

```
$child.$id
```

#### Context

You can even use methods as fields.
If your method takes arguments, pass them into the function evaluation using the `context` keyword argument.
Your method must use named arguments, and they will be injected by name from the `context`.

```py
from crocodsl import parse


class FancyObj:

    def next_court_date(self, *, current_time):
        """Find next court date based on the current time."""
        ...


expr = parse("Not($next_court_date Eq None)")

my_obj = FancyObj(...)

# Reference the result of calling a method as a field using args from context.
has_next_court_date = expr(my_obj, context={'current_time': ...})
```

### Logging

You can pass a log function when evaluating an expression to generate a detailed trace of evaluation steps.
This is useful for debugging.

```py
from crocodsl import parse


expr = parse("Hash(Concat('pfx', $id)) Lt 0.5")
expr({'id': 'foo'}, log=print)
```
