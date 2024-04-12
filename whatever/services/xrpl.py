import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

DEFAULT_FLAG = 8


def create_wallet():
    wallet = Wallet.create()
    return wallet.public_key, wallet.private_key, wallet.seed


class XRPLService:
    def __init__(self):
        self.client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    def mint_house(self, seed: str, taxon: int, **kwargs):
        minter_wallet = Wallet.from_seed(seed)
        mint_tx = xrpl.models.transactions.NFTokenMint(
            account=minter_wallet.address,
            uri=xrpl.utils.str_to_hex(kwargs['uri']),
            flags=DEFAULT_FLAG,
            transfer_fee=int(kwargs.get('transfer_fee', 0)),
            nftoken_taxon=int(taxon)
        )
        try:
            response = xrpl.transaction.submit_and_wait(mint_tx, self.client, minter_wallet)
            reply = response.result
        except xrpl.transaction.XRPLReliableSubmissionException as e:
            reply = f"Submit failed: {e}"

        print(reply)
