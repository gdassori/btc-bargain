class BargainInput:
    def __init__(
            self,
            outpoint_hash: str,
            outpoint_index: int,
            amount: int,
            is_segwit: bool = True,
            signature=None,
            size=0,
            script=None
     ):
        self.outpoint_hash = outpoint_hash
        self.outpoint_index = outpoint_index
        self._amount = amount
        self.is_segwit = is_segwit
        self.signature = signature
        self._size = size
        self._script = script

    @property
    def script(self):
        return self._script

    @property
    def amount(self):
        return int(self._amount)

    def set_size(self, size: int):
        self._size = int(size)
        return self

    @property
    def size(self):
        """
        The final size of the input once signed.
        """
        return int(self._size)

    def add_signature(self, signature: str):
        self.signature = signature
        return self

    def to_json(self):
        return {
            'outpoint_hash': self.outpoint_hash,
            'outpoint_index': self.outpoint_index,
            'amount': self.amount,
            'is_segwit': self.is_segwit,
            'size': self.size,
            'signature': self.signature
        }

    def verify_signature_for_sighash_type(self, sighash_type):
        return True

    def clone(self) -> 'BargainInput':
        return BargainInput(
            self.outpoint_hash,
            self.outpoint_index,
            self._amount,
            self.is_segwit,
            '',
            self._size,
            self._script,
        )
