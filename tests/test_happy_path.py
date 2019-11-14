import hashlib
from unittest import TestCase, mock
from unittest.mock import ANY

import bitcoin
from btcbargain.input import BargainInput
from btcbargain.output import BargainOutput
from btcbargain.participant import BargainParticipant
from btcbargain.sealer import BargainSealer
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
                2
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
                size=203,
                script=self._scripts[2]
            ),
            BargainInput(  # received by self.address[2]
                outpoint_hash='9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb',
                outpoint_index=1,
                amount=int(2 * 10 ** 8),
                signature='',
                size=203,
                script=self._scripts[2]
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
                size=203,
                script=self._scripts[3]
            ),
            BargainInput(  # received by self.address[3]
                outpoint_hash='677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b',
                outpoint_index=1,
                amount=int(3 * 10 ** 8),
                signature='',
                size=203,
                script=self._scripts[3]
            ),
            output=BargainOutput(
                address=self.addresses[1],
                amount=int(0.003 * 10 ** 8),
                size=23
            )
        )
        BargainTransaction.create(p1)
        transaction = BargainTransaction.create(p1)
        transaction.make()
        p1.add_signature_to_input(
            0,
            bitcoin.segwit_multisign(
                transaction.raw,
                0,
                p1.tx_inputs[0].script,
                self.privates[2*3],
                p1.tx_inputs[0].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        p1.add_signature_to_input(
            1,
            bitcoin.segwit_multisign(
                transaction.raw,
                1,
                p1.tx_inputs[1].script,
                self.privates[2*3],
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
                            'signature': ANY,
                            'size': 203
                        },
                        {
                            'amount': int(2 * 10 ** 8),
                            'is_segwit': True,
                            'outpoint_hash': '9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb',
                            'outpoint_index': 1,
                            'signature': ANY,
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
            'sealer': None,
            'total_size': 429
        }
        self.assertEqual(transaction.to_json(), payload)
        transaction.add_participant(p2)
        p2.add_signature_to_input(
            0,
            bitcoin.segwit_multisign(
                transaction.raw,
                0,
                p1.tx_inputs[0].script,
                self.privates[3*3],
                p2.tx_inputs[0].amount,
                hashcode=bitcoin.SIGHASH_NONE | bitcoin.SIGHASH_ANYONECANPAY
            )
        )
        p2.add_signature_to_input(
            1,
            bitcoin.segwit_multisign(
                transaction.raw,
                1,
                p1.tx_inputs[1].script,
                self.privates[3*3],
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
                        'signature': ANY,
                        'size': 203
                    },
                    {
                        'amount': int(3 * 10 ** 8),
                        'is_segwit': True,
                        'outpoint_hash': '677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b',
                        'outpoint_index': 1,
                        'signature': ANY,
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
        self.assertFalse(transaction.sealed)
        sealer = BargainSealer()
        sealer.add_recipient_address('2N9nL6NHhT3Ac7NXgsn1qa4ywNDqRPHaowU').mount_transaction(transaction)
        index = 0
        for ip, p in enumerate(transaction.participants):
            for i, v in enumerate(p.tx_inputs):
                sealer.add_signature_to_input(
                    index,
                    bitcoin.segwit_multisign(
                        transaction.raw,
                        index,
                        v.script,
                        self.privates[((index+2) * 3) + 1],
                        v.amount,
                        hashcode=bitcoin.SIGHASH_ALL
                    )
                )
                index += 1
        expected_transaction = {
            "bargain_transaction_id": None,
            "participants": [
                {
                    "inputs": [
                        {
                            "outpoint_hash": "83db16dcc199d25b9fc3aa4d47ccff44224f26c3c4995c844738e2363a307985",
                            "outpoint_index": 0,
                            "amount": 100000000,
                            "is_segwit": True,
                            "size": 203,
                            "signature": "304502210080cfce427024e6e259bee117c787d5041c2522b5a3c58ed6f45105f2d16613"
                                         "380220193b619c2ec84ffd05310a74ba225d8ebde830e7d013aa231dcd718573cccbc082"
                        },
                        {
                            "outpoint_hash": "9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb",
                            "outpoint_index": 1,
                            "amount": 200000000,
                            "is_segwit": True,
                            "size": 203,
                            "signature": "3043021f20946e5ed0ef24b4578fe8307675f21ba61c845b4436f58af5cbb0edba3e7f"
                                         "022069c9bc51969e177bd0bfaac2fd759d74a1c4fa41519a8fa19c5d2e3a8c2c56d982"
                        }
                    ],
                    "output": {
                        "address": "2NBKXce23hdu3eDUmv17fB1vaDLQcayV5NF",
                        "amount": 4000000,
                        "size": 23
                    },
                    "transferring_amount": 300000000,
                    "paying_amount": 295990000,
                    "receiving_amount": 4000000,
                    "absolute_fee": 10000,
                    "participant_size": 23,
                    "participant_id": "participant_1"
                },
                {
                    "inputs": [
                        {
                            "outpoint_hash": "4dc2b795bddb3d9227e267730c01a9690b273f753fff554f2db1bbc708bb2c3e",
                            "outpoint_index": 1,
                            "amount": 100000000,
                            "is_segwit": True,
                            "size": 203,
                            "signature": "3045022100a768c539d81cf6961368a7724fff650a243b40aab687fc2d219640724b6354"
                                         "180220537012c3f7eb7191d30234f5d847b11c0e91b61aa7e0b6676a2150fff0a2d5a882"
                        },
                        {
                            "outpoint_hash": "677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b",
                            "outpoint_index": 1,
                            "amount": 300000000,
                            "is_segwit": True,
                            "size": 203,
                            "signature": "3045022100baed44f2d1a79651da23459de3f98baab50bb3f2bf2f95959a3f187f198855"
                                         "ce02203e2d3b499060ef9a378568c083c039ab33d640733dbc1153f0862415bd76da6182"
                        }
                    ],
                    "output": {
                        "address": "2NBNzpn6wJJexvYehBULpz95MfnU4LEwC65",
                        "amount": 300000,
                        "size": 23
                    },
                    "transferring_amount": 400000000,
                    "paying_amount": 399690000,
                    "receiving_amount": 300000,
                    "absolute_fee": 10000,
                    "participant_size": 23,
                    "participant_id": "participant_2"
                }
            ],
            "sealed": True,
            "sealer": {
                "inputs": [
                    {
                        "amount": 100000000,
                        "is_segwit": True,
                        "outpoint_hash": "83db16dcc199d25b9fc3aa4d47ccff44224f26c3c4995c844738e2363a307985",
                        "outpoint_index": 0,
                        "signature": "3044022031d77ab1376a0374b678356d135409762faf6ae013b265d80c39326c6c6cbeb"
                                     "a02203484bf3dd932a805d38d168dca5e89edce98fc699558a1a4391d0a1f035c804901",
                        "size": 203
                    },
                    {
                        "amount": 200000000,
                        "is_segwit": True,
                        "outpoint_hash": "9c79cb282dcd0e03125553c5e515093a64093035aa0ce0c34d1fcc7ff29a5acb",
                        "outpoint_index": 1,
                        "signature": "3045022100d68f40f1ced0d984567b6a354d82d1a5a33bad93f7e2447b32464369147706"
                                      "44022063074e3d476f532c774ecfe6fc7fa19b491c92d2a9f1885047bf024680ac461301",
                        "size": 203
                    },
                    {
                        "amount": 100000000,
                        "is_segwit": True,
                        "outpoint_hash": "4dc2b795bddb3d9227e267730c01a9690b273f753fff554f2db1bbc708bb2c3e",
                        "outpoint_index": 1,
                        "signature": "3044022042ce722514a729f76813fb016acc1c66aa3449e4edd0fd5e4e034abf770c68e"
                                     "d02205ece1b49dda7d7964a2b51249e2850d60b07ff8f1bfba5d99cb8b13f4fb8d2e401",
                        "size": 203
                    },
                    {
                        "amount": 300000000,
                        "is_segwit": True,
                        "outpoint_hash": "677ff256cedf11c962ddd34d06ac26fc3a3c219896d55a56d5fcc215e198810b",
                        "outpoint_index": 1,
                        "signature": "304402202b5d36b86610dd54360a6eefe11fa60547d63cf62fb6168410e3e89480d7f93"
                                     "3022016d6da6e82c9d80e88526ff0013b97b80e26bf57274a4a807af03e386373eed701",
                        "size": 203
                    }
                ],
                "output": {
                    "address": "2N9nL6NHhT3Ac7NXgsn1qa4ywNDqRPHaowU",
                    "amount": 695680000,
                    "size": 23
                },
                "recipient_address": "2N9nL6NHhT3Ac7NXgsn1qa4ywNDqRPHaowU"
            },
            "total_size": 881,
            "current_absolute_fee_paid": 20000
        }
        self.assertEqual(
            transaction.to_json(),
            expected_transaction
        )
        transaction.make().seal()
        print(transaction.raw)
