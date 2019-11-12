class BTCBargainException(BaseException):
    pass


class MissingClientSignature(BTCBargainException):
    pass


class InvalidClientSignature(BTCBargainException):
    pass


class InconsistentSignaturesAmount(BTCBargainException):
    pass
