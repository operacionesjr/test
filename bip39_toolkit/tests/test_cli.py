import unittest
import subprocess
import os
import csv

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
        args = ["derive-eth", TEST_MNEMONIC, "--passphrase", TEST_PASSPHRASE, "--path", DEFAULT_PATH]
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
        args = ["derive-eth", "invalid mnemonic phrase not long enough or correct words", "--path", DEFAULT_PATH]
        result = self.run_cli_command(args)
        # The mnemonic library's `to_seed` calls `check()` which raises exceptions.
        # The cli.py does not currently have a try-except block around `bip39_manager.mnemonic_to_seed`.
        # So, an unhandled exception in the subprocess is expected to result in a non-zero return code.
        # The error message from the mnemonic library (e.g. "Invalid mnemonic checksum") would go to stderr.
        self.assertNotEqual(result.returncode, 0, "Command should fail for invalid mnemonic. STDOUT: {result.stdout} STDERR: {result.stderr}")
        # A more specific check on stderr might be too brittle if library error messages change.
        # Checking for the presence of "error" in stderr is a reasonable expectation.
        self.assertIn("error", result.stderr.lower(), f"stderr should contain 'error'. STDERR: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
