import typing

from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput


class BargainParticipant:
    def __init__(
            self,
            participant_id: str,
            absolute_fee: int,
            *tx_inputs: BargainInput,
            output: typing.Optional[BargainOutput] = None,
    ):
        self._absolute_fee = absolute_fee
        self.tx_inputs = tx_inputs
        self.output = output
        self.participant_id = participant_id

    def add_signature_to_input(self, input_index: int, signature: str):
        self.tx_inputs[input_index].add_signature(signature)
        return self

    @property
    def transferring_amount(self) -> int:
        return int(sum([i.amount for i in self.tx_inputs]))

    @property
    def paying_amount(self) -> int:
        return int(self.transferring_amount - self.receiving_amount - self.absolute_fee)

    @property
    def receiving_amount(self) -> int:
        return int(self.output.amount)

    @property
    def absolute_fee(self) -> int:
        return int(self._absolute_fee)

    @property
    def participant_size(self) -> int:
        return int(self.output.size or 0 + sum([i.size for i in self.tx_inputs]))

    @property
    def size_bytes(self) -> int:
        return int(sum([self.output.size or 0] + [i.size for i in self.tx_inputs]))

    @property
    def absolute_fees(self) -> int:
        return int(self._absolute_fee)

    def to_json(self) -> typing.Dict:
        return {
            'inputs': [i.to_json() for i in self.tx_inputs],
            'output': self.output and self.output.to_json(),
            'transferring_amount': self.transferring_amount,
            'paying_amount': self.paying_amount,
            'receiving_amount': self.receiving_amount,
            'absolute_fee': self.absolute_fee,
            'participant_size': self.participant_size,
            'participant_id': self.participant_id
        }
