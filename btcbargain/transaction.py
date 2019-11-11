import typing

from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant


class BargainTransaction:
    def __init__(self):
        self._participants = []
        self.bargain_transaction_id = None

    @property
    def total_size(self) -> int:
        total = 0
        for p in self._participants:
            for s in p.size_bytes:
                total += s
        return total

    @property
    def inputs(self) -> typing.List[BargainInput]:
        res = []
        for p in self._participants:
            res.extend(p.tx_inputs)
        return res

    @property
    def outputs(self) -> typing.List[BargainOutput]:
        return [p.output for p in self._participants]

    @property
    def current_absolute_fee_paid(self) -> int:
        total = 0
        for p in self._participants:
            for f in p.absolute_fee:
                total += f
        return total

    @property
    def participants(self) -> typing.List[BargainParticipant]:
        return self._participants

    def add_participant(self, p1: BargainParticipant) -> 'BargainTransaction':
        self._participants.append(p1)
        return self
