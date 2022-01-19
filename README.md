# Saddle Multisig Scripts

A collection of ApeSafe scripts which create txns executed by Saddle.finance's multisig

## Set up

On a machine with Python and mkvenv installed...

1. Install pipx globally

    `python3 -m pip install --user pipx && python3 -m pipx ensurepath`

2. Install eth-brownie globally
    `pipx install eth-brownie`

3. Create a new virtual environment (note: don't install deps at this step)

    `mkvenv --python=3.9.9`

4. Install dependencies 

    `pip install --no-deps -r requirements.txt`

5. Add your keys to .env

6. Run your script against a forked mainnet before running against mainnet

    `brownie run scripts/2022_01_15_1_hello_multisig.py --network mainnet-fork`

7. Run your script on mainnet using the multisig private key

## Conventions

### Template
Use `scripts/_template_script.py` to create your new script

### Naming
To keep files organized, use the following structure: 

`year_month_day_chainid_[file_name].py` eg `2022_01_15_1_sip_2_admin_fees.py`

### Safety
Optionally use the helper util to ensure that your file is named correctly and is running on the expected chain.

```python
from helpers import assert_filename
# will throw if the script is run on a chain other than what your filename specifies 
assert_filename(__file__)

...the rest of my script
```

## Links
[Brownie](https://eth-brownie.readthedocs.io/en/stable/toctree.html)

[ApeSafe](https://github.com/banteg/ape-safe)

[Etherscan Cache](https://github.com/banteg/etherscan-cache) (optional)
