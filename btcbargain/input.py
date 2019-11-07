class BargainInput:
    def __init__(
            self,
            outpoint_hash: str,
            outpoint_index: int,
            amount: int,
            is_segwit: bool = True,
            signature=None
     ):
        self.outpoint_hash = outpoint_hash
        self.outpoint_index = outpoint_index
        self.amount = amount
        self.is_segwit = is_segwit
        self.signature = signature

    @property
    def current_size(self):
        pass

    @property
    def final_estimated_size(self):
        pass

    def add_signature(self, signature: 'BargainSignature'):
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
