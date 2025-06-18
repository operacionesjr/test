import unittest
from bip39_toolkit.bip39_toolkit.bitcoin_manager import BitcoinManager

# These are example key/address pairs. For robust testing, these should be
# derived from known private keys using BIP32 and then validated against
# other reputable Bitcoin libraries or block explorers.
# For the purpose of this subtask, we assume these are correct test vectors.

# Mainnet Examples
KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1 = "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798" # Example from bitcoinutils docs often used
EXPECTED_P2PKH_MAINNET_1 = "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"
EXPECTED_P2SH_P2WPKH_MAINNET_1 = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
EXPECTED_P2WPKH_MAINNET_1 = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"

KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_2 = "03a34b99f22c790c4e36b2b3c2c35a36db06226e41c692fc82b8b56ac1c540c5bd" # Another example
EXPECTED_P2PKH_MAINNET_2 = "1N2fW3XRn7hWc6Nz45K2pP8tZgY5yAS72H"
EXPECTED_P2SH_P2WPKH_MAINNET_2 = "3LpLGkDbMYB5R43QNoQgc71sQk9b62zU7G"
EXPECTED_P2WPKH_MAINNET_2 = "bc1q5shns2dgm2esd006pswt97m2g9g68u242ahf99"


# Testnet Examples (using different keys for variety, and ensuring testnet prefix)
# A common testnet compressed public key (derived from a known testnet private key)
KNOWN_COMPRESSED_PUBLIC_KEY_HEX_TESTNET_1 = "030b760297798046909774f42639108927806245283ac3153cf011c604a433609f"
EXPECTED_P2PKH_TESTNET_1 = "mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn"
EXPECTED_P2SH_P2WPKH_TESTNET_1 = "2MzQwSSnBHWHqSAqtTVQ6v47XtaisrJa1Vc"
EXPECTED_P2WPKH_TESTNET_1 = "tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7"


class TestBitcoinManager(unittest.TestCase):

    def test_generate_p2pkh_mainnet(self):
        manager = BitcoinManager(network='mainnet')
        address1 = manager.get_p2pkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1)
        self.assertEqual(address1, EXPECTED_P2PKH_MAINNET_1)
        address2 = manager.get_p2pkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_2)
        self.assertEqual(address2, EXPECTED_P2PKH_MAINNET_2)

    def test_generate_p2sh_p2wpkh_mainnet(self):
        manager = BitcoinManager(network='mainnet')
        address1 = manager.get_p2sh_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1)
        self.assertEqual(address1, EXPECTED_P2SH_P2WPKH_MAINNET_1)
        address2 = manager.get_p2sh_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_2)
        self.assertEqual(address2, EXPECTED_P2SH_P2WPKH_MAINNET_2)

    def test_generate_p2wpkh_mainnet(self):
        manager = BitcoinManager(network='mainnet')
        address1 = manager.get_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1)
        self.assertEqual(address1, EXPECTED_P2WPKH_MAINNET_1)
        address2 = manager.get_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_2)
        self.assertEqual(address2, EXPECTED_P2WPKH_MAINNET_2)

    def test_get_all_address_types_mainnet(self):
        manager = BitcoinManager(network='mainnet')
        all_addresses = manager.get_all_address_types(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1)
        self.assertEqual(all_addresses['p2pkh'], EXPECTED_P2PKH_MAINNET_1)
        self.assertEqual(all_addresses['p2sh_p2wpkh'], EXPECTED_P2SH_P2WPKH_MAINNET_1)
        self.assertEqual(all_addresses['p2wpkh'], EXPECTED_P2WPKH_MAINNET_1)

    def test_generate_p2pkh_testnet(self):
        manager = BitcoinManager(network='testnet')
        address = manager.get_p2pkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_TESTNET_1)
        self.assertEqual(address, EXPECTED_P2PKH_TESTNET_1)

    def test_generate_p2sh_p2wpkh_testnet(self):
        manager = BitcoinManager(network='testnet')
        address = manager.get_p2sh_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_TESTNET_1)
        self.assertEqual(address, EXPECTED_P2SH_P2WPKH_TESTNET_1)

    def test_generate_p2wpkh_testnet(self):
        manager = BitcoinManager(network='testnet')
        address = manager.get_p2wpkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_TESTNET_1)
        self.assertEqual(address, EXPECTED_P2WPKH_TESTNET_1)

    def test_get_all_address_types_testnet(self):
        manager = BitcoinManager(network='testnet')
        all_addresses = manager.get_all_address_types(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_TESTNET_1)
        self.assertEqual(all_addresses['p2pkh'], EXPECTED_P2PKH_TESTNET_1)
        self.assertEqual(all_addresses['p2sh_p2wpkh'], EXPECTED_P2SH_P2WPKH_TESTNET_1)
        self.assertEqual(all_addresses['p2wpkh'], EXPECTED_P2WPKH_TESTNET_1)

    def test_invalid_public_key_format(self):
        manager = BitcoinManager(network='mainnet')
        with self.assertRaises(ValueError):
            manager.get_p2pkh_address("0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f8179") # Too short
        with self.assertRaises(ValueError):
            manager.get_p2pkh_address(KNOWN_COMPRESSED_PUBLIC_KEY_HEX_MAINNET_1 + "00") # Too long
        with self.assertRaises(ValueError):
            manager.get_p2pkh_address("not_a_hex_string")

if __name__ == "__main__":
    unittest.main()
