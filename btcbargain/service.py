from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant
from btcbargain.transaction import BargainTransaction
from btcbargain.input import BargainInput, BargainSignature


class BTCBargainTransactionService:
    def __init__(
            self,
            signature_service
    ):
        self.signature_service = signature_service

    def _add_output(
            self, output: BargainOutput
    ):
        pass

    def _add_input(
            self, transaction: BargainTransaction, tx_input: BargainInput
    ):
        pass

    def get_transaction(self, transaction: BargainTransaction) -> 'BargainTransaction':
        return transaction

    def add_participants(
            self, transaction: BargainTransaction, participant: BargainParticipant
    ):
        pass

    def seal_transaction(
            self, transaction: BargainTransaction, *signatures: BargainSignature
    ):
        """
        This method MUST apply the SIGHASH_ALL signature
        to all the participant's inputs.
        Due the behaviour of SIGHASH_ALL, the sealing must be done
        once all the outputs are defined.
        """
        pass
