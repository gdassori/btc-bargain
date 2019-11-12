import hashlib
from unittest import TestCase, mock

import bitcoin
from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant
from btcbargain.service import BTCBargainTransactionService
from btcbargain.transaction import BargainTransaction


class TestHappyPath(TestCase):
    def setUp(self) -> None:
        self.signature_service = mock.Mock()
        self.sut = BTCBargainTransactionService(self.signature_service)
        self._bake()

    def _bake(self):
        self.privates = [
            hashlib.sha256('priv{}'.format(i).encode()).hexdigest() + '01' for i in range(0, 18)
        ]
        self._scripts = [
            bitcoin.mk_multisig_script(
                bitcoin.privtopub(self.privates[x]),
                bitcoin.privtopub(self.privates[x + 1]),
                bitcoin.privtopub(self.privates[x + 2]),
                3
            ) for x in range(0, 18, 3)
        ]
        self.addresses = [
            bitcoin.p2sh_scriptaddr(script, magicbyte=196) for script in self._scripts
        ]

    def test(self):
        p1 = BargainParticipant(
            'participant_1',
            int(0.0001 * 10 ** 8),
            BargainInput(  # received by self.address[2]
                outpoint_hash='83db16dcc199d25b9fc3aa4d47ccff44224f26c3c4995c844738e2363a307985',
                outpoint_index=0,
                amount=int(1 * 10 ** 8),
                signature='',
                size=203
            ),
            BargainInput(  # received by self.address[2]
                outpoint_hash='9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb',
                outpoint_index=1,
                amount=int(2 * 10 ** 8),
                signature='',
                size=203
            ),
            output=BargainOutput(
                address=self.addresses[0],
                amount=int(0.04 * 10 ** 8),
                size=23
            ),
        )
        p2 = BargainParticipant(
            'participant_2',
            int(0.0001 * 10 ** 8),
            BargainInput(  # received by self.address[3]
                outpoint_hash='4dc2b795bddb3d9227e267730c01a9690b273f753fff554f2db1bbc708bb2c3e',
                outpoint_index=1,
                amount=int(1 * 10 ** 8),
                signature='',
                size=203
            ),
            BargainInput(  # received by self.address[3]
                outpoint_hash='677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b',
                outpoint_index=1,
                amount=int(3 * 10 ** 8),
                signature='',
                size=203
            ),
            output=BargainOutput(
                address=self.addresses[1],
                amount=int(0.003 * 10 ** 8),
                size=23
            )
        )
        BargainTransaction.create(p1)
        transaction = BargainTransaction.create(p1)
        rawtx = transaction.make()
        p1.add_signature_to_input(
            0,
            bitcoin.segwit_multisign(
                rawtx,
                0,
                self._scripts[2],
                self.privates[2],
                p1.tx_inputs[0].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        p1.add_signature_to_input(
            1,
            bitcoin.segwit_multisign(
                rawtx,
                1,
                self._scripts[2],
                self.privates[2],
                p1.tx_inputs[1].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        payload = {
            'bargain_transaction_id': None,
            'current_absolute_fee_paid': 10000,
            'participants': [
                {
                    'absolute_fee': 10000,
                    'inputs': [
                        {
                            'amount': int(1 * 10 ** 8),
                            'is_segwit': True,
                            'outpoint_hash': '83db16dcc199d25b9fc3aa4d47ccff44224f26c3c4995c844738e2363a307985',
                            'outpoint_index': 0,
                            'signature': '3045022100817a694f588d0453aa04a3acec67f8f5758c63fac36d40c9016267420a484f'
                                         'd30220292bd7e5100d0fc047ba9ad2c0a07810c8e8d5791065ae8416351fe93ad9d4d782',
                            'size': 203
                        },
                        {
                            'amount': int(2 * 10 ** 8),
                            'is_segwit': True,
                            'outpoint_hash': '9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb',
                            'outpoint_index': 1,
                            'signature': '3044022003525fe82230107fa804abb0ea2518f6487a55e46ccb6806ea87df9955a8010'
                                         'b02204aa7fddc330512fe01eeac472a7ad0a9ab481e05e0d540916287238d9f793f4a82',
                            'size': 203
                        }
                    ],
                    'output': {
                        'address': self.addresses[0],
                        'amount': 4000000,
                        'size': 23
                    },
                    'participant_id': 'participant_1',
                    'participant_size': 23,
                    'paying_amount': 295990000,
                    'receiving_amount': 4000000,
                    'transferring_amount': 300000000
                }
            ],
            'sealed': False,
            'signatures': [],
            'total_size': 429
        }
        self.assertEqual(transaction.to_json(), payload)
        transaction.add_participant(p2)
        p2.add_signature_to_input(
            0,
            bitcoin.segwit_multisign(
                rawtx,
                0,
                self._scripts[3],
                self.privates[3],
                p2.tx_inputs[0].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        p2.add_signature_to_input(
            1,
            bitcoin.segwit_multisign(
                rawtx,
                1,
                self._scripts[3],
                self.privates[3],
                p2.tx_inputs[1].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        payload['participants'].append(
            {
                'absolute_fee': 10000,
                'inputs': [
                    {
                        'amount': int(1 * 10 ** 8),
                        'is_segwit': True,
                        'outpoint_hash': '4dc2b795bddb3d9227e267730c01a9690b273f753fff554f2db1bbc708bb2c3e',
                        'outpoint_index': 1,
                        'signature': '3044022044b9ebc1725214df2a49bf48364bbb6c74c2078a1c9b5e467481f065c85577f'
                                     '802207fefefc64fc0736b08f6614311ee18eaa3b03aed03da21d21522fa54710c4d1382',
                        'size': 203
                    },
                    {
                        'amount': int(3 * 10 ** 8),
                        'is_segwit': True,
                        'outpoint_hash': '677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b',
                        'outpoint_index': 1,
                        'signature': '3045022100cac1600e53b0705fa9da865bc24d7656130165e37c46ecc4b8535fad84ae81'
                                     '0802202cf734ba559900195007083bd473620c4f73b80dc2867777d6c9070df2bd09d382',
                        'size': 203
                    }
                ],
                'output': {
                    'address': self.addresses[1],
                    'amount': 300000,
                    'size': 23
                },
                'participant_id': 'participant_2',
                'participant_size': 23,
                'paying_amount': 399690000,
                'receiving_amount': 300000,
                'transferring_amount': 400000000
            }
        )
        payload['current_absolute_fee_paid'] = 20000
        payload['total_size'] = 858
        self.assertEqual(transaction.to_json(), payload)
        half_signed_rawtx = transaction.make()
        print(half_signed_rawtx)