from unittest import TestCase, mock

from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant
from btcbargain.service import BTCBargainTransactionService


class TestHappyPath(TestCase):
    def setUp(self) -> None:
        self.signature_service = mock.Mock()
        self.bargain_repository = mock.Mock()
        self.sut = BTCBargainTransactionService(
            self.signature_service,
            self.bargain_repository
        )

    def test(self):
        p1 = BargainParticipant(
            0.0001 * 10 ** 8,
            BargainInput(
                outpoint_hash='ff' * 32,
                outpoint_index=0,
                amount=0.01 * 10**8,
                signature='aa'*68
            ),
            BargainInput(
                outpoint_hash='ff' * 32,
                outpoint_index=0,
                amount=0.005 * 10 ** 8,
                signature='bb' * 68
            ),
            output=BargainOutput(
                address='btcAddress1',
                amount=0.004 * 10**8
            ),
        )
        p2 = BargainParticipant(
            0.0001 * 10 ** 8,
            BargainInput(
                outpoint_hash='ca' * 32,
                outpoint_index=0,
                amount=0.006 * 10**8,
                signature='cc' * 68
            ),
            BargainInput(
                outpoint_hash='ca' * 32,
                outpoint_index=0,
                amount=0.02 * 10 ** 8,
                signature='dd' * 68
            ),
            output=BargainOutput(
                address='btcAddress2',
                amount=0.003 * 10**8
            )
        )
        unsealed_transaction_p1 = self.sut.create_transaction(p1)
        unsealed_transaction_p1 = self.sut.get_transaction(unsealed_transaction_p1)
        self.assertEqual(
            unsealed_transaction_p1,
            ""
        )
        unsealed_transaction_p1_p2 = self.sut.add_participants(
            unsealed_transaction_p1,
            p2
        )
        self.assertEqual(
            unsealed_transaction_p1_p2,
            ""
        )
        sealed_transaction = self.sut.seal_transaction(
            unsealed_transaction_p1_p2
        )
        self.assertEqual(
            sealed_transaction,
            ""
        )
