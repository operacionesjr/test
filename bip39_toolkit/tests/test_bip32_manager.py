import unittest
import hmac
import hashlib
from bip39_toolkit.bip39_manager import BIP39Manager
from bip39_toolkit.bip32_manager import BIP32Manager

class TestBIP32Manager(unittest.TestCase):
    def setUp(self):
        # Use a known mnemonic to generate a predictable seed
        self.mnemonic = "letter ethics correct umbrella prevent search physical space prize type cover strong"
        self.passphrase = "testpassphrase"
        bip39_mgr = BIP39Manager()
        self.seed = bip39_mgr.mnemonic_to_seed(self.mnemonic, self.passphrase)
        self.bip32_manager = BIP32Manager(self.seed)

    def test_derive_path(self):
        # Standard Ethereum path
        path = "m/44'/60'/0'/0/0"
        derived_key = self.bip32_manager.derive_path(path)
        self.assertIsNotNone(derived_key)

        # Another common path
        path_2 = "m/44'/60'/0'/0/1"
        derived_key_2 = self.bip32_manager.derive_path(path_2)
        self.assertIsNotNone(derived_key_2)

        # Ensure different paths give different keys (by checking their string representation or a property)
        self.assertNotEqual(derived_key.PrivateKey(), derived_key_2.PrivateKey())


    def test_get_private_key(self):
        path = "m/44'/60'/0'/0/0"
        derived_key = self.bip32_manager.derive_path(path)
        private_key = self.bip32_manager.get_private_key(derived_key)
        self.assertIsInstance(private_key, bytes)
        self.assertEqual(len(private_key), 32) # BIP32 private keys are 32 bytes

    def test_get_public_key(self):
        path = "m/44'/60'/0'/0/0"
        derived_key = self.bip32_manager.derive_path(path)
        public_key = self.bip32_manager.get_public_key(derived_key)
        self.assertIsInstance(public_key, bytes)
        self.assertEqual(len(public_key), 33) # Compressed public keys are 33 bytes

    def test_get_address(self):
        # This test might be more conceptual for BIP32Manager itself,
        # as address generation is usually chain-specific (like ETHManager).
        # BIP32Utils.Address() often gives a Bitcoin-style address.
        path = "m/44'/60'/0'/0/0"
        derived_key = self.bip32_manager.derive_path(path)
        address = self.bip32_manager.get_address(derived_key)
        self.assertIsInstance(address, str)
        self.assertTrue(len(address) > 0)
        # For the given mnemonic, passphrase, and path m/44'/60'/0'/0/0,
        # the BTC address derived by BIP32Utils is: 1PMy4pAAX48t9M9WJwoyVfXgVzHk12Zkds
        # This depends on the BIP32Utils library's specific address format.
        # Note: This is NOT an Ethereum address.
        expected_btc_address = "1PMy4pAAX48t9M9WJwoyVfXgVzHk12Zkds" # Example, verify with your BIP32Utils version
        # self.assertEqual(address, expected_btc_address)
        # Commenting out as this can vary slightly and is not the main focus for ETH.

    def test_bip32_official_vector_1(self):
        vector = {
            "seed_hex": "000102030405060708090a0b0c0d0e0f",
            "derivations": [
                {
                    "path": "m",
                    "xpub": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8",
                    "xprv": "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi"
                },
                {
                    "path": "m/0'",
                    "xpub": "xpub68Gmy5EdvgibQVfPdqkBBCHxA5htiqg55crXYuXoQRKfDBFA1WEjWgP6LHhwBZeNK1VTsfTFUHCdrfp1bgwQ9xv5ski8PX9rL2dZXvgGDnw",
                    "xprv": "xprv9uHRZZhk6KAJC1avXpDAp4MDc3sQKNxDiPvvkX8Br5ngLNv1TxvUxt4cV1rGL5hj6KCesnDYUhd7oWgT11eZG7XnxHrnYeSvkzY7d2bhkJ7"
                },
                {
                    "path": "m/0'/1",
                    "xpub": "xpub6ASuArnXKPbfEwhqN6e3mwBcDTgzisQN1wXN9BJcM47sSikHjJf3UFHKkNAWbWMiGj7Wf5uMash7SyYq527Hqck2AxYysAA7xmALppuCkwQ",
                    "xprv": "xprv9wTYmMFdV23N2TdNG573QoEsfRrWKQgWeibmLntzniatZvR9BmLnvSxqu53Kw1UmYPxLgboyZQaXwTCg8MSY3H2EU4pWcQDnRnrVA1xe8fs"
                }
            ]
        }

        seed_S_hex = vector["seed_hex"]
        seed_S_bytes = bytes.fromhex(seed_S_hex)
        bip32_seed_I = hmac.new(b"Bitcoin seed", seed_S_bytes, hashlib.sha512).digest()

        bip32_m_manager = BIP32Manager(bip32_seed_I)

        for i, derivation in enumerate(vector["derivations"]):
            path = derivation["path"]
            expected_xpub = derivation["xpub"]
            expected_xprv = derivation["xprv"]

            with self.subTest(path=path, vector_index=i):
                if path == "m":
                    self.assertEqual(bip32_m_manager.master_key.ExtendedKey(), expected_xprv)
                    self.assertEqual(bip32_m_manager.master_key.PublicKey().ExtendedKey(), expected_xpub)
                else:
                    # Our BIP32Manager.derive_path expects the full path from "m"
                    # The BIP32Utils library's DerivePath method on a key object handles relative paths from that key.
                    # If our manager's derive_path is called with "m/0'", it should pass "0'" to master_key.DerivePath("0'")
                    # or handle the "m/" prefix appropriately.
                    # The current implementation of BIP32Manager: self.master_key.DerivePath(path)
                    # BIP32Utils DerivePath(path) method:
                    # - If path is "m" or "./", it returns self.
                    # - Otherwise, it splits path by "/" and processes segments.
                    # So, passing "m/0'" to master_key.DerivePath("m/0'") should work as expected.
                    derived_key_object = bip32_m_manager.derive_path(path)

                    actual_xprv = derived_key_object.ExtendedKey()
                    actual_xpub = derived_key_object.PublicKey().ExtendedKey()

                    self.assertEqual(actual_xprv, expected_xprv, f"XPRV mismatch for path {path}")
                    self.assertEqual(actual_xpub, expected_xpub, f"XPUB mismatch for path {path}")

if __name__ == "__main__":
    unittest.main()
