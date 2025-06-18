import argparse
import random
import csv
from .bip39_manager import BIP39Manager
from .bip32_manager import BIP32Manager
from .eth_manager import ETHManager

def main():
    parser = argparse.ArgumentParser(description="BIP39 Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate Mnemonic
    parser_generate = subparsers.add_parser("generate", help="Generate a new BIP39 mnemonic")
    parser_generate.add_argument("--strength", type=int, default=256, help="Strength of the mnemonic (e.g., 128, 256)")
    parser_generate.add_argument("--language", default="english", help="Language for the mnemonic")

    # Derive Seed
    parser_derive_seed = subparsers.add_parser("derive-seed", help="Derive seed from mnemonic")
    parser_derive_seed.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_derive_seed.add_argument("--passphrase", default="", help="Optional passphrase")

    # Derive ETH Address
    parser_derive_eth = subparsers.add_parser("derive-eth", help="Derive ETH address from mnemonic")
    parser_derive_eth.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_derive_eth.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_derive_eth.add_argument("--path", default="m/44'/60'/0'/0/0", help="BIP32 derivation path")

    # Sequential Search Command
    parser_search_seq = subparsers.add_parser("search-sequential", help="Sequentially search derivation paths for ETH addresses")
    parser_search_seq.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_search_seq.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_search_seq.add_argument("--account-start", type=int, default=0, help="Starting account number (hardened)")
    parser_search_seq.add_argument("--account-end", type=int, default=0, help="Ending account number (inclusive)")
    parser_search_seq.add_argument("--change-start", type=int, default=0, help="Starting change index (0 for external, 1 for internal)")
    parser_search_seq.add_argument("--change-end", type=int, default=0, help="Ending change index (inclusive)")
    parser_search_seq.add_argument("--index-start", type=int, default=0, help="Starting address index")
    parser_search_seq.add_argument("--index-end", type=int, default=20, help="Ending address index (inclusive)")
    parser_search_seq.add_argument("--output-file", type=str, default=None, help="Optional file path to save results in CSV format.")

    # Random Search Command
    parser_search_rand = subparsers.add_parser("search-random", help="Randomly search derivation paths for ETH addresses")
    parser_search_rand.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_search_rand.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_search_rand.add_argument("--account-min", type=int, default=0, help="Minimum account number (hardened)")
    parser_search_rand.add_argument("--account-max", type=int, default=0, help="Maximum account number (inclusive)")
    parser_search_rand.add_argument("--change-min", type=int, default=0, help="Minimum change index (0 for external, 1 for internal)")
    parser_search_rand.add_argument("--change-max", type=int, default=0, help="Maximum change index (inclusive)")
    parser_search_rand.add_argument("--index-min", type=int, default=0, help="Minimum address index")
    parser_search_rand.add_argument("--index-max", type=int, default=1000, help="Maximum address index (inclusive)")
    parser_search_rand.add_argument("--iterations", type=int, default=100, help="Number of random paths to generate")
    parser_search_rand.add_argument("--output-file", type=str, default=None, help="Optional file path to save results in CSV format.")

    # Random Mnemonic Search Command
    parser_search_mnemonics = subparsers.add_parser("search-mnemonics", help="Generate multiple random mnemonics and derive ETH address for a fixed path")
    parser_search_mnemonics.add_argument("--count", type=int, default=10, help="Number of random mnemonics to generate")
    parser_search_mnemonics.add_argument("--strength", type=int, default=128, choices=[128, 160, 192, 224, 256], help="Strength of the mnemonics (e.g., 128 for 12 words)")
    parser_search_mnemonics.add_argument("--language", default="english", help="Language for the mnemonics (default: english)")
    parser_search_mnemonics.add_argument("--passphrase", default="", help="Optional fixed passphrase for all mnemonics")
    parser_search_mnemonics.add_argument("--path", default="m/44'/60'/0'/0/0", help="Fixed BIP32 derivation path to use for each mnemonic")
    parser_search_mnemonics.add_argument("--output-file", type=str, default=None, help="Optional file path to save results in CSV format.")

    args = parser.parse_args()
    bip39_manager = BIP39Manager()

    if args.command == "generate":
        mnemonic = bip39_manager.generate_mnemonic(strength=args.strength, language=args.language)
        print(f"Generated Mnemonic: {mnemonic}")

    elif args.command == "derive-seed":
        seed = bip39_manager.mnemonic_to_seed(args.mnemonic, passphrase=args.passphrase)
        print(f"Derived Seed (hex): {seed.hex()}")

    elif args.command == "derive-eth":
        seed = bip39_manager.mnemonic_to_seed(args.mnemonic, passphrase=args.passphrase)
        bip32_manager = BIP32Manager(seed)
        derived_key = bip32_manager.derive_path(args.path)
        private_key_bytes = bip32_manager.get_private_key(derived_key)

        eth_manager = ETHManager(private_key_bytes)
        address = eth_manager.get_address()

        # Get the compressed public key from BIP32 derivation
        public_key_compressed_bytes = bip32_manager.get_public_key(derived_key)

        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"BIP39 Seed (hex): {seed.hex()}")

        try:
            print(f"BIP32 Root Key (xprv): {bip32_manager.master_key.ExtendedKey()}")
        except Exception as e:
            print(f"BIP32 Root Key (xprv): Could not retrieve (Error: {e})")

        print(f"Derivation Path: {args.path}")
        print(f"Derived Private Key (hex): {private_key_bytes.hex()}")

        # Display the compressed public key from BIP32 derivation
        print(f"Derived Public Key (BIP32 compressed, hex): {public_key_compressed_bytes.hex()}")

        # Display the uncompressed public key from eth_keys (used for ETH address)
        eth_public_key_object = eth_manager.get_public_key()
        print(f"Derived Public Key (ETH uncompressed, hex): {eth_public_key_object.to_bytes().hex()}")

        print(f"Derived ETH Address: {address}")

    elif args.command == "search-sequential":
        print(f"Initiating sequential search for ETH addresses...")
        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"Account Range: {args.account_start}-{args.account_end}")
        print(f"Change Range: {args.change_start}-{args.change_end}")
        print(f"Index Range: {args.index_start}-{args.index_end}")
        print("---")

        seed = bip39_manager.mnemonic_to_seed(args.mnemonic, passphrase=args.passphrase)
        bip32_manager = BIP32Manager(seed)

        # Fixed parts of the Ethereum derivation path
        purpose = 44
        coin_type = 60

        results_found = 0

        csv_writer = None
        output_file_handle = None
        header = ["Path", "ETH_Address", "Private_Key_Hex", "Public_Key_Uncompressed_Hex"]

        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(header)
                print(f"Saving results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}")
                csv_writer = None
                output_file_handle = None

        if not csv_writer:
            print(",".join(header))

        for account_val in range(args.account_start, args.account_end + 1):
            for change_val in range(args.change_start, args.change_end + 1):
                for index_val in range(args.index_start, args.index_end + 1):
                    path = f"m/{purpose}'/{coin_type}'/{account_val}'/{change_val}/{index_val}"
                    try:
                        derived_key_object = bip32_manager.derive_path(path)
                        private_key_bytes = bip32_manager.get_private_key(derived_key_object)
                        eth_manager = ETHManager(private_key_bytes)
                        address = eth_manager.get_address()
                        eth_public_key_object = eth_manager.get_public_key()
                        public_key_hex = eth_public_key_object.to_bytes().hex()

                        row_data = [path, address, private_key_bytes.hex(), public_key_hex]
                        if csv_writer:
                            csv_writer.writerow(row_data)
                        else:
                            print(",".join(row_data))
                        results_found += 1
                    except Exception as e:
                        message = f"Error deriving path {path}: {e}"
                        if csv_writer:
                             csv_writer.writerow([path, message, "", ""])
                        else:
                            print(message)

        if output_file_handle:
            output_file_handle.close()
            print(f"Results saved to {args.output_file}")

        print("---")
        print(f"Sequential search finished. Found {results_found} addresses.")

    elif args.command == "search-random":
        print(f"Initiating random search for ETH addresses...")
        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"Account Range: {args.account_min}-{args.account_max}")
        print(f"Change Range: {args.change_min}-{args.change_max}")
        print(f"Index Range: {args.index_min}-{args.index_max}")
        print(f"Number of Iterations: {args.iterations}")
        print("---")

        # Validate ranges
        if args.account_min > args.account_max:
            print("Error: Account min cannot be greater than account max.")
            return # Or exit
        if args.change_min > args.change_max:
            print("Error: Change min cannot be greater than change max.")
            return
        if args.index_min > args.index_max:
            print("Error: Index min cannot be greater than index max.")
            return

        seed = bip39_manager.mnemonic_to_seed(args.mnemonic, passphrase=args.passphrase)
        bip32_manager = BIP32Manager(seed)

        purpose = 44
        coin_type = 60

        results_found = 0

        csv_writer = None
        output_file_handle = None
        header = ["Path", "ETH_Address", "Private_Key_Hex", "Public_Key_Uncompressed_Hex"]

        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(header)
                print(f"Saving results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}")
                csv_writer = None
                output_file_handle = None

        if not csv_writer:
            print(",".join(header))

        for _ in range(args.iterations):
            account_val = random.randint(args.account_min, args.account_max)
            change_val = random.randint(args.change_min, args.change_max)
            index_val = random.randint(args.index_min, args.index_max)
            path = f"m/{purpose}'/{coin_type}'/{account_val}'/{change_val}/{index_val}"
            try:
                derived_key_object = bip32_manager.derive_path(path)
                private_key_bytes = bip32_manager.get_private_key(derived_key_object)
                eth_manager = ETHManager(private_key_bytes)
                address = eth_manager.get_address()
                eth_public_key_object = eth_manager.get_public_key()
                public_key_hex = eth_public_key_object.to_bytes().hex()

                row_data = [path, address, private_key_bytes.hex(), public_key_hex]
                if csv_writer:
                    csv_writer.writerow(row_data)
                else:
                    print(",".join(row_data))
                results_found += 1
            except Exception as e:
                message = f"Error deriving path {path}: {e}"
                if csv_writer:
                    csv_writer.writerow([path, message, "", ""])
                else:
                    print(message)

        if output_file_handle:
            output_file_handle.close()
            print(f"Results saved to {args.output_file}")

        print("---")
        print(f"Random search finished. Generated and checked {results_found} addresses out of {args.iterations} iterations.")

    elif args.command == "search-mnemonics":
        print(f"Initiating random mnemonic search...")
        print(f"Number of mnemonics to generate: {args.count}")
        print(f"Mnemonic strength: {args.strength} bits")
        print(f"Mnemonic language: {args.language}")
        if args.passphrase:
            print(f"Fixed Passphrase: {args.passphrase}")
        else:
            print("Fixed Passphrase: [none]")
        print(f"Fixed Derivation Path: {args.path}")
        print("---")

        csv_writer = None
        output_file_handle = None
        header = ["Mnemonic_Phrase", "Path", "ETH_Address", "Private_Key_Hex", "Public_Key_Uncompressed_Hex"]

        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(header)
                print(f"Saving results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}")
                csv_writer = None
                output_file_handle = None

        if not csv_writer:
            print(",".join(header))

        current_bip39_manager = BIP39Manager(language=args.language)
        generated_count = 0

        for _ in range(args.count):
            mnemonic_phrase = "" # Initialize for error logging
            try:
                mnemonic_phrase = current_bip39_manager.generate_mnemonic(strength=args.strength)
                if not current_bip39_manager.is_mnemonic_valid(mnemonic_phrase):
                    message = f"Generated an invalid mnemonic: {mnemonic_phrase} - skipping."
                    if csv_writer: csv_writer.writerow([mnemonic_phrase, args.path, message, "", ""]) # Path is fixed
                    else: print(message)
                    continue

                seed = current_bip39_manager.mnemonic_to_seed(mnemonic_phrase, passphrase=args.passphrase)
                bip32_manager_local = BIP32Manager(seed)
                derived_key_object = bip32_manager_local.derive_path(args.path)
                private_key_bytes = bip32_manager_local.get_private_key(derived_key_object)
                eth_manager = ETHManager(private_key_bytes)
                address = eth_manager.get_address()
                eth_public_key_object = eth_manager.get_public_key()
                public_key_hex = eth_public_key_object.to_bytes().hex()

                row_data = [mnemonic_phrase, args.path, address, private_key_bytes.hex(), public_key_hex]
                if csv_writer:
                    csv_writer.writerow(row_data)
                else:
                    print(f'"{mnemonic_phrase}",{args.path},{address},{private_key_bytes.hex()},{public_key_hex}')
                generated_count += 1
            except Exception as e:
                message = f"Error processing mnemonic '{mnemonic_phrase}': {e}"
                if csv_writer: csv_writer.writerow([mnemonic_phrase, args.path, message, "", ""])
                else: print(message)

        if output_file_handle:
            output_file_handle.close()
            print(f"Results saved to {args.output_file}")

        print("---")
        print(f"Random mnemonic search finished. Processed {generated_count} mnemonics.")

if __name__ == "__main__":
    main()
