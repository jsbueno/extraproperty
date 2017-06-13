
_classproperty_data = {}


def _ensure_init_subclass(descriptor, owner):
    # Get the previous __init_subclass__ as a "classmethod" object, not as bound method:
    wrapped = [inisub for inisub in (cls.__dict__.get('__init_subclass__', None) for cls in owner.__mro__) if inisub][0]
    def __init_subclass__(cls, *args, **kw):
        nonlocal owner
        for descriptor in _classproperty_data[owner]:
            attr = getattr(cls, descriptor.name)
            if attr is descriptor and not any(supercls in descriptor.classes  for supercls in cls.__mro__[1:]):
                raise TypeError(f'You must assign a value to "{attr.name}" at class declaration')
            elif attr is not descriptor:
                # A new attribute was assigned to ower descriptor on this class body:
                descriptor.classes[cls] = attr
                delattr (cls, descriptor.name)
        # Manually perform the "descriptor get" so that the orginal __init_subclass__
        # is bound to the correct class.
        return wrapped.__get__(None, cls)(*args, **kw)

    if owner not in _classproperty_data:
        _classproperty_data[owner] = []
        owner.__init_subclass__ = classmethod(__init_subclass__)

    _classproperty_data[owner].append(descriptor)


class classproperty:
    """Descriptor to define an Abstract Property in a class.

    No derived classes can be created without redefining the property -
    and it prevents assignment of different values to the attribute
    in instances of the class (although it can be overwritten if assigned
    to in a class after it is created).
    No need t use ABCMeta classes for this- it works by auto-wrapping
    "__init_subclass__".
    """

    def __init__(self):
        self.classes = {}

    def __get__(self, instance, owner):
        for cls in owner.__mro__[:-1]:
            if cls in self.classes:
                return self.classes[cls]
        return self

    def __set__(self, instance, value):
        raise TypeError(f'It is not possible to assign a new value to classproperty "{self.name}"')

    def __delete__(self, instance):
        raise TypeError('ClassProperties are undestructible')

    def __hash__(self):
        return hash(id(self))

    def __set_name__(self, owner, name):
        self.name = name
        _ensure_init_subclass(self, owner)

    def __repr__(self):
        return f'Attribute "{self.name}" on classes {self.classes.keys()}'

