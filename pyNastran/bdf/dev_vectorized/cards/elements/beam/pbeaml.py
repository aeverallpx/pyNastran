from six import  iteritems
from numpy import array, asarray

from pyNastran.bdf.field_writer_8 import print_card_8
from pyNastran.bdf.field_writer_16 import print_card_16
from pyNastran.bdf.dev_vectorized.cards.elements.property import Property

from pyNastran.bdf.cards.properties.beam import PBEAML as vPBEAML
from pyNastran.bdf.dev_vectorized.utils import slice_to_iter


class PBEAML(object):
    type = 'PBEAML'

    def __iter__(self):
        pids = self.property_id
        for pid in pids:
            yield pid

    def values(self):
        pids = self.property_id
        for pid in pids:
            yield self.__getitem__(pid)

    def items(self):
        pids = self.property_id
        for pid in pids:
            yield pid, self.__getitem__(pid)

    def __getitem__(self, property_id):
        property_id, int_flag = slice_to_iter(property_id)
        obj = PBEAML(self.model)

        properties = {}
        for pid in sorted(property_id):
            properties[pid] = self.properties[pid]
        obj.n = len(property_id)
        obj.properties = properties
        obj.property_id = sorted(self.properties.keys())
        #obj._comments = obj._comments[index]
        #obj.comments = obj.comments[index]
        return obj

    def allocate(self, ncards):
        pass

    def slice_by_index(self, i):
        i = asarray(i)
        obj = PBEAML(self.model)
        raise NotImplementedError()
        return obj

    def __init__(self, model):
        """
        Defines the PBEAML object.

        :param model: the BDF object
        :param cards: the list of PBEAML cards
        """
        self.properties = {}
        self.model = model
        self.n = 0

    def add(self, card, comment=''):
        prop = vPBEAML(card, comment=comment)
        self.properties[prop.pid] = prop

    def build(self):
        self.n = len(self.properties)
        self.property_id = array(sorted(self.properties.keys()), dtype='int32')

    #=========================================================================
    def write_card(self, f, size=8, property_id=None):
        if size == 8:
            for pid, prop in sorted(iteritems(self.properties)):
                f.write(prop.write_card(size, print_card_8))
        else:
            for pid, prop in sorted(iteritems(self.properties)):
                f.write(prop.write_card(size, print_card_16))
