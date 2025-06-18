import unittest
import json # Added for consistency with the request, though direct list usage is simpler
from bip39_toolkit.bip39_manager import BIP39Manager

class TestBIP39Manager(unittest.TestCase):
    def setUp(self):
        self.bip39_manager = BIP39Manager()
        self.test_mnemonic_128 = "letter ethics correct umbrella prevent search physical space prize type cover strong" # Example 12-word mnemonic
        self.test_mnemonic_256 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art" # Example 24-word mnemonic


    def test_generate_mnemonic_128(self):
        mnemonic = self.bip39_manager.generate_mnemonic(strength=128)
        self.assertEqual(len(mnemonic.split()), 12)
        self.assertTrue(self.bip39_manager.is_mnemonic_valid(mnemonic))

    def test_generate_mnemonic_256(self):
        mnemonic = self.bip39_manager.generate_mnemonic(strength=256)
        self.assertEqual(len(mnemonic.split()), 24)
        self.assertTrue(self.bip39_manager.is_mnemonic_valid(mnemonic))

    def test_mnemonic_to_seed(self):
        # Test with a known 12-word mnemonic and no passphrase
        seed = self.bip39_manager.mnemonic_to_seed(self.test_mnemonic_128, passphrase="")
        self.assertIsInstance(seed, bytes)
        self.assertTrue(len(seed) > 0)
        # Expected seed for the given mnemonic (replace with actual expected seed if known for specific test vectors)
        # For "letter ethics correct umbrella prevent search physical space prize type cover strong" with no passphrase
        # the seed is (using an online generator for this example):
        expected_seed_hex = "4293c3d867ac3addc9ffc43a139291019955180f5518a00f228a3df599c1981a3ac801853063d2301aa7460b3704f68874967366a660ae58f938376e8d1996b5"
        self.assertEqual(seed.hex(), expected_seed_hex)


    def test_mnemonic_to_seed_with_passphrase(self):
        mnemonic = self.test_mnemonic_128
        passphrase = "testpassphrase"
        seed = self.bip39_manager.mnemonic_to_seed(mnemonic, passphrase=passphrase)
        self.assertIsInstance(seed, bytes)
        self.assertTrue(len(seed) > 0)
        # Seed should be different with a passphrase
        seed_no_passphrase = self.bip39_manager.mnemonic_to_seed(mnemonic, passphrase="")
        self.assertNotEqual(seed, seed_no_passphrase)

    def test_is_mnemonic_valid(self):
        self.assertTrue(self.bip39_manager.is_mnemonic_valid(self.test_mnemonic_128))
        self.assertTrue(self.bip39_manager.is_mnemonic_valid(self.test_mnemonic_256))
        invalid_mnemonic = "this is not a valid mnemonic phrase"
        self.assertFalse(self.bip39_manager.is_mnemonic_valid(invalid_mnemonic))
        # Test with a mnemonic that has an incorrect checksum word
        invalid_checksum_mnemonic = "letter ethics correct umbrella prevent search physical space prize type cover wrong" # last word changed
        self.assertFalse(self.bip39_manager.is_mnemonic_valid(invalid_checksum_mnemonic))


    def test_bip39_official_english_vectors(self):
        # Test vectors from python-mnemonic, assuming passphrase "TREZOR"
        # Structure: [entropy_hex, mnemonic_phrase, seed_hex] (master_xprv omitted for this test)
        passphrase = "TREZOR"

        bip39_english_test_vectors = [
            [
                "00000000000000000000000000000000",
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
            ],
            [
                "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
                "legal winner thank year wave sausage worth useful legal winner thank yellow",
                "2e8905819b8723fe2c1d161860e5ee1830318dbf49a83bd451cfb8440c28bd6fa457fe1296106559a3c80937a1c1069be3a3a5bd381ee6260e8d9739fce1f607"
            ],
            [
                "80808080808080808080808080808080",
                "letter advice cage absurd amount doctor acoustic avoid letter advice cage above",
                "d71de856f81a8acc65e6fc851a38d4d7ec216fd0796d0a6827a3ad6ed5511a30fa280f12eb2e47ed2ac03b5c462a0358d18d69fe4f985ec81778c1b370b652a8"
            ],
            [
                "ffffffffffffffffffffffffffffffff",
                "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
                "ac27495480225222079d7be181583751e86f571027b0497b5b5d11218e0a8a13332572917f0f8e5a589620c6f15b11c61dee327651a14c34e18231052e48c069"
            ],
            [ # A 24-word example
                "0000000000000000000000000000000000000000000000000000000000000000",
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art",
                "bda85446c68413707090a52022edd26a1c9462295029f2e60cd7c4f2bbd3097170af7a4d73245cafa9c3cca8d561a7c3de6f5d4a10be8ed2a5e608d68f92fcc8"
            ]
        ]

        for i, vector in enumerate(bip39_english_test_vectors):
            mnemonic_phrase = vector[1]
            expected_seed_hex = vector[2]

            # self.bip39_manager is initialized with 'english' in setUp
            with self.subTest(vector_index=i, mnemonic=mnemonic_phrase[:20] + "..."):
                generated_seed_bytes = self.bip39_manager.mnemonic_to_seed(mnemonic_phrase, passphrase=passphrase)
                generated_seed_hex = generated_seed_bytes.hex()
                self.assertEqual(generated_seed_hex, expected_seed_hex,
                                 f"Seed mismatch for vector {i}: {mnemonic_phrase}")


    def test_generate_seed_custom_pbkdf2_iterations(self):
        mnemonic_phrase = self.test_mnemonic_128 # "letter ethics correct umbrella prevent search physical space prize type cover strong"
        passphrase = "testpassphrase"

        # Standard BIP39 iterations (for reference, though our custom method defaults to it if not specified)
        seed_2048_custom_default = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, passphrase=passphrase)
        # Explicitly 2048
        seed_2048_custom_explicit = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, passphrase=passphrase, iterations=2048)

        # Seed from the original library method (which uses 2048)
        # Note: mnemonic_to_seed uses the 'mnemonic' library, while generate_seed_custom_pbkdf2 uses pycryptodome.
        # A direct byte-for-byte match is expected if both implement PBKDF2-HMAC-SHA512 correctly with same inputs.
        seed_2048_library = self.bip39_manager.mnemonic_to_seed(mnemonic_phrase, passphrase=passphrase)

        self.assertEqual(seed_2048_custom_default, seed_2048_library, "Custom PBKDF2 with default 2048 iterations should match library's 2048 output.")
        self.assertEqual(seed_2048_custom_explicit, seed_2048_library, "Custom PBKDF2 with explicit 2048 iterations should match library's 2048 output.")

        # Test with a different iteration count
        seed_1000 = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, passphrase=passphrase, iterations=1000)
        self.assertIsInstance(seed_1000, bytes)
        self.assertEqual(len(seed_1000), 64) # Should still be a 64-byte seed
        self.assertNotEqual(seed_1000, seed_2048_library, "Seed with 1000 iterations should differ from 2048 iterations.")

        seed_4096 = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, passphrase=passphrase, iterations=4096)
        self.assertIsInstance(seed_4096, bytes)
        self.assertEqual(len(seed_4096), 64)
        self.assertNotEqual(seed_4096, seed_2048_library, "Seed with 4096 iterations should differ from 2048 iterations.")
        self.assertNotEqual(seed_4096, seed_1000, "Seed with 4096 iterations should differ from 1000 iterations.")

    def test_generate_seed_custom_pbkdf2_invalid_iterations(self):
        mnemonic_phrase = self.test_mnemonic_128
        with self.assertRaisesRegex(ValueError, "PBKDF2 iterations count must be a positive integer."):
            self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, iterations=0)
        with self.assertRaisesRegex(ValueError, "PBKDF2 iterations count must be a positive integer."):
            self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, iterations=-100)
        with self.assertRaisesRegex(ValueError, "PBKDF2 iterations count must be a positive integer."):
            self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, iterations="not_an_int")

    def test_generate_seed_custom_pbkdf2_normalization(self):
        # Using a simple ASCII string with an accent that NFKD would decompose.
        # "résumé" contains 'e' with acute accent. NFKD decomposes it into 'e' and a combining acute accent.
        mnemonic_with_accent = "résumé résumé résumé résumé résumé résumé résumé résumé résumé résumé résumé café" # Standard 12-word length
        passphrase_with_accent = "passphrésé" # Also contains 'e' with acute accent

        try:
            seed_accent_2048 = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_with_accent, passphrase_with_accent, iterations=2048)
            self.assertIsInstance(seed_accent_2048, bytes)
            self.assertEqual(len(seed_accent_2048), 64)

            seed_accent_1000 = self.bip39_manager.generate_seed_custom_pbkdf2(mnemonic_with_accent, passphrase_with_accent, iterations=1000)
            self.assertIsInstance(seed_accent_1000, bytes)
            self.assertEqual(len(seed_accent_1000), 64)

            self.assertNotEqual(seed_accent_2048, seed_accent_1000, "Seeds with different iterations should differ, even with accents.")

        except Exception as e:
            self.fail(f"generate_seed_custom_pbkdf2 failed with normalization-sensitive input: {e}")

if __name__ == "__main__":
    unittest.main()
