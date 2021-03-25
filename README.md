# btc-bargain

Bitcoin Multisig Onchain Exchange Library prototype

---

In this example implementation we have a `2-on-m` scheme, in which a client owns a key, and a server owns `m-1` keys. 
Multiple clients depends on the same server for the co-signing of their inputs. 
Let's call this custodian wallet provider "Multisig Wallet Provider Co.", MWPC from now.

Alice, Bob and Carol are users of the MWPC system, and want to exchange Bitcoins between them.

What happens, at this point, is the following:

- Alice received onchain unspents, and want to send Bitcoins to Bob. To do so Alice establish a connection with MWPC, with which she previously established a wallet. 
- MWPC, that keeps track of Alice's UTXO, asks her to sign with SIGHASHNONE|AOP a set of inputs able to cover the amount she wish to send (let's keep the fee out for now). No onchain transaction happens.
- MWPC collect the signature and the amount Alice wants to send to Bob, and store this data into a database for and undefined amount of time.
- Bob is instantly credited of the amount sent by Alice. There's still no onchain transaction or TXID, just an IOU from MWPC to Bob.
- Then, Bob want to send the whole amount he received, to Carol.
- At this point nothing happens. The input Alice previously signed will be assigned to Carol. The NONE|AOP signature is loosy enough to be still valid. Also, no transaction happens onchain, just MWPC keeps withdraw the IOU from Bob and establish a new one with Carol.
- An unlimited amount of transactions may occour before the settlement.
- An unlimited number of participants may join the same transaction (note: onchain protocol limits).
- At some point, MWPC "seal" the transaction with a SIGHASH_ALL signature, and this is broadcast on the chain. Both Carol and Alice would be credited of an unspent, having the same transaction id. Carol will be credited of part of the inputs initially signed by Alice and co-signed by MWPC, and Alice will receive her change, if any.

Features:

- This scheme dramatically reduces transaction fees for certain type of actors.
- It cut times for having a transaction spendable inside the "MWPC" domain (offchain instant txs).
- It enables high-frequencies trading between multisig half-custodian parties (Bisq-like exchange?).
- It may improve on-chain privacy, since the final transaction in this example will occour between Alice and Carol, hiding Bob. The same privacy level of LN from this point of view.

Notes:

- The entire system is transparent for the users.
- If at any point a user want to go outside the domain with the pending unspents, the destination could be put into the MWPC "sealed" transaction together with the other inputs, even cutting an hop.
- Could work as privacy improvement tool as well, with well tailored outputs.

Drawbacks:

- Trust. Because Alice must potentially sign a big input with an insecure signature, and this means until the settlement the system can alter the recipients. But users are already into an n-o-m scheme, so anyone inside this scheme would have already opted in it and could only benefit from this implementation.
