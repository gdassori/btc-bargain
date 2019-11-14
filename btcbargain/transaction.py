import typing

import bitcoin

from btcbargain import exceptions
from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant

REPLACE_BY_FEE_SEQUENCE_NUMBER = 0xffffffff - 2


class BargainTransaction:
    def __init__(self):
        self._participants = []
        self._sealer = None
        self.bargain_transaction_id = None
        self._raw = None

    @property
    def sealed(self):
        if not self.sealer:
            return False
        status = []
        for p in self.participants:
            for i in p.tx_inputs:
                status.append(
                    self.sealer.signatures.get(i.outpoint_hash + ':' + str(i.outpoint_index))
                )
        return bool(status and all(status))

    @property
    def sealer(self):
        return self._sealer

    @sealer.setter
    def sealer(self, value):
        from btcbargain.sealer import BargainSealer
        assert isinstance(value, BargainSealer)
        self._sealer = value

    @property
    def raw(self):
        return self._raw

    @classmethod
    def create(cls, *participants) -> 'BargainTransaction':
        i = cls()
        for p in participants:
            i.add_participant(p)
        return i

    @property
    def total_size(self) -> int:
        total = 0
        counted = []
        for p in self._participants:
            counted.extend(['{}:{}'.format(i.outpoint_index, i.outpoint_hash) for i in p.tx_inputs])
            total += p.size_bytes
        if self.sealer:
            for i in self.sealer.tx_inputs:
                if '{}:{}'.format(i.outpoint_index, i.outpoint_hash) not in counted:
                    total += i.size
            if self.sealer.output:
                total += self.sealer.output.size
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
        return self._participants

    def add_participant(self, p: BargainParticipant) -> 'BargainTransaction':
        self._participants.append(p)
        if self.raw:
            self.make()
        return self

    def add_sealer(self, s) -> 'BargainTransaction':
        self._sealer = s
        if self.raw:
            self.make()
        return self

    def to_json(self) -> typing.Dict:
        return {
            'bargain_transaction_id': self.bargain_transaction_id,
            'participants': [p.to_json() for p in self.participants],
            'sealer': self.sealer and self.sealer.to_json(),
            'sealed': self.sealed,
            'total_size': self.total_size,
            'current_absolute_fee_paid': self.current_absolute_fee_paid,
        }

    def make(self) -> 'BargainTransaction':
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
        self._raw = rawtx
        return self

    def seal(self):
        index = 0
        for p in self.participants:
            for i, o in enumerate(p.tx_inputs):
                if o.signature:
                    signatures = [o.signature]
                    sealing_signature = self.sealer and self.sealer.signatures.get(
                        o.outpoint_hash + ':' + str(o.outpoint_index), None
                    )
                    if not sealing_signature:
                        raise exceptions.MissingSealerSignature(
                            o.outpoint_hash + ':' + str(o.outpoint_index)
                        )
                    sealing_signature and signatures.append(sealing_signature)
                    if o.is_segwit:
                        assert o.script
                        self._raw = bitcoin.apply_segwit_multisignatures(
                            self._raw, index, o.script, signatures, nested=True
                        )
                    else:
                        self._raw = bitcoin.apply_multisignatures(self._raw, index, o.script, signatures)
                else:
                    raise exceptions.MissingClientSignature
                index += 1
        return self
