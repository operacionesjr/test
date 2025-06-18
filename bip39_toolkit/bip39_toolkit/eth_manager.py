from eth_keys import keys
from eth_utils import to_checksum_address

class ETHManager:
    def __init__(self, private_key_bytes):
        self.private_key = keys.PrivateKey(private_key_bytes)

    def get_public_key(self):
        return self.private_key.public_key

    def get_address(self):
        return to_checksum_address(self.private_key.public_key.to_address())
