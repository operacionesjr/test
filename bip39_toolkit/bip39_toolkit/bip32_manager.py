import BIP32Utils

class BIP32Manager:
    def __init__(self, seed):
        self.master_key = BIP32Utils.BIP32Key.fromEntropy(seed)

    def derive_path(self, path):
        return self.master_key.DerivePath(path)

    def get_private_key(self, derived_key):
        return derived_key.PrivateKey()

    def get_public_key(self, derived_key):
        return derived_key.PublicKey()

    def get_address(self, derived_key):
        return derived_key.Address()
