import mnemonic
import unicodedata
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512

class BIP39Manager:
    def __init__(self, language="english"):
        self.mnemonic_generator = mnemonic.Mnemonic(language)

    def generate_mnemonic(self, strength=256):
        return self.mnemonic_generator.generate(strength=strength)

    def mnemonic_to_seed(self, mnemonic_phrase, passphrase=""):
        return self.mnemonic_generator.to_seed(mnemonic_phrase, passphrase=passphrase)

    def is_mnemonic_valid(self, mnemonic_phrase):
        return self.mnemonic_generator.check(mnemonic_phrase)

    def generate_seed_custom_pbkdf2(self, mnemonic_phrase, passphrase="", iterations=2048):
        """
        Generates a seed from a mnemonic phrase using PBKDF2 with a custom iteration count.
        Conforms to BIP39 for normalization and salt construction.
        Uses pycryptodome for PBKDF2 implementation.

        :param mnemonic_phrase: The mnemonic sentence.
        :param passphrase: The optional passphrase.
        :param iterations: The number of PBKDF2 iterations.
        :return: 64-byte seed.
        :raises ValueError: if iterations is not positive.
        """
        if not isinstance(iterations, int) or iterations <= 0:
            raise ValueError("PBKDF2 iterations count must be a positive integer.")

        # NFKD normalization and UTF-8 encoding for mnemonic
        normalized_mnemonic = unicodedata.normalize('NFKD', mnemonic_phrase)
        password_bytes = normalized_mnemonic.encode('utf-8')

        # NFKD normalization and UTF-8 encoding for passphrase for the salt
        normalized_passphrase = unicodedata.normalize('NFKD', passphrase)
        salt_passphrase_bytes = normalized_passphrase.encode('utf-8')

        salt = b"mnemonic" + salt_passphrase_bytes

        # dkLen is 64 bytes (512 bits) for BIP39 seeds
        dkLen = 64

        seed = PBKDF2(password_bytes, salt, dkLen=dkLen, count=iterations, hmac_hash_module=SHA512)
        return seed
