# BIP39 Toolkit

A command-line Python tool for working with BIP39 mnemonics, BIP32 hierarchical deterministic wallets, and deriving Ethereum addresses. It includes advanced search functionalities to explore derivation paths and generate multiple mnemonics.

**Disclaimer:** This tool is provided for educational and experimental purposes. Handle cryptographic keys with extreme care. Do not use this tool with mainnet private keys or mnemonics that control real funds without thorough personal review and understanding of the code and its dependencies.

## Features

*   Generate BIP39 mnemonics of various strengths (12-24 words).
*   Derive BIP39 seeds from mnemonics and optional passphrases.
*   Derive Ethereum private keys, public keys, and addresses from a mnemonic, passphrase, and BIP32 derivation path.
*   Display detailed information for a single derivation: Mnemonic, Passphrase, Seed, BIP32 Root Key (xprv), Path, Private/Public Keys, and ETH Address.
*   **Sequential Search:** Iterate through ranges of `account`, `change`, and `address_index` components in Ethereum derivation paths (`m/44'/60'/account'/change/address_index`) for a given mnemonic.
*   **Random Search:** Randomly sample derivation paths within specified ranges for `account`, `change`, and `address_index` for a given mnemonic.
*   **Random Mnemonic Search:** Generate multiple random mnemonics and derive an ETH address/keys for a fixed path from each.
*   **CSV Output:** Save results from all search commands to a CSV file using the `--output-file` option.

## Installation

1.  **Prerequisites:**
    *   Python 3.7+

2.  **Clone the Repository:**
    ```bash
    # git clone <repository_url> # Assuming this will be in a git repo
    # cd bip39_toolkit
    ```
    (If not cloning, ensure you have the `bip39_toolkit` directory structure.)

3.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    Navigate to the project's root directory (where `requirements.txt` is located) and run:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The tool is run as a Python module from the root directory of the project (`bip39_toolkit/`).

```bash
python -m bip39_toolkit.bip39_toolkit.cli <command> [options]
```

### Commands

#### `generate`
Generate a new BIP39 mnemonic.
```bash
python -m bip39_toolkit.bip39_toolkit.cli generate --strength 128 --language english
# Strengths: 128 (12 words), 160 (15 words), 192 (18 words), 224 (21 words), 256 (24 words)
```

#### `derive-seed`
Derive a BIP39 seed from a mnemonic.
```bash
python -m bip39_toolkit.bip39_toolkit.cli derive-seed "your twelve word mnemonic phrase here accordingly" --passphrase "optional_secret_passphrase"
```

#### `derive-eth`
Derive and display detailed information for a single Ethereum address.
```bash
python -m bip39_toolkit.bip39_toolkit.cli derive-eth "letter ethics correct umbrella prevent search physical space prize type cover strong" --passphrase "testpassphrase" --path "m/44'/60'/0'/0/0"
```
**Output includes:** Mnemonic, Passphrase, BIP39 Seed, BIP32 Root Key (xprv), Derivation Path, Derived Private Key (hex), Derived Public Key (BIP32 compressed, hex), Derived Public Key (ETH uncompressed, hex), and Derived ETH Address.

#### `search-sequential`
Sequentially search derivation paths.
```bash
# Example: Search account 0, change 0, indices 0-5
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --account-start 0 --account-end 0 --change-start 0 --change-end 0 --index-start 0 --index-end 5

# Save results to CSV
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --index-end 10 --output-file results_sequential.csv
```
**Output columns (stdout or CSV):** `Path, ETH_Address, Private_Key_Hex, Public_Key_Uncompressed_Hex`

#### `search-random`
Randomly search derivation paths.
```bash
# Example: Search 10 random paths within default ranges for account 0, change 0, index 0-1000
python -m bip39_toolkit.bip39_toolkit.cli search-random "your mnemonic..." --iterations 10

# Define specific ranges and save to CSV
python -m bip39_toolkit.bip39_toolkit.cli search-random "your mnemonic..." --account-min 0 --account-max 1 --index-min 0 --index-max 100 --iterations 20 --output-file results_random.csv
```
**Output columns (stdout or CSV):** `Path, ETH_Address, Private_Key_Hex, Public_Key_Uncompressed_Hex`

#### `search-mnemonics`
Generate multiple random mnemonics and derive an address for a fixed path from each.
```bash
# Example: Generate 5 mnemonics (12 words) and derive address for default path m/44'/60'/0'/0/0
python -m bip39_toolkit.bip39_toolkit.cli search-mnemonics --count 5 --strength 128

# Use a specific path and passphrase, save to CSV
python -m bip39_toolkit.bip39_toolkit.cli search-mnemonics --count 10 --passphrase "fixed_secret" --path "m/44'/60'/1'/0/0" --output-file results_mnemonics.csv
```
**Output columns (stdout or CSV):** `Mnemonic_Phrase, Path, ETH_Address, Private_Key_Hex, Public_Key_Uncompressed_Hex` (Mnemonic phrase will be quoted if printed to stdout and contains spaces).

### General Options
*   `--help`: Show help message for the main tool or a specific command.
    ```bash
    python -m bip39_toolkit.bip39_toolkit.cli --help
    python -m bip39_toolkit.bip39_toolkit.cli derive-eth --help
    ```

## Dependencies

This tool relies on the following Python libraries:
*   `mnemonic`: For BIP39 mnemonic generation and seed derivation.
*   `bip32utils`: For BIP32 hierarchical deterministic key derivation. (Note: Ensure you are using a version compatible with the expected API, or adapt as needed. `pybip32` is an alternative).
*   `pycryptodome`: For cryptographic primitives if not covered by other libraries (e.g. HMAC, SHA).
*   `eth-keys`: For Ethereum public key and address generation from private keys.
*   `eth-utils`: For Ethereum checksum address utility.

(The `csv` module is part of the Python standard library.)

## Development & Testing

The project includes unit tests and basic CLI integration tests. To run tests (assuming `unittest` is used and tests are discoverable):
```bash
# Navigate to the root of the project (bip39_toolkit/)
python -m unittest discover -s tests
```
(You might need to adjust the command based on your specific test runner setup if it evolves.)
