from .squatnet import SquatNet
from ..source import Source

class SquatNetMontpellier(Source, SquatNet):
    location = (43.6084009, 3.8793055)
    distance = 100

    def __init__(self, *args, **kwargs):
        super().__init__(city='Montpellier', country='FR')
