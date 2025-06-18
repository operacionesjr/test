import unittest
import subprocess
import os
import csv
import re

# Define the path to the CLI script.
# This assumes the tests are run from the root of the 'bip39_toolkit' project directory.
CLI_SCRIPT_PATH = ["python", "-m", "bip39_toolkit.bip39_toolkit.cli"]

# Known test mnemonic from other tests
TEST_MNEMONIC = "letter ethics correct umbrella prevent search physical space prize type cover strong"
TEST_PASSPHRASE = "testpassphrase" # Used in test_eth_manager for the known address
EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH = "0x5f9800971ADC009893185C587107913259659167" # For m/44'/60'/0'/0/0 with TEST_PASSPHRASE
DEFAULT_PATH = "m/44'/60'/0'/0/0"

class TestCLI(unittest.TestCase):

    def run_cli_command(self, args):
        try:
            process = subprocess.run(CLI_SCRIPT_PATH + args, capture_output=True, text=True, check=False, timeout=30)
            return process
        except subprocess.TimeoutExpired:
            self.fail(f"CLI command {' '.join(args)} timed out.")
        except Exception as e:
            self.fail(f"CLI command {' '.join(args)} failed with exception: {e}")


    def test_cli_help(self):
        result = self.run_cli_command(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage: cli.py [-h]", result.stdout) # Note: main module name is cli.py, not __main__.py when run with -m
        self.assertIn("Available commands", result.stdout)

    def test_cli_generate_mnemonic(self):
        result = self.run_cli_command(["generate", "--strength", "128"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Generated Mnemonic:", result.stdout)
        mnemonic_line = [line for line in result.stdout.split('\n') if "Generated Mnemonic:" in line][0]
        mnemonic_phrase = mnemonic_line.split("Generated Mnemonic:")[1].strip()
        self.assertEqual(len(mnemonic_phrase.split()), 12)

    def test_cli_derive_eth_known_mnemonic(self):
        # This test is for the old command name, should be updated or removed if derive-eth is fully replaced.
        # For now, assuming 'derive-address --coin ETH' is the replacement.
        # Let's adapt this test to use the new 'derive-address' command for ETH.
        args = ["derive-address", TEST_MNEMONIC, "--passphrase", TEST_PASSPHRASE, "--path", DEFAULT_PATH, "--coin", "ETH"]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn(EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH, result.stdout)
        self.assertIn("Mnemonic:", result.stdout)
        self.assertIn("Passphrase:", result.stdout)
        self.assertIn("BIP39 Seed (hex):", result.stdout)
        self.assertIn("BIP32 Root Key (xprv):", result.stdout)
        self.assertIn("Derived Private Key (hex):", result.stdout)

    def test_cli_search_sequential_small_range(self):
        args = [
            "search-sequential", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--account-start", "0", "--account-end", "0",
            "--change-start", "0", "--change-end", "0",
            "--index-start", "0", "--index-end", "0" # Only 1 address
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("Path,ETH_Address,Private_Key_Hex,Public_Key_Uncompressed_Hex", result.stdout.replace(" ", "")) # Header, remove spaces for robust check
        self.assertIn(f"{DEFAULT_PATH},{EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH}", result.stdout.replace(" ", ""))
        self.assertIn("Sequential search finished. Found 1 addresses.", result.stdout)

    def test_cli_search_random_small_run(self):
        args = [
            "search-random", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--account-min", "0", "--account-max", "0",
            "--change-min", "0", "--change-max", "0",
            "--index-min", "0", "--index-max", "0",
            "--iterations", "1"
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("Path,ETH_Address,Private_Key_Hex,Public_Key_Uncompressed_Hex", result.stdout.replace(" ", ""))
        self.assertIn(f"{DEFAULT_PATH},{EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH}", result.stdout.replace(" ", ""))
        self.assertIn("Random search finished. Generated and checked 1 addresses out of 1 iterations.", result.stdout)

    def test_cli_search_mnemonics_small_run(self):
        args = [
            "search-mnemonics",
            "--count", "1",
            "--strength", "128",
            "--path", DEFAULT_PATH,
            "--passphrase", "test"
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("Mnemonic_Phrase,Path,ETH_Address,Private_Key_Hex,Public_Key_Uncompressed_Hex", result.stdout.replace(" ", ""))
        self.assertIn(DEFAULT_PATH, result.stdout)
        self.assertIn("Random mnemonic search finished. Processed 1 mnemonics.", result.stdout)

    def test_cli_search_sequential_csv_output(self):
        output_csv_file = "test_output_sequential.csv"
        # Ensure file does not exist before test
        if os.path.exists(output_csv_file):
            os.remove(output_csv_file)

        args = [
            "search-sequential", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--account-start", "0", "--account-end", "0",
            "--change-start", "0", "--change-end", "0",
            "--index-start", "0", "--index-end", "0",
            "--output-file", output_csv_file
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertTrue(os.path.exists(output_csv_file), f"CSV output file {output_csv_file} was not created.")

        with open(output_csv_file, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, ["Path", "ETH_Address", "Private_Key_Hex", "Public_Key_Uncompressed_Hex"])
            try:
                data_row = next(reader)
                self.assertEqual(data_row[0], DEFAULT_PATH)
                self.assertEqual(data_row[1], EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH)
            except StopIteration:
                self.fail("CSV file is empty or missing data rows.")

        if os.path.exists(output_csv_file): # Clean up
            os.remove(output_csv_file)

    def test_cli_invalid_mnemonic_derive_eth(self):
        # This test should also be updated for 'derive-address'
        args = ["derive-address", "--coin", "ETH", "invalid mnemonic phrase not long enough or correct words", "--path", DEFAULT_PATH]
        result = self.run_cli_command(args)
        # The mnemonic library's `to_seed` calls `check()` which raises exceptions.
        # The cli.py does not currently have a try-except block around `bip39_manager.mnemonic_to_seed`.
        # So, an unhandled exception in the subprocess is expected to result in a non-zero return code.
        # The error message from the mnemonic library (e.g. "Invalid mnemonic checksum") would go to stderr.
        self.assertNotEqual(result.returncode, 0, "Command should fail for invalid mnemonic. STDOUT: {result.stdout} STDERR: {result.stderr}")
        # A more specific check on stderr might be too brittle if library error messages change.
        # Checking for the presence of "error" in stderr is a reasonable expectation.
        self.assertIn("error", result.stderr.lower(), f"stderr should contain 'error'. STDERR: {result.stderr}")


    def test_cli_search_sequential_with_target_file_match(self):
        target_file_content = f"{EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH}\n0xNonExistentAddress123\n"
        temp_target_filename = "temp_targets_seq_match.txt"
        temp_matches_filename = "temp_matches_seq.csv"

        # Ensure clean slate for test files
        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)

        with open(temp_target_filename, "w") as f:
            f.write(target_file_content)

        args = [
            "search-sequential", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--coin", "ETH", # Explicitly ETH for this test case
            "--account-start", "0", "--account-end", "0",
            "--change-start", "0", "--change-end", "0",
            "--index-start", "0", "--index-end", "1", # Search a small range including the known address
            "--target-file", temp_target_filename,
            "--matches-file", temp_matches_filename
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Check stdout for match found message
        self.assertIn("！！！ MATCH FOUND ！！！", result.stdout)
        self.assertIn(EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH, result.stdout)
        self.assertIn(f"Path: {DEFAULT_PATH}", result.stdout)

        # Check matches CSV file
        self.assertTrue(os.path.exists(temp_matches_filename))
        with open(temp_matches_filename, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header[0], "Path")
            self.assertEqual(header[1], "Derived_Address")
            self.assertEqual(header[2], "Matched_Target_Address")

            found_match_in_csv = False
            for row in reader:
                if row[0] == DEFAULT_PATH and row[1].lower() == EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH.lower():
                    # Matched_Target_Address in CSV is what was in the target file, which is already lowercased for ETH during load by CLI
                    self.assertEqual(row[2].lower(), EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH.lower())
                    found_match_in_csv = True
                    break
            self.assertTrue(found_match_in_csv, "Expected match not found in matches CSV file.")

        # Clean up
        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)

    def test_cli_search_sequential_with_target_file_no_match(self):
        target_file_content = "0xNonExistentAddress123\n0xAnotherNonExistentAddress456\n"
        temp_target_filename = "temp_targets_seq_no_match.txt"
        temp_matches_filename = "temp_matches_seq_no.csv"

        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)

        with open(temp_target_filename, "w") as f:
            f.write(target_file_content)

        args = [
            "search-sequential", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--coin", "ETH",
            "--account-start", "0", "--account-end", "0",
            "--change-start", "0", "--change-end", "0",
            "--index-start", "0", "--index-end", "0",
            "--target-file", temp_target_filename,
            "--matches-file", temp_matches_filename
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        self.assertNotIn("！！！ MATCH FOUND ！！！", result.stdout)

        self.assertTrue(os.path.exists(temp_matches_filename))
        with open(temp_matches_filename, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            try:
                next(reader)
                self.fail("Matches file should be empty (only header) if no matches found.")
            except StopIteration:
                pass

        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)

    def test_cli_search_random_with_target_file_match(self):
        target_file_content = f"{EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH}\n"
        temp_target_filename = "temp_targets_rand_match.txt"
        temp_matches_filename = "temp_matches_rand.csv"

        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)

        with open(temp_target_filename, "w") as f:
            f.write(target_file_content)

        args = [
            "search-random", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--coin", "ETH",
            "--account-min", "0", "--account-max", "0",
            "--change-min", "0", "--change-max", "0",
            "--index-min", "0", "--index-max", "0",
            "--iterations", "5",
            "--target-file", temp_target_filename,
            "--matches-file", temp_matches_filename
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        self.assertIn("！！！ MATCH FOUND ！！！", result.stdout)
        self.assertIn(EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH, result.stdout)

        self.assertTrue(os.path.exists(temp_matches_filename))
        with open(temp_matches_filename, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header[0], "Path")
            data_row = next(reader)
            self.assertEqual(data_row[1].lower(), EXPECTED_ETH_ADDRESS_FOR_TEST_MNEMONIC_AND_PATH.lower())

        if os.path.exists(temp_target_filename): os.remove(temp_target_filename)
        if os.path.exists(temp_matches_filename): os.remove(temp_matches_filename)


    def test_cli_derive_address_btc(self):
        # Test with BIP84 path for P2WPKH
        btc_path_bip84 = "m/84'/0'/0'/0/0"
        args_bip84 = ["derive-address", TEST_MNEMONIC, "--passphrase", TEST_PASSPHRASE, "--coin", "BTC", "--path", btc_path_bip84]
        result_bip84 = self.run_cli_command(args_bip84)
        self.assertEqual(result_bip84.returncode, 0, f"STDOUT_BIP84: {result_bip84.stdout}\nSTDERR_BIP84: {result_bip84.stderr}")
        self.assertIn("Derived BTC Addresses:", result_bip84.stdout)
        self.assertIn("P2PKH (Legacy):", result_bip84.stdout)
        self.assertIn("P2SH-P2WPKH (SegWit-in-P2SH):", result_bip84.stdout)
        self.assertIn("P2WPKH (Native SegWit/Bech32):", result_bip84.stdout)
        self.assertIn("bc1q", result_bip84.stdout) # Check for Bech32 prefix for P2WPKH

        # Check that a compressed public key is displayed (starts with 02 or 03)
        self.assertTrue(re.search(r"Derived Public Key \(BIP32 compressed, hex\): (02|03)[0-9a-fA-F]{64}", result_bip84.stdout) is not None, "Compressed public key not found or invalid format for BTC.")
        # Ensure no ETH uncompressed pubkey is shown for BTC
        self.assertNotIn("Derived Public Key (ETH uncompressed, hex):", result_bip84.stdout)


    def test_cli_search_sequential_btc(self):
        args = [
            "search-sequential", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--coin", "BTC",
            "--account-start", "0", "--account-end", "0",
            "--change-start", "0", "--change-end", "0",
            "--index-start", "0", "--index-end", "0" # Only 1 address
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Check for BTC specific header (P2WPKH is the default for search)
        self.assertIn("Path,BTC_Address_P2WPKH,Private_Key_Hex,Public_Key_Compressed_Hex", result.stdout.replace(" ", ""))

        # Check if a BTC P2WPKH address is present
        output_lines = result.stdout.splitlines()
        data_line = ""
        for line in output_lines:
            if line.startswith("m/84'/0'/0'/0/0"): # Default path used for BTC search
                data_line = line
                break
        self.assertTrue(data_line, "Data line for BTC search not found.")
        self.assertIn("bc1q", data_line, "P2WPKH address prefix not found in BTC search output.")

        parts = data_line.split(',')
        self.assertTrue(len(parts) == 4, "Output does not have 4 columns for BTC search.")
        self.assertTrue(parts[3].strip().startswith(("02", "03")) and len(parts[3].strip()) == 66, "Compressed public key format incorrect in BTC search output.")

        self.assertIn("Sequential search finished. Found 1 addresses.", result.stdout)

    def test_cli_search_random_btc(self):
        args = [
            "search-random", TEST_MNEMONIC,
            "--passphrase", TEST_PASSPHRASE,
            "--coin", "BTC",
            "--account-min", "0", "--account-max", "0",
            "--change-min", "0", "--change-max", "0",
            "--index-min", "0", "--index-max", "0",
            "--iterations", "1"
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("Path,BTC_Address_P2WPKH,Private_Key_Hex,Public_Key_Compressed_Hex", result.stdout.replace(" ", ""))
        self.assertIn("bc1q", result.stdout)
        self.assertIn("Random search finished. Generated and checked 1 addresses out of 1 iterations.", result.stdout)

    def test_cli_search_mnemonics_btc(self):
        args = [
            "search-mnemonics",
            "--count", "1",
            "--strength", "128",
            "--coin", "BTC",
        ]
        result = self.run_cli_command(args)
        self.assertEqual(result.returncode, 0, f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        self.assertIn("INFO: Default ETH path was specified but coin is BTC. Using BTC default P2WPKH path: m/84'/0'/0'/0/0", result.stdout)
        self.assertIn("Mnemonic_Phrase,Path,BTC_Address_P2WPKH,Private_Key_Hex,Public_Key_Compressed_Hex", result.stdout.replace(" ", ""))
        self.assertIn("m/84'/0'/0'/0/0", result.stdout)
        self.assertIn("bc1q", result.stdout)
        self.assertIn("Random mnemonic search finished. Processed 1 mnemonics.", result.stdout)

if __name__ == "__main__":
    unittest.main()
