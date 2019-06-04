"""
"""
import operator
from service.identified_coast import IdentifiedCoast


class Border:
    def __init__(self, t1, t2, shared_coast=False):
        self.territories = (t1, t2)
        self.shared_coast = shared_coast


class IdentifiedCoastBorder:
    def __init__(self, territory, identified_coast):
        self.territory = territory
        self.identified_coast = identified_coast

    identified_coast = property(operator.attrgetter('_identified_coast'))

    @identified_coast.setter
    def identified_coast(self, i):
        if not isinstance(i, IdentifiedCoast):
            raise Exception("Identified coast must be of type IdentifiedCoast")
        self._identified_coast = i
