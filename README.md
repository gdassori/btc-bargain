# btc-bargain
Bitcoin Multisig Onchain Exchange Library

---

In this example implementation we have an half custodian system, in which parties have a key, and the server another (as companies like Conio, BitGo, Green, does). 

At some point, parties want to exchange bitcoins between them, without going onchain for the settlement. Parties can trade multiple times between them, and the main settlement object is still kept by the server.

The scheme is the following:

- Alice, Bob and Carol are part of the same half-custodian infrastructure.
- Alice send Bitcoins to Bob, doing a SIGHASH_NONE|SIGHASH_AOP on its key, trusting the custodian system.
- The custodian system collect the signature and the amount Alice wants to send to Bob, and store this data.
- Bob is credited of the amount instantly, and can exchange to other parties.
- Bob send some bitcoins to Carol.
- The input Alice signed is splitted between Carol and Bob, Alice's signature is still valid.
- Bob doesn't need to pay a transaction fee for the operation, cause the input is already paid by Alice.
- An unlimited amount of transactions may occour before the settlement.
- An unlimited number of participants may join the same transaction.
- At the end of the day, the custodian system seal the transaction with a SIGHASH_ALL signature, and this is broadcast on the chain, and the amounts consolidated.

Features:

- It reduces transaction fees.
- It cut times for having a transaction spendable inside the system.
- It enables high-frequencies trading between multisig half-custodian parties.
- It may improve on-chain privacy, since the final transaction in this example will occour between Alice and Carol, potentially hiding Bob.

Notes:

- The entire system may be transparent for the users.
- If Bob want to send the transaction outside the custodian system, it must be broadcast, and this can be done using the Alice input.
- This could be also set as a coinjoin, working on the outputs factory class.

Drawbacks:

- Trust. Because Alice must potentially sign a big input with an insecure signature, and this means until the settlement the system can alter the recipients. But users are already into an half-custodian system, which is basically something trusted with additional security.
