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
        """
        Set the input size. This method must be called by the
        CoreWallet's method which return the input size starting from
        the address.
        """
        self._size = int(size)
        return self

    @property
    def size(self):
        """
        The final size of the input once signed.
        """
        return int(self._size)

    def add_signature(self, signature: 'BargainSignature'):
        """
        !!Achtung!!

        Signature Hash Type: SIGHASH_NONE|ANYONECANPAY = 0x82
        This flag means the signature is committed ONLY to the input.

        This is *** VERY HARMFUL ***
        and the signature must be sealed by a second one of type SIGHASH_ALL.
        """
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


class BargainSignature:
    """
    This signature MUST be of type SIGHASH_NONE|ANYONECANPAY
    And is committed to the input only.
    The final tx is sealed by the backend with SIGHASH_ALL
    """
    def __init__(
            self,
            data: str,
            tx_input: BargainInput
    ):
        self.tx_input = tx_input
        self.data = data
