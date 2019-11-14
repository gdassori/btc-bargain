import typing

from btcbargain import exceptions
from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.transaction import BargainTransaction


OUTPUT_SIZE = 23


class BargainSealer:
    def __init__(
            self,
            *tx_inputs: BargainInput,
            output: typing.Optional[BargainOutput] = None,
            recipient_address=None
    ):
        self.tx_inputs = [x for x in tx_inputs]
        self.output = output
        self.recipient_address = recipient_address

    def add_recipient_address(self, address: str):
        self.recipient_address = address
        return self

    def add_signature_to_input(self, input_index: int, signature: str):
        self.tx_inputs[input_index].add_signature(signature)
        return self

    def to_json(self) -> typing.Dict:
        return {
            'inputs': [i.to_json() for i in self.tx_inputs],
            'output': self.output and self.output.to_json(),
            'recipient_address': self.recipient_address
        }

    @property
    def signatures(self) -> typing.Dict:
        res = {}
        for i in self.tx_inputs:
            if i.signature:
                res[i.outpoint_hash + ':{}'.format(i.outpoint_index)] = i.signature
        return res

    def mount_transaction(self, transaction: BargainTransaction) -> 'BargainSealer':
        if not self.recipient_address:
            raise exceptions.MissingSealerRecipient
        gathering_amount = 0
        for participant in transaction.participants:
            gathering_amount += participant.paying_amount
            for i in participant.tx_inputs:
                self.tx_inputs.append(i.clone())
        transaction.sealer = self
        self._add_gathering_output(gathering_amount)
        return self

    def _add_gathering_output(self, amount: int):
        self.output = BargainOutput(self.recipient_address, amount, OUTPUT_SIZE)
