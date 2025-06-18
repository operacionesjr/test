# BIP39 Toolkit

A command-line Python tool for working with BIP39 mnemonics, BIP32 hierarchical deterministic wallets, and deriving cryptocurrency addresses (Ethereum and Bitcoin). It includes advanced search functionalities to explore derivation paths, generate multiple mnemonics, and search for specific target addresses.

**Disclaimer:** This tool is provided for educational and experimental purposes. Handle cryptographic keys with extreme care. Do not use this tool with mainnet private keys or mnemonics that control real funds without thorough personal review and understanding of the code and its dependencies.

## Features

*   Generate BIP39 mnemonics of various strengths (12-24 words).
*   Derive BIP39 seeds from mnemonics and optional passphrases.
*   Derive **Ethereum (ETH)** private keys, public keys (uncompressed), and addresses from a mnemonic, passphrase, and BIP32 derivation path.
*   Derive **Bitcoin (BTC)** private keys, public keys (compressed), and addresses (P2PKH, P2SH-P2WPKH, P2WPKH/Bech32) from a mnemonic, passphrase, and BIP32 derivation path.
*   Display detailed information for a single derivation (ETH or BTC): Mnemonic, Passphrase, Seed, BIP32 Root Key (xprv), Path, Private Key, Public Key(s), and Address(es).
*   **Sequential Search:** Iterate through ranges of `account`, `change`, and `address_index` components in derivation paths (e.g., `m/44'/60'/account'/change/address_index` for ETH, `m/84'/0'/account'/change/address_index` for BTC P2WPKH) for a given mnemonic and coin type.
*   **Random Search:** Randomly sample derivation paths within specified ranges for `account`, `change`, and `address_index` for a given mnemonic and coin type.
*   **Random Mnemonic Search:** Generate multiple random mnemonics and derive an address/keys for a fixed path and coin type from each.
*   **Target Address Searching:** For `search-sequential` and `search-random` commands, you can provide a file of target addresses (`--target-file`). The tool will check derived addresses against this list and highlight any matches.
*   **Save Matches:** Found target addresses from searches can be saved to a separate CSV file using `--matches-file`.
*   **CSV Output:** Save results from all search commands to a CSV file using the `--output-file` option. Output format adapts to the selected coin type.
*   **Custom PBKDF2 Iterations:** Specify custom PBKDF2 iteration counts for seed generation (for advanced users; produces non-standard seeds).

## Installation

1.  **Prerequisites:**
    *   Python 3.7+

2.  **Clone the Repository:**
    ```bash
    # git clone <repository_url> # Replace with actual URL when available
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
    This installs necessary libraries such as `mnemonic`, `bip32utils`, `eth-keys`, and `bitcoinutils`.

## Usage

The tool is run as a Python module from the root directory of the project (`bip39_toolkit/`).

```bash
python -m bip39_toolkit.bip39_toolkit.cli <command> [options]
```

Many commands that derive addresses or search for them now include a `--coin <TICKER>` option (choices: `ETH`, `BTC`; default: `ETH`) to specify the cryptocurrency context.

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

#### `derive-address`
Derive and display detailed information for a single address (ETH or BTC).
Options include:
    *   `--pbkdf2-rounds <number>`: Specify the number of PBKDF2 iterations (default: 2048).
    **WARNING:** Using a PBKDF2 iteration count other than 2048 will result in a non-standard seed that is incompatible with most wallets.

**Output includes:** Common details (Mnemonic, Passphrase, PBKDF2 Iterations used, BIP39 Seed, BIP32 Root Key, Path, Private Key, Compressed Public Key) and then coin-specific details.
*   For ETH: Uncompressed Public Key and ETH Address.
*   For BTC: P2PKH, P2SH-P2WPKH, and P2WPKH addresses.

**Example for ETH:**
```bash
python -m bip39_toolkit.bip39_toolkit.cli derive-address "letter ethics correct umbrella prevent search physical space prize type cover strong" --passphrase "testpassphrase" --coin ETH --path "m/44'/60'/0'/0/0"
```

**Example for BTC (BIP84 path for P2WPKH):**
```bash
python -m bip39_toolkit.bip39_toolkit.cli derive-address "letter ethics correct umbrella prevent search physical space prize type cover strong" --passphrase "testpassphrase" --coin BTC --path "m/84'/0'/0'/0/0"
```
**With custom PBKDF2 rounds (e.g., 10000):**
```bash
python -m bip39_toolkit.bip39_toolkit.cli derive-address "your mnemonic..." --coin ETH --pbkdf2-rounds 10000
```

#### `search-sequential`
Sequentially search derivation paths for a chosen coin (ETH or BTC).
The output address and public key formats adapt to the selected coin (ETH address and uncompressed pubkey for ETH; BTC P2WPKH address and compressed pubkey for BTC).
Options include `[--account-start ... --index-end]`, `--output-file`, `--target-file`, `--matches-file`, and:
    *   `--pbkdf2-rounds-start <number>`: Start of PBKDF2 iteration range (default: 2048).
    **WARNING:** Using a PBKDF2 iteration count other than 2048 will result in a non-standard seed that is incompatible with most wallets.
    *   `--pbkdf2-rounds-end <number>`: End of PBKDF2 iteration range (default: 2048).
    **WARNING:** Using a PBKDF2 iteration count other than 2048 will result in a non-standard seed that is incompatible with most wallets.

# Example for ETH: Search account 0, change 0, indices 0-5
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --coin ETH --account-start 0 --account-end 0 --index-start 0 --index-end 5

# Example for BTC with custom PBKDF2 range (2048-2049 iterations):
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --coin BTC --index-start 0 --index-end 0 --pbkdf2-rounds-start 2048 --pbkdf2-rounds-end 2049

# Example for BTC (P2WPKH addresses by default in search): Search account 0, change 0, indices 0-3 (uses default BTC path m/84'/0'/...)
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --coin BTC --account-start 0 --account-end 0 --index-start 0 --index-end 3 --output-file results_btc_seq.csv

# Example for ETH with target address search:
python -m bip39_toolkit.bip39_toolkit.cli search-sequential "your mnemonic..." --coin ETH --index-end 10 --target-file targets.txt --matches-file found_eth.csv
```
**Output columns (stdout or CSV):** `PBKDF2_Rounds, Path, <Coin_Address_Type>, Private_Key_Hex, <Coin_Public_Key_Type_Hex>`

