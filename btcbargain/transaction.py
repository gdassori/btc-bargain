import typing

import bitcoin
from bitcoin import SIGHASH_ANYONECANPAY, SIGHASH_NONE

from btcbargain import exceptions
from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant


REPLACE_BY_FEE_SEQUENCE_NUMBER = 0xffffffff - 2


class BargainTransaction:
    """
    Inputs order MUST be kept.
    A participant nor its input can leave the transaction, otherwise all the cur_input_index+N inputs
    signatures would be invalidated by shifting their position inside the outpoints list.
    """
    def __init__(self):
        self._participants = []
        self.bargain_transaction_id = None
        self._sealing_signatures = []

    @property
    def sealing_signatures(self):
        return self._sealing_signatures

    @classmethod
    def create(cls, *participants) -> 'BargainTransaction':
        i = cls()
        for p in participants:
            i.add_participant(p)
        return i

    @property
    def total_size(self) -> int:
        total = 0
        for p in self._participants:
            total += p.size_bytes
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
            total += p.absolute_fee
        return total

    @property
    def participants(self) -> typing.List[BargainParticipant]:
        """
        strictly keep this list in its original order
        """
        return self._participants

    def add_participant(self, p: BargainParticipant) -> 'BargainTransaction':
        self._participants.append(p)
        return self

    def to_json(self) -> typing.Dict:
        return {
            'bargain_transaction_id': self.bargain_transaction_id,
            'participants': [
                p.to_json() for p in self.participants
            ],
            'sealed': self.inputs and len(self.sealing_signatures) == len(self.inputs),
            'total_size': self.total_size,
            'current_absolute_fee_paid': self.current_absolute_fee_paid,
            'signatures': self.sealing_signatures
        }

    def make(self) -> str:
        outpoints = []
        for p in self.participants:
            for i, o in enumerate(p.tx_inputs):
                outpoints.append(
                    {
                        'output': '{}:{}'.format(o.outpoint_hash, o.outpoint_index),
                        'value': o.amount,
                        'segregated': o.is_segwit,
                        'sequence': REPLACE_BY_FEE_SEQUENCE_NUMBER,

                    }
                )
        outputs = [
            {
                'value': o.amount,
                'address': o.address,
            } for o in [p.output for p in self.participants]
        ]
        rawtx = bitcoin.mktx(*outpoints, *outputs)
        for p in self.participants:
            for i, o in enumerate(p.tx_inputs):
                if o.signature:
                    if o.is_segwit:
                        rawtx = bitcoin.apply_segwit_multisignatures(rawtx, i, o.script, [o.signature])
                    else:
                        rawtx = bitcoin.apply_multisignatures(rawtx, i, o.script, [o.signature])
        return rawtx

    def add_sealing_signatures(self, *signatures):
        for p in self._participants:
            if not all(len(i.signature) for i in p.tx_inputs):
                raise exceptions.MissingClientSignature
            if not all(i.verify_signature_for_sighash_type(SIGHASH_NONE | SIGHASH_ANYONECANPAY) for i in p.tx_inputs):
                raise exceptions.InvalidClientSignature
        if len(signatures) != len(self.inputs):
            raise exceptions.InconsistentSignaturesAmount
        return self
