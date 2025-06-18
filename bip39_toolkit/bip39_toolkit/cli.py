import argparse
import random
import csv
from .bip39_manager import BIP39Manager
from .bip32_manager import BIP32Manager
from .eth_manager import ETHManager
from .bitcoin_manager import BitcoinManager

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

    # Derive Address (ETH or BTC)
    parser_derive_address = subparsers.add_parser("derive-address", help="Derive address (ETH or BTC) from mnemonic")
    parser_derive_address.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_derive_address.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_derive_address.add_argument("--path", default="m/44'/60'/0'/0/0", help="BIP32 derivation path (default is ETH standard)")
    parser_derive_address.add_argument("--coin", type=str, default="ETH", choices=["ETH", "BTC"], help="Specify cryptocurrency (ETH or BTC, default: ETH)")
    parser_derive_address.add_argument("--pbkdf2-rounds", type=int, default=2048, help="Number of PBKDF2 iterations for seed generation. WARNING: Using non-standard PBKDF2 iterations will result in seeds incompatible with most standard wallets. (Default: 2048)")

    # Sequential Search Command
    parser_search_seq = subparsers.add_parser("search-sequential", help="Sequentially search derivation paths for ETH or BTC addresses")
    parser_search_seq.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_search_seq.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_search_seq.add_argument("--coin", type=str, default="ETH", choices=["ETH", "BTC"], help="Specify cryptocurrency (ETH or BTC, default: ETH)")
    parser_search_seq.add_argument("--account-start", type=int, default=0, help="Starting account number (hardened)")
    parser_search_seq.add_argument("--account-end", type=int, default=0, help="Ending account number (inclusive)")
    parser_search_seq.add_argument("--change-start", type=int, default=0, help="Starting change index (0 for external, 1 for internal)")
    parser_search_seq.add_argument("--change-end", type=int, default=0, help="Ending change index (inclusive)")
    parser_search_seq.add_argument("--index-start", type=int, default=0, help="Starting address index")
    parser_search_seq.add_argument("--index-end", type=int, default=20, help="Ending address index (inclusive)")
    parser_search_seq.add_argument("--output-file", type=str, default=None, help="Optional file path to save all results in CSV format.")
    parser_search_seq.add_argument("--target-file", type=str, default=None, help="Path to a text file containing target addresses (one per line) to search for.")
    parser_search_seq.add_argument("--matches-file", type=str, default=None, help="Optional file path to save only found matches in CSV format.")
    parser_search_seq.add_argument("--pbkdf2-rounds-start", type=int, default=2048, help="Start of PBKDF2 iteration range for seed generation. WARNING: Using non-standard PBKDF2 iterations will result in seeds incompatible with most standard wallets. (Default: 2048)")
    parser_search_seq.add_argument("--pbkdf2-rounds-end", type=int, default=2048, help="End of PBKDF2 iteration range (inclusive). WARNING: Using non-standard PBKDF2 iterations will result in seeds incompatible with most standard wallets. (Default: 2048)")

    # Random Search Command
    parser_search_rand = subparsers.add_parser("search-random", help="Randomly search derivation paths for ETH or BTC addresses")
    parser_search_rand.add_argument("mnemonic", help="BIP39 mnemonic phrase")
    parser_search_rand.add_argument("--passphrase", default="", help="Optional passphrase")
    parser_search_rand.add_argument("--coin", type=str, default="ETH", choices=["ETH", "BTC"], help="Specify cryptocurrency (ETH or BTC, default: ETH)")
    parser_search_rand.add_argument("--account-min", type=int, default=0, help="Minimum account number (hardened)")
    parser_search_rand.add_argument("--account-max", type=int, default=0, help="Maximum account number (inclusive)")
    parser_search_rand.add_argument("--change-min", type=int, default=0, help="Minimum change index (0 for external, 1 for internal)")
    parser_search_rand.add_argument("--change-max", type=int, default=0, help="Maximum change index (inclusive)")
    parser_search_rand.add_argument("--index-min", type=int, default=0, help="Minimum address index")
    parser_search_rand.add_argument("--index-max", type=int, default=1000, help="Maximum address index (inclusive)")
    parser_search_rand.add_argument("--iterations", type=int, default=100, help="Number of random paths to generate")
    parser_search_rand.add_argument("--output-file", type=str, default=None, help="Optional file path to save all results in CSV format.")
    parser_search_rand.add_argument("--target-file", type=str, default=None, help="Path to a text file containing target addresses (one per line) to search for.")
    parser_search_rand.add_argument("--matches-file", type=str, default=None, help="Optional file path to save only found matches in CSV format.")
    parser_search_rand.add_argument("--pbkdf2-rounds", type=int, default=2048, help="Number of PBKDF2 iterations for seed generation. WARNING: Using non-standard PBKDF2 iterations will result in seeds incompatible with most standard wallets. (Default: 2048)")

    # Random Mnemonic Search Command
    parser_search_mnemonics = subparsers.add_parser("search-mnemonics", help="Generate multiple random mnemonics and derive address (ETH or BTC) for a fixed path")
    parser_search_mnemonics.add_argument("--count", type=int, default=10, help="Number of random mnemonics to generate")
    parser_search_mnemonics.add_argument("--strength", type=int, default=128, choices=[128, 160, 192, 224, 256], help="Strength of the mnemonics (e.g., 128 for 12 words)")
    parser_search_mnemonics.add_argument("--language", default="english", help="Language for the mnemonics (default: english)")
    parser_search_mnemonics.add_argument("--passphrase", default="", help="Optional fixed passphrase for all mnemonics")
    parser_search_mnemonics.add_argument("--coin", type=str, default="ETH", choices=["ETH", "BTC"], help="Specify cryptocurrency (ETH or BTC, default: ETH)")
    parser_search_mnemonics.add_argument("--path", default="m/44'/60'/0'/0/0", help="Fixed BIP32 derivation path to use (default ETH path, auto-adjusts for BTC if still default)")
    parser_search_mnemonics.add_argument("--output-file", type=str, default=None, help="Optional file path to save results in CSV format.")
    parser_search_mnemonics.add_argument("--pbkdf2-rounds", type=int, default=2048, help="Number of PBKDF2 iterations for seed generation. WARNING: Using non-standard PBKDF2 iterations will result in seeds incompatible with most standard wallets. (Default: 2048)")

    args = parser.parse_args()
    bip39_manager = BIP39Manager()

    if args.command == "generate":
        mnemonic = bip39_manager.generate_mnemonic(strength=args.strength, language=args.language)
        print(f"Generated Mnemonic: {mnemonic}")

    elif args.command == "derive-seed":
        # Note: derive-seed command does not currently have --pbkdf2-rounds.
        # It could be added, or users wanting custom rounds for seed viewing should use derive-address and check seed.
        seed = bip39_manager.mnemonic_to_seed(args.mnemonic, passphrase=args.passphrase)
        print(f"Derived Seed (hex): {seed.hex()}")

    elif args.command == "derive-address":
        print(f"--- Derivation Parameters ---")
        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"PBKDF2 Iterations: {args.pbkdf2_rounds}")
        print(f"Derivation Path: {args.path}")
        print(f"Coin: {args.coin}")

        try:
            seed = bip39_manager.generate_seed_custom_pbkdf2(args.mnemonic, passphrase=args.passphrase, iterations=args.pbkdf2_rounds)
        except ValueError as ve:
            print(f"Error during seed generation: {ve}")
            return

        bip32_manager = BIP32Manager(seed)
        derived_key = bip32_manager.derive_path(args.path)
        private_key_bytes = bip32_manager.get_private_key(derived_key)
        public_key_compressed_bytes = bip32_manager.get_public_key(derived_key)

        print(f"--- Common Information (derived from seed) ---")
        print(f"BIP39 Seed (hex): {seed.hex()}")
        try:
            # Note: master_key.ExtendedKey() is from the root of the BIP32 tree (from the seed)
            # It does not change per-path, but is determined by the seed.
            print(f"BIP32 Root Key (xprv): {bip32_manager.master_key.ExtendedKey()}")
        except Exception as e:
            print(f"BIP32 Root Key (xprv): Could not retrieve (Error: {e})") # Should be rare if seed is valid

        # This private key is specific to the derived_key object for the given path
        print(f"Derived Private Key (hex): {private_key_bytes.hex()}")
        print(f"Derived Public Key (BIP32 compressed, hex): {public_key_compressed_bytes.hex()}")

        if args.coin == "ETH":
            print(f"--- Ethereum Specific ---")
            eth_manager = ETHManager(private_key_bytes)
            eth_public_key_object = eth_manager.get_public_key() # This is an eth_keys.PublicKey object
            print(f"Derived Public Key (ETH uncompressed, hex): {eth_public_key_object.to_bytes().hex()}")
            eth_address = eth_manager.get_address()
            print(f"Derived ETH Address: {eth_address}")

        elif args.coin == "BTC":
            print(f"--- Bitcoin Specific ---")
            # BitcoinManager's methods expect compressed public key hex string
            public_key_compressed_hex = public_key_compressed_bytes.hex()

            # For Bitcoin, decide on mainnet or testnet based on derivation path or a new arg if needed.
            # For now, assuming mainnet for derive-address.
            # Path conventions: m/44'/0'/... for BTC mainnet legacy/segwit-P2SH
            # m/84'/0'/... for BTC mainnet native segwit (P2WPKH)
            # m/44'/1'/... for BTC testnet
            # We'll use a simple heuristic for now, or default to mainnet.
            # A more robust solution might involve parsing args.path or a dedicated --network arg.
            network_type = 'mainnet'
            if args.path.startswith("m/44'/1'") or args.path.startswith("m/84'/1'"): # Basic check for testnet paths
                network_type = 'testnet'
                print(f"INFO: Detected potential Bitcoin testnet path, using network='testnet'.")

            bitcoin_manager = BitcoinManager(network=network_type)
            try:
                btc_addresses = bitcoin_manager.get_all_address_types(public_key_compressed_hex)
                print(f"Derived BTC Addresses ({network_type}):")
                print(f"  P2PKH (Legacy): {btc_addresses['p2pkh']}")
                print(f"  P2SH-P2WPKH (SegWit-in-P2SH): {btc_addresses['p2sh_p2wpkh']}")
                print(f"  P2WPKH (Native SegWit/Bech32): {btc_addresses['p2wpkh']}")
            except ValueError as e:
                print(f"Error generating Bitcoin addresses: {e}")
            except Exception as e: # Catch other bitcoinutils errors
                print(f"An unexpected error occurred with Bitcoin address generation: {e}")


    elif args.command == "search-sequential":
        print(f"Initiating sequential search for {args.coin} addresses...")
        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"Coin Type: {args.coin}")
        print(f"Account Range: {args.account_start}-{args.account_end}")
        print(f"Change Range: {args.change_start}-{args.change_end}")
        print(f"Index Range: {args.index_start}-{args.index_end}")
        print(f"PBKDF2 Rounds Range: {args.pbkdf2_rounds_start}-{args.pbkdf2_rounds_end}")
        print("---")

        # Outer loop for PBKDF2 iterations
        for current_pbkdf2_iteration in range(args.pbkdf2_rounds_start, args.pbkdf2_rounds_end + 1):
            try:
                print(f"INFO: Processing with PBKDF2 Iterations: {current_pbkdf2_iteration}")
                seed = bip39_manager.generate_seed_custom_pbkdf2(args.mnemonic, passphrase=args.passphrase, iterations=current_pbkdf2_iteration)
            except ValueError as ve:
                print(f"Error during seed generation for {current_pbkdf2_iteration} rounds: {ve}. Skipping this iteration count.")
                continue # Skip to next iteration count

            bip32_manager = BIP32Manager(seed) # Re-initialize with the new seed

            if args.coin == "ETH":
            purpose = 44
            coin_type = 60
            address_header_name = "ETH_Address"
            # For ETH, we typically display uncompressed public key
            public_key_header_name = "Public_Key_Uncompressed_Hex"
            bitcoin_manager = None # Not needed for ETH
        elif args.coin == "BTC":
            purpose = 84 # For P2WPKH (Native SegWit)
            coin_type = 0  # Bitcoin mainnet
            address_header_name = "BTC_Address_P2WPKH"
            # For BTC, we typically display compressed public key
            public_key_header_name = "Public_Key_Compressed_Hex"
            # Determine network for BitcoinManager (mainnet/testnet)
            # This is a simplified heuristic based on standard BTC paths.
            # A more robust solution might be a separate --network arg for search.
            # For search, we assume mainnet if coin_type is 0, testnet if 1.
            # Path structure: m / purpose' / coin_type' / account' / change / index
            # If coin_type in path is 1, it's testnet. For this search, we are setting coin_type.
            # So, we'll rely on a simple check or add a --network flag later if needed.
            # For now, let's assume mainnet for BTC search if not specified.
            # If the account values imply a testnet path later, that's a different concern.
            # The purpose/coin_type here are for path construction.
            # BitcoinManager is instantiated per-network.
            bitcoin_manager = BitcoinManager(network='mainnet') # Default to mainnet for search for now
            # TODO: Add a --network option for search commands for BTC (or infer from coin_type if it's 1 for testnet)
        else:
            print(f"Error: Unsupported coin type {args.coin}") # Should not happen
            return # Exit this command if coin is unsupported.

        # Target address loading and matches file setup (remains outside the PBKDF2 loop)
        target_addresses = set()
        if args.target_file:
            try:
                with open(args.target_file, "r") as f_targets:
                    for line in f_targets:
                        addr = line.strip()
                        if addr:
                            if args.coin == "ETH":
                                target_addresses.add(addr.lower())
                            else: # BTC addresses are case-sensitive in some contexts, store as is.
                                target_addresses.add(addr)
                print(f"INFO: Loaded {len(target_addresses)} target addresses from {args.target_file}")
            except IOError as e:
                print(f"Error reading target file {args.target_file}: {e}. Proceeding without target matching.")
                target_addresses.clear() # Ensure it's empty if file reading failed

        matches_writer = None
        matches_file_handle = None
        # Matches header updated to include PBKDF2_Rounds
        matches_header = ["PBKDF2_Rounds", "Path", "Derived_Address", "Matched_Target_Address", "Private_Key_Hex", "Public_Key_Hex"]
        if args.matches_file:
            try:
                matches_file_handle = open(args.matches_file, "w", newline="")
                matches_writer = csv.writer(matches_file_handle)
                matches_writer.writerow(matches_header)
                print(f"Saving found matches to {args.matches_file}...")
            except IOError as e:
                print(f"Error: Could not open matches file {args.matches_file} for writing: {e}")
                matches_writer = None
                matches_file_handle = None # Ensure it's None

        results_found = 0
        csv_writer = None
        output_file_handle = None
        # Dynamic header based on coin type for the main output file, now includes PBKDF2_Rounds
        main_output_header = ["PBKDF2_Rounds", "Path", address_header_name, "Private_Key_Hex", public_key_header_name]

        # Setup CSV writer for main output file if specified (once, before all loops)
        csv_writer = None
        output_file_handle = None
        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(main_output_header)
                print(f"Saving all results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}. Results will be printed to stdout.")
                csv_writer = None
                output_file_handle = None

        if not csv_writer: # If no output file or error opening, print header to stdout
            print(",".join(main_output_header))

        # The actual derivation loops (account, change, index) are now inside the PBKDF2 iteration loop
            for account_val in range(args.account_start, args.account_end + 1):
                for change_val in range(args.change_start, args.change_end + 1):
                    for index_val in range(args.index_start, args.index_end + 1):
                        path = f"m/{purpose}'/{coin_type}'/{account_val}'/{change_val}/{index_val}"
                        try:
                            derived_key_object = bip32_manager.derive_path(path) # bip32_manager is now from the current PBKDF2 iteration's seed
                            private_key_bytes = bip32_manager.get_private_key(derived_key_object)
                            public_key_compressed_bytes = bip32_manager.get_public_key(derived_key_object)
                            public_key_compressed_hex = public_key_compressed_bytes.hex()

                            address_value = ""
                            public_key_to_display_hex = ""

                            if args.coin == "ETH":
                                eth_manager = ETHManager(private_key_bytes)
                                address_value = eth_manager.get_address()
                                eth_public_key_object = eth_manager.get_public_key()
                                public_key_to_display_hex = eth_public_key_object.to_bytes().hex()
                            elif args.coin == "BTC" and bitcoin_manager:
                                try:
                                    address_value = bitcoin_manager.get_p2wpkh_address(public_key_compressed_hex)
                                    public_key_to_display_hex = public_key_compressed_hex
                                except ValueError as ve:
                                    print(f"Error generating BTC address for path {path} (PBKDF2 {current_pbkdf2_iteration} rounds): {ve}")
                                    address_value = "Error"
                                    public_key_to_display_hex = public_key_compressed_hex
                                except Exception as e_btc:
                                    print(f"Unexpected BTC derivation error for path {path} (PBKDF2 {current_pbkdf2_iteration} rounds): {e_btc}")
                                    address_value = "Error"
                                    public_key_to_display_hex = public_key_compressed_hex

                            row_data = [current_pbkdf2_iteration, path, address_value, private_key_bytes.hex(), public_key_to_display_hex]
                            if csv_writer:
                                csv_writer.writerow(row_data)
                            else:
                                print(",".join(map(str, row_data)))
                            results_found += 1

                            if target_addresses and address_value != "Error":
                                normalized_derived_address = address_value.lower() if args.coin == "ETH" else address_value
                                matched_target = None
                                if normalized_derived_address in target_addresses:
                                    matched_target = normalized_derived_address

                                if matched_target:
                                    print(f"！！！ MATCH FOUND (PBKDF2 {current_pbkdf2_iteration} rounds) ！！！ Path: {path}, Address: {address_value}, Target: {matched_target}")
                                    if matches_writer:
                                        # Matches header: ["Path", "Derived_Address", "Matched_Target_Address", "Private_Key_Hex", "Public_Key_Hex"]
                                        match_row_data_for_file = [current_pbkdf2_iteration, path, address_value, matched_target, private_key_bytes.hex(), public_key_to_display_hex]
                                        matches_writer.writerow(match_row_data_for_file)


                        except Exception as e:
                            message = f"Error deriving path {path} (PBKDF2 {current_pbkdf2_iteration} rounds): {e}"
                            if csv_writer:
                                 csv_writer.writerow([current_pbkdf2_iteration, path, message, "", ""]) # Corrected to 5 elements
                            else:
                                print(message)

        # Close files after all loops are done
        if output_file_handle: # This is the main output file
            output_file_handle.close()
            print(f"All results saved to {args.output_file}")

        if matches_file_handle:
            matches_file_handle.close()
            print(f"Found matches saved to {args.matches_file}")

        print("---")
        print(f"Sequential search finished. Found {results_found} addresses.")

    elif args.command == "search-random":
        print(f"Initiating random search for {args.coin} addresses...")
        print(f"Mnemonic: {args.mnemonic}")
        if args.passphrase:
            print(f"Passphrase: {args.passphrase}")
        else:
            print("Passphrase: [none]")
        print(f"Coin Type: {args.coin}")
        print(f"Account Range: {args.account_min}-{args.account_max}")
        print(f"Change Range: {args.change_min}-{args.change_max}")
        print(f"Index Range: {args.index_min}-{args.index_max}")
        print(f"Number of Iterations: {args.iterations}")
        print(f"PBKDF2 Iterations: {args.pbkdf2_rounds}")
        print("---")

        # Validate ranges
        if args.account_min > args.account_max:
            print("Error: Account min cannot be greater than account max.")
            return
        if args.change_min > args.change_max:
            print("Error: Change min cannot be greater than change max.")
            return
        if args.index_min > args.index_max:
            print("Error: Index min cannot be greater than index max.")
            return

        try:
            seed = bip39_manager.generate_seed_custom_pbkdf2(args.mnemonic, passphrase=args.passphrase, iterations=args.pbkdf2_rounds)
        except ValueError as ve:
            print(f"Error during seed generation: {ve}")
            return

        bip32_manager = BIP32Manager(seed)

        if args.coin == "ETH":
            purpose = 44
            coin_type = 60
            address_header_name = "ETH_Address"
            public_key_header_name = "Public_Key_Uncompressed_Hex"
            bitcoin_manager = None
        elif args.coin == "BTC":
            purpose = 84
            coin_type = 0
            address_header_name = "BTC_Address_P2WPKH"
            public_key_header_name = "Public_Key_Compressed_Hex"
            bitcoin_manager = BitcoinManager(network='mainnet')
        else:
            print(f"Error: Unsupported coin type {args.coin}") # Should not happen
            return

        # Target address loading and matches file setup
        target_addresses = set()
        if args.target_file:
            try:
                with open(args.target_file, "r") as f_targets:
                    for line in f_targets:
                        addr = line.strip()
                        if addr:
                            if args.coin == "ETH":
                                target_addresses.add(addr.lower())
                            else:
                                target_addresses.add(addr)
                print(f"INFO: Loaded {len(target_addresses)} target addresses from {args.target_file}")
            except IOError as e:
                print(f"Error reading target file {args.target_file}: {e}. Proceeding without target matching.")
                target_addresses.clear()

        matches_writer = None
        matches_file_handle = None
        # Matches header updated to include PBKDF2_Rounds
        matches_header = ["PBKDF2_Rounds", "Path", "Derived_Address", "Matched_Target_Address", "Private_Key_Hex", "Public_Key_Hex"]
        if args.matches_file:
            try:
                matches_file_handle = open(args.matches_file, "w", newline="")
                matches_writer = csv.writer(matches_file_handle)
                matches_writer.writerow(matches_header)
                print(f"Saving found matches to {args.matches_file}...")
            except IOError as e:
                print(f"Error: Could not open matches file {args.matches_file} for writing: {e}")
                matches_writer = None
                matches_file_handle = None

        results_found = 0
        csv_writer = None
        output_file_handle = None
        # Main output header updated
        main_output_header = ["PBKDF2_Rounds", "Path", address_header_name, "Private_Key_Hex", public_key_header_name]

        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(main_output_header)
                print(f"Saving all results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}")
                csv_writer = None
                output_file_handle = None

        if not csv_writer:
            print(",".join(main_output_header))

        for _ in range(args.iterations):
            account_val = random.randint(args.account_min, args.account_max)
            change_val = random.randint(args.change_min, args.change_max)
            index_val = random.randint(args.index_min, args.index_max)
            path = f"m/{purpose}'/{coin_type}'/{account_val}'/{change_val}/{index_val}"
            try:
                derived_key_object = bip32_manager.derive_path(path) # bip32_manager uses the seed from args.pbkdf2_rounds
                private_key_bytes = bip32_manager.get_private_key(derived_key_object)
                public_key_compressed_bytes = bip32_manager.get_public_key(derived_key_object)
                public_key_compressed_hex = public_key_compressed_bytes.hex()

                address_value = ""
                public_key_to_display_hex = ""

                if args.coin == "ETH":
                    eth_manager = ETHManager(private_key_bytes)
                    address_value = eth_manager.get_address()
                    eth_public_key_object = eth_manager.get_public_key()
                    public_key_to_display_hex = eth_public_key_object.to_bytes().hex()
                elif args.coin == "BTC" and bitcoin_manager:
                    try:
                        address_value = bitcoin_manager.get_p2wpkh_address(public_key_compressed_hex)
                        public_key_to_display_hex = public_key_compressed_hex
                    except ValueError as ve:
                        print(f"Error generating BTC address for path {path}: {ve}")
                        address_value = "Error"
                        public_key_to_display_hex = public_key_compressed_hex
                    except Exception as e_btc:
                        print(f"Unexpected BTC derivation error for path {path}: {e_btc}")
                        address_value = "Error"
                        public_key_to_display_hex = public_key_compressed_hex

                row_data = [args.pbkdf2_rounds, path, address_value, private_key_bytes.hex(), public_key_to_display_hex]
                if csv_writer:
                    csv_writer.writerow(row_data)
                else:
                    print(",".join(map(str,row_data)))
                results_found += 1

                if target_addresses and address_value != "Error":
                    normalized_derived_address = address_value.lower() if args.coin == "ETH" else address_value
                    matched_target = None
                    if normalized_derived_address in target_addresses:
                         matched_target = normalized_derived_address

                    if matched_target:
                        print(f"！！！ MATCH FOUND (PBKDF2 {args.pbkdf2_rounds} rounds) ！！！ Path: {path}, Address: {address_value}, Target: {matched_target}")
                        if matches_writer:
                            match_row_data_for_file = [args.pbkdf2_rounds, path, address_value, matched_target, private_key_bytes.hex(), public_key_to_display_hex]
                            matches_writer.writerow(match_row_data_for_file)

            except Exception as e:
                message = f"Error deriving path {path} (PBKDF2 {args.pbkdf2_rounds} rounds): {e}"
                if csv_writer:
                    csv_writer.writerow([args.pbkdf2_rounds, path, message, "", ""]) # Corrected to 5 elements
                else:
                    print(message)

        if output_file_handle:
            output_file_handle.close()
            print(f"All results saved to {args.output_file}")

        if matches_file_handle:
            matches_file_handle.close()
            print(f"Found matches saved to {args.matches_file}")

        print("---")
        print(f"Random search finished. Generated and checked {results_found} addresses out of {args.iterations} iterations.")

    elif args.command == "search-mnemonics":
        print(f"Initiating random mnemonic search for {args.coin} addresses...")
        print(f"Number of mnemonics to generate: {args.count}")
        print(f"Mnemonic strength: {args.strength} bits")
        print(f"Mnemonic language: {args.language}")
        if args.passphrase:
            print(f"Fixed Passphrase: {args.passphrase}")
        else:
            print("Fixed Passphrase: [none]")
        print(f"Coin Type: {args.coin}")
        print(f"PBKDF2 Iterations: {args.pbkdf2_rounds}")

        default_eth_path = "m/44'/60'/0'/0/0"
        default_btc_path_p2wpkh = "m/84'/0'/0'/0/0"
        current_path_to_use = args.path

        if args.path == default_eth_path and args.coin == "BTC":
            current_path_to_use = default_btc_path_p2wpkh
            print(f"INFO: Default ETH path was specified but coin is BTC. Using BTC default P2WPKH path: {current_path_to_use}")
        elif args.path == default_btc_path_p2wpkh and args.coin == "ETH":
            current_path_to_use = default_eth_path
            print(f"INFO: Default BTC path was specified but coin is ETH. Using ETH default path: {current_path_to_use}")

        print(f"Derivation Path to be used: {current_path_to_use}")
        print("---")

        csv_writer = None
        output_file_handle = None
        bitcoin_manager = None # Define before conditional assignment

        if args.coin == "ETH":
            address_header_name_mnem = "ETH_Address"
            public_key_header_name_mnem = "Public_Key_Uncompressed_Hex"
        elif args.coin == "BTC":
            address_header_name_mnem = "BTC_Address_P2WPKH"
            public_key_header_name_mnem = "Public_Key_Compressed_Hex"
            network_type_mnem = 'mainnet'
            if current_path_to_use.startswith("m/84'/1'") or current_path_to_use.startswith("m/44'/1'"):
                network_type_mnem = 'testnet'
                print(f"INFO: Detected potential Bitcoin testnet path ({current_path_to_use}), using network='testnet' for BitcoinManager.")
            bitcoin_manager = BitcoinManager(network=network_type_mnem)
        else:
            print(f"Error: Unsupported coin type {args.coin}") # Should not happen
            return

        # Header updated to include PBKDF2_Rounds
        main_output_header_mnem = ["Mnemonic_Phrase", "PBKDF2_Rounds", "Path", address_header_name_mnem, "Private_Key_Hex", public_key_header_name_mnem]

        if args.output_file:
            try:
                output_file_handle = open(args.output_file, "w", newline="")
                csv_writer = csv.writer(output_file_handle)
                csv_writer.writerow(main_output_header_mnem)
                print(f"Saving results to {args.output_file}...")
            except IOError as e:
                print(f"Error: Could not open file {args.output_file} for writing: {e}")
                csv_writer = None
                output_file_handle = None

        if not csv_writer:
            print(",".join(main_output_header_mnem))

        current_bip39_manager = BIP39Manager(language=args.language) # For generating mnemonics in specified language
        generated_count = 0

        for _ in range(args.count):
            mnemonic_phrase = ""
            try:
                mnemonic_phrase = current_bip39_manager.generate_mnemonic(strength=args.strength)
                if not current_bip39_manager.is_mnemonic_valid(mnemonic_phrase): # Should generally be valid
                    message = f"Generated an invalid mnemonic: {mnemonic_phrase} - skipping."
                    if csv_writer: csv_writer.writerow([mnemonic_phrase, args.pbkdf2_rounds, current_path_to_use, message, "", ""])
                    else: print(message)
                    continue

                # Use generate_seed_custom_pbkdf2 here, current_bip39_manager is fine as it's not language specific for this method
                seed = bip39_manager.generate_seed_custom_pbkdf2(mnemonic_phrase, passphrase=args.passphrase, iterations=args.pbkdf2_rounds)
                bip32_manager_local = BIP32Manager(seed)
                derived_key_object = bip32_manager_local.derive_path(current_path_to_use)
                private_key_bytes = bip32_manager_local.get_private_key(derived_key_object)
                public_key_compressed_bytes = bip32_manager_local.get_public_key(derived_key_object)
                public_key_compressed_hex = public_key_compressed_bytes.hex()

                address_value = ""
                public_key_to_display_hex = ""

                if args.coin == "ETH":
                    eth_manager = ETHManager(private_key_bytes)
                    address_value = eth_manager.get_address()
                    eth_public_key_object = eth_manager.get_public_key()
                    public_key_to_display_hex = eth_public_key_object.to_bytes().hex()
                elif args.coin == "BTC" and bitcoin_manager:
                    try:
                        address_value = bitcoin_manager.get_p2wpkh_address(public_key_compressed_hex)
                        public_key_to_display_hex = public_key_compressed_hex
                    except ValueError as ve:
                        print(f"Error generating BTC address for mnemonic '{mnemonic_phrase}' path {current_path_to_use}: {ve}")
                        address_value = "Error"
                        public_key_to_display_hex = public_key_compressed_hex
                    except Exception as e_btc:
                        print(f"Unexpected BTC derivation error for mnemonic '{mnemonic_phrase}' path {current_path_to_use}: {e_btc}")
                        address_value = "Error"
                        public_key_to_display_hex = public_key_compressed_hex

                row_data = [mnemonic_phrase, current_path_to_use, address_value, private_key_bytes.hex(), public_key_to_display_hex]
                if csv_writer:
                    csv_writer.writerow(row_data)
                else:
                    # Ensure mnemonic_phrase is quoted for stdout if it contains spaces or commas
                    print(f'"{mnemonic_phrase}",{current_path_to_use},{address_value},{private_key_bytes.hex()},{public_key_to_display_hex}')
                generated_count += 1
            except Exception as e:
                message = f"Error processing mnemonic '{mnemonic_phrase}': {e}"
                if csv_writer: csv_writer.writerow([mnemonic_phrase, current_path_to_use, message, "", ""])
                else: print(message)

        if output_file_handle:
            output_file_handle.close()
            print(f"Results saved to {args.output_file}")

        print("---")
        print(f"Random mnemonic search finished. Processed {generated_count} mnemonics.")

if __name__ == "__main__":
    main()
