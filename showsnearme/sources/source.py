from .sources import Sources


class Source:
    location = (0, 0)
    distance = 100

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Sources.register(cls)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
