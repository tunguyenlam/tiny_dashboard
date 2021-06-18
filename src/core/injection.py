import types
import inspect
class Container:
    """
    Storing objects and provide by injection.
    """
    __container_instance = None

    @staticmethod
    def get_instance():
        if Container.__container_instance == None:
            Container()
        return Container.__container_instance

    def __init__(self):
        """
        2 types of objects are seperatly stored.
        """
        self.factories = {}
        self.instances = {}
        Container.__container_instance = self

    def add(self, obj, id):
        if id is None:
            id = obj.__name__
        # only store class with __init__()
        if inspect.isclass(obj):
            self.factories[id] = obj
        else:
            self.instances[id] = obj

    def __getitem__(self, id):
        try:
            instance = self.instances[id]
        except KeyError:
            try:
                instance = self.instances[id] = self.factories[id]()
            except KeyError:
                raise KeyError("No object registered for id '%s'" % id)
        return instance

def add_to_context(obj, id = None):
    if id is None:
        id = obj.__name__
    Container.get_instance().add(obj, id)

def inject(object_ids):
    """
    We can inject into class or function.
    1. Sample to inject class:

        @inject(object_ids=['dependency', 'word'])
        class Dependency:
            def __init__(self, *args, dep, word):
                ....

    2. Sample to inject complicated params functions:

        @inject(object_ids=['step_checker'])
        def transform(self, *args, step_checker, **kwargs):
            ....

    :param object_ids: ids of injected object
    :return:
    """
    def wrap(cls):
        if isinstance(cls, types.FunctionType):
            function = cls
            def new_function(*args, **kwargs):
                container = Container.get_instance()
                deps = {id : container[id] for id in object_ids}
                z = {**deps, **kwargs}
                return function(*args, **z)
            return new_function
        else:
            orig_init = cls.__init__
            def new_init(self, *args, **kwargs):
                """
                Inject init function. cool thing!
                :param self: object
                :return: init
                """
                container = Container.get_instance()
                deps = {id: container[id] for id in object_ids}
                kwargs.update(**deps)
                orig_init(self, *args, **kwargs)

            cls.__init__ = new_init
            return cls
    return wrap


def provides(features, container):
    def wrap(cls):
        for feature in features:
            container.add(cls, feature)
        return cls
    return wrap