#### `search-random`
Randomly search derivation paths for a chosen coin (ETH or BTC).
Output format adapts like `search-sequential`.
Options include `[--account-min ... --iterations]`, `--output-file`, `--target-file`, `--matches-file`, and:
    *   `--pbkdf2-rounds <number>`: Number of PBKDF2 iterations (default: 2048).
    **WARNING:** Using a PBKDF2 iteration count other than 2048 will result in a non-standard seed that is incompatible with most wallets.

# Example for ETH: 10 random paths
python -m bip39_toolkit.bip39_toolkit.cli search-random "your mnemonic..." --coin ETH --iterations 10

# Example for BTC: 20 random paths, save to CSV
python -m bip39_toolkit.bip39_toolkit.cli search-random "your mnemonic..." --coin BTC --iterations 20 --output-file results_btc_random.csv

# Example for BTC with target address search:
python -m bip39_toolkit.bip39_toolkit.cli search-random "your mnemonic..." --coin BTC --iterations 50 --target-file btc_targets.txt --matches-file found_btc_random.csv
```
**Output columns (stdout or CSV):** `PBKDF2_Rounds, Path, <Coin_Address_Type>, Private_Key_Hex, <Coin_Public_Key_Type_Hex>`

#### `search-mnemonics`
Generate multiple random mnemonics and derive an address for a fixed path and coin type from each.
If the default ETH path (`m/44'/60'/0'/0/0`) is used with `--coin BTC`, the path automatically adjusts to a default BTC P2WPKH path (e.g., `m/84'/0'/0'/0/0`).
Output format adapts like other search commands.
Options include `[--count ... --path]`, `--output-file`, and:
    *   `--pbkdf2-rounds <number>`: Number of PBKDF2 iterations (default: 2048).
    **WARNING:** Using a PBKDF2 iteration count other than 2048 will result in a non-standard seed that is incompatible with most wallets.

# Example for ETH: Generate 5 mnemonics
python -m bip39_toolkit.bip39_toolkit.cli search-mnemonics --coin ETH --count 5 --strength 128

# Example for BTC: Generate 3 mnemonics, use a specific BTC path, save to CSV
python -m bip39_toolkit.bip39_toolkit.cli search-mnemonics --coin BTC --count 3 --path "m/84'/0'/0'/0/0" --output-file results_btc_mnemonics.csv
```
**Output columns (stdout or CSV):** `Mnemonic_Phrase, PBKDF2_Rounds, Path, <Coin_Address_Type>, Private_Key_Hex, <Coin_Public_Key_Type_Hex>`

### General Options
*   `--help`: Show help message for the main tool or a specific command.
    ```bash
    python -m bip39_toolkit.bip39_toolkit.cli --help
    python -m bip39_toolkit.bip39_toolkit.cli derive-address --help
    ```

## Dependencies

This tool relies on the following Python libraries:
*   `mnemonic`: For BIP39 mnemonic generation and seed derivation.
*   `bip32utils`: For BIP32 hierarchical deterministic key derivation.
*   `pycryptodome`: For cryptographic primitives.
*   `eth-keys`: For Ethereum public key and address generation from private keys.
*   `eth-utils`: For Ethereum checksum address utility.
*   `bitcoinutils`: For Bitcoin key and address manipulation, including P2PKH, P2SH-P2WPKH, and P2WPKH (Bech32) addresses.

(The `csv` and `re` modules are part of the Python standard library.)

## Development & Testing

The project includes unit tests and CLI integration tests. To run tests (assuming `unittest` is used and tests are discoverable):
```bash
# Navigate to the root of the project (bip39_toolkit/)
python -m unittest discover -s tests
```
(You might need to adjust the command based on your specific test runner setup if it evolves.)
