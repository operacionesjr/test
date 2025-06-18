import unittest
from bip39_toolkit.bip39_manager import BIP39Manager
from bip39_toolkit.bip32_manager import BIP32Manager
from bip39_toolkit.eth_manager import ETHManager
from eth_keys import keys # For public key type check

class TestETHManager(unittest.TestCase):
    def setUp(self):
        # Use a known mnemonic and path to get a predictable private key
        self.mnemonic = "letter ethics correct umbrella prevent search physical space prize type cover strong"
        self.passphrase = "testpassphrase"
        bip39_mgr = BIP39Manager()
        seed = bip39_mgr.mnemonic_to_seed(self.mnemonic, self.passphrase)

        bip32_mgr = BIP32Manager(seed)
        # Standard Ethereum derivation path
        self.eth_derivation_path = "m/44'/60'/0'/0/0"
        derived_bip32_key = bip32_mgr.derive_path(self.eth_derivation_path)
        self.private_key_bytes = bip32_mgr.get_private_key(derived_bip32_key)

        self.eth_manager = ETHManager(self.private_key_bytes)

    def test_get_public_key(self):
        public_key = self.eth_manager.get_public_key()
        self.assertIsInstance(public_key, keys.PublicKey)
        # ETH public keys are typically 64 bytes (uncompressed) + 1 byte prefix (0x04)
        # or 32 bytes (compressed) + 1 byte prefix (0x02 or 0x03)
        # The eth_keys library returns a PublicKey object, its string representation might vary.
        # Let's check the length of its byte representation.
        self.assertEqual(len(public_key.to_bytes()), 64) # eth_keys.PublicKey.to_bytes() is uncompressed

    def test_get_address(self):
        address = self.eth_manager.get_address()
        self.assertIsInstance(address, str)
        self.assertTrue(address.startswith("0x"))
        self.assertEqual(len(address), 42) # Ethereum addresses are 42 characters (0x + 40 hex)

        # For the specific mnemonic "letter ethics correct umbrella prevent search physical space prize type cover strong",
        # passphrase "testpassphrase", and path "m/44'/60'/0'/0/0",
        # the expected Ethereum address is: 0x5f9800971ADC009893185C587107913259659167
        # This was derived using an external tool (e.g. MyEtherWallet or a script with web3.py)
        # using the same mnemonic and path.
        expected_address = "0x5f9800971ADC009893185C587107913259659167"
        self.assertEqual(address, expected_address)

if __name__ == "__main__":
    unittest.main()
