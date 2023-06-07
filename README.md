# Saddle Multisig Scripts

A collection of ApeSafe scripts which create txns executed by Saddle.finance's multisig

## Set up

On a machine with Python and mkvenv installed...

1. ***WARNING** this will overwrite existing global brownie network config*

    Run `./setup.sh` to install deps, move files, and add deployer account. Interactive. 
    
2. Run your script against a forked mainnet

    `brownie run scripts/2022_01_15_1_hello_multisig.py --network mainnet-fork`

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


## Troubleshooting
Ensure you have ganache v7 installation
```sh
> ganache-cli --version
ganache v7.7.3 (@ganache/cli: 0.8.2, @ganache/core: 0.8.2)
```
If you are using ganache v6, follow the upgrade guide below to install ganache v7
https://github.com/trufflesuite/ganache/blob/develop/UPGRADE-GUIDE.md

If pip installation fails inside a venv, try removing all pip packages and reinstalling.

```sh
git checkout origin/master requirements.txt
pip uninstall -y -r <(pip freeze)
pip install --no-deps -r requirements.txt
```