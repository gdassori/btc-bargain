class BargainOutput:
    def __init__(
        self,
        address: str,
        amount: int,
        size: int
    ):
        self.address = address
        self.amount = amount
        self._size = size

    @property
    def size(self):
        return int(self._size)

    def to_json(self):
        return {
            'address': self.address,
            'amount': self.amount,
            'size': self.size
        }
