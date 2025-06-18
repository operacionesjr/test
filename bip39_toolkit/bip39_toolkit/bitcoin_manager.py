from bitcoinutils.setup import setup
from bitcoinutils.keys import PublicKey # P2pkhAddress, P2shAddress, P2wpkhAddress are implicitly handled by PublicKey methods or script conversions
from bitcoinutils.script import Script # May not be directly needed if PublicKey methods suffice
from bitcoinutils.addresses import P2shAddress # Specifically needed for P2SH from script

class BitcoinManager:
    def __init__(self, network='mainnet'):
        """
        Initializes the BitcoinManager.
        :param network: 'mainnet' or 'testnet'.
        """
        # Setup the network (mainnet or testnet) for bitcoinutils
        # This needs to be called before any address or key operations.
        setup(network)
        self.network = network # Store for potential future use, though setup() is global

    def get_p2pkh_address(self, public_key_hex_compressed):
        """
        Generates a P2PKH (Pay-to-Public-Key-Hash) address (legacy, e.g., 1...).
        :param public_key_hex_compressed: Compressed public key in hex format (33 bytes).
        :return: P2PKH address string.
        """
        if not public_key_hex_compressed or len(public_key_hex_compressed) != 66: # 33 bytes * 2 hex chars
            raise ValueError("Invalid compressed public key hex format for P2PKH.")

        pub_key = PublicKey(public_key_hex_compressed)
        # get_address() defaults to P2PKH for a PublicKey object.
        # Using compressed=True is implicit if the PublicKey was created from compressed hex.
        return pub_key.get_address().to_string()

    def get_p2sh_p2wpkh_address(self, public_key_hex_compressed):
        """
        Generates a P2SH-P2WPKH (Pay-to-Witness-Public-Key-Hash wrapped in P2SH) address (e.g., 3...).
        This is a common type of SegWit address that is backwards compatible.
        :param public_key_hex_compressed: Compressed public key in hex format.
        :return: P2SH-P2WPKH address string.
        """
        if not public_key_hex_compressed or len(public_key_hex_compressed) != 66:
            raise ValueError("Invalid compressed public key hex format for P2SH-P2WPKH.")

        pub_key = PublicKey(public_key_hex_compressed)

        # Get the P2WPKH address (SegWit native) object first
        p2wpkh_address_obj = pub_key.get_segwit_address()

        # Get the scriptPubKey for this P2WPKH address
        redeem_script = p2wpkh_address_obj.to_script_pub_key()

        # Create a P2SH address from this redeem script
        return P2shAddress.from_script(redeem_script).to_string()

    def get_p2wpkh_address(self, public_key_hex_compressed):
        """
        Generates a P2WPKH (Pay-to-Witness-Public-Key-Hash) native SegWit address (Bech32, e.g., bc1q...).
        :param public_key_hex_compressed: Compressed public key in hex format.
        :return: P2WPKH (Bech32) address string.
        """
        if not public_key_hex_compressed or len(public_key_hex_compressed) != 66:
            raise ValueError("Invalid compressed public key hex format for P2WPKH.")

        pub_key = PublicKey(public_key_hex_compressed)
        # get_segwit_address() on a PublicKey object returns the P2WPKH address object.
        return pub_key.get_segwit_address().to_string()

    def get_all_address_types(self, public_key_hex_compressed):
        """
        Generates all three common address types for a given public key.
        :param public_key_hex_compressed: Compressed public key in hex format.
        :return: Dictionary with keys 'p2pkh', 'p2sh_p2wpkh', 'p2wpkh' and their address strings.
        """
        return {
            'p2pkh': self.get_p2pkh_address(public_key_hex_compressed),
            'p2sh_p2wpkh': self.get_p2sh_p2wpkh_address(public_key_hex_compressed),
            'p2wpkh': self.get_p2wpkh_address(public_key_hex_compressed),
        }
