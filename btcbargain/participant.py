import typing

from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput


class BargainParticipant:
    def __init__(
            self,
            absolute_fee: int,
            *tx_inputs: BargainInput,
            output: typing.Optional[BargainOutput] = None,
    ):
        self._absolute_fee = absolute_fee
        self.tx_inputs = tx_inputs
        self.output = output

    @property
    def transferring_amount(self) -> int:
        return sum([i.amount for i in self.tx_inputs])

    @property
    def paying_amount(self) -> int:
        return self.transferring_amount - self.receiving_amount - self.absolute_fee

    @property
    def receiving_amount(self) -> int:
        return self.output.amount

    @property
    def absolute_fee(self) -> int:
        return self._absolute_fee

    def participant_size(self) -> int:
        return self.output.size + sum([i.size for i in self.tx_inputs])

    @property
    def size_bytes(self) -> int:
        return sum([self.output.size] + [i.size for i in self.tx_inputs])

    @property
    def absolute_fees(self) -> int:
        return self._absolute_fee
