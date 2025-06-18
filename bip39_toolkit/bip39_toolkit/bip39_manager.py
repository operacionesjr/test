import mnemonic

class BIP39Manager:
    def __init__(self, language="english"):
        self.mnemonic_generator = mnemonic.Mnemonic(language)

    def generate_mnemonic(self, strength=256):
        return self.mnemonic_generator.generate(strength=strength)

    def mnemonic_to_seed(self, mnemonic_phrase, passphrase=""):
        return self.mnemonic_generator.to_seed(mnemonic_phrase, passphrase=passphrase)

    def is_mnemonic_valid(self, mnemonic_phrase):
        return self.mnemonic_generator.check(mnemonic_phrase)
