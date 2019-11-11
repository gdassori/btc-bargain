class BargainInput:
    def __init__(
            self,
            outpoint_hash: str,
            outpoint_index: int,
            amount: int,
            is_segwit: bool = True,
            signature=None,

     ):
        self.outpoint_hash = outpoint_hash
        self.outpoint_index = outpoint_index
        self.amount = amount
        self.is_segwit = is_segwit
        self.signature = signature
        self._size = None

    def set_size(self, size: int):
        """
        Set the input size. This method must be called by the
        CoreWallet's method which return the input size starting from
        the address.
        """
        self._size = size

    @property
    def size(self):
        """
        The final size of the input once signed.
        """
        return self._size

    def add_signature(self, signature: 'BargainSignature'):
        """
        !!Achtung!!

        Signature Hash Type: SIGHASH_NONE|ANYONECANPAY = 0x82
        This flag means the signature is committed ONLY to the input.

        This is *** VERY HARMFUL ***
        and the signature must be sealed by a second one of type SIGHASH_ALL.
        """
        self.signature = signature


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
