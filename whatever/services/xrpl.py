import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet

DEFAULT_FLAG = 8

class XRPLService:
    def __init__(self):
        self.client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

    def get_or_create_wallet(self, seed:str =None) -> tuple:
        if not seed:
            wallet = generate_faucet_wallet(self.client)
        else:
            wallet = Wallet.from_seed(seed)
        return wallet.public_key, wallet.private_key, wallet.seed

    def mint_house(self, seed: str, taxon: int, **kwargs):
        minter_wallet = Wallet.from_seed(seed)
        mint_tx = xrpl.models.transactions.NFTokenMint(
            account=minter_wallet.address,
            uri=xrpl.utils.str_to_hex(kwargs['uri']),
            flags=DEFAULT_FLAG,
            transfer_fee=int(kwargs.get('transfer_fee', 0)),
            nftoken_taxon=int(taxon)
        )
        reply = None
        try:
            print("mint tx", mint_tx)
            print("minter wallet", minter_wallet)
            response = xrpl.transaction.submit_and_wait(mint_tx, self.client, minter_wallet)
            reply = response.result
        except Exception as e:
            print("Failed, ", e)
        return reply

