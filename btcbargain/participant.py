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
        self.outputs = output

    def transferring_amount(self) -> int:
        pass

    def paying_amount(self) -> int:
        pass

    def receiving_amount(self) -> int:
        pass

    @property
    def absolute_fee(self) -> int:
        return self._absolute_fee

    def participant_size(self) -> int:
        pass

    @property
    def size_bytes(self) -> int:
        return 10  # FIXME TODO sum inputs\outputs size
