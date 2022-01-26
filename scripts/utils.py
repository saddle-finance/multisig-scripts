import click
from ape_safe import ApeSafe
from gnosis.safe.safe_tx import SafeTx

def confirm_posting_transaction(safe: ApeSafe, safe_tx: SafeTx):
    should_post = click.confirm(f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?")
    while True:
        if should_post:
            safe.post_transaction(safe_tx)
            print("Transaction posted to network")
            break
        else:
            should_post = click.confirm(f"Post this gnosis safe transaction to {safe.address} on {safe.base_url}?")