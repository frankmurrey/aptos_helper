from aptos_rest_client.client import CustomRestClient


class UlnSigner:
    executor_address = '0x1d8727df513fa2a8785d0834e40b34223daff1affc079574082baadb74b66ee4'
    oracle_address = '0x12e12de0af996d9611b0b78928cd9f4cbf50d94d972043cdd829baa77a78929b'
    layerzero_address = '0x54ad3d30af77b60d939ae356e6606de9a4da67583f02b962d2d3f2e481484e90'
    bridge_address = '0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa'
    module = f'{layerzero_address}::uln_signer'
    module_name = 'layerzero::uln_signer'

    def __init__(self, sdk: CustomRestClient):
        self.sdk = sdk

    def get_fee(self, address: str, dst_chain_id: int):
        resource = self.sdk.account_resource(
            address,
            f"{self.module}::Config"
        )

        response = self.sdk.get_table_item(
            resource['data']['fees']['handle'],
            key_type='u64',
            value_type=f'{self.module}::Fee',
            key=str(dst_chain_id),
        )

        return {
            "base_fee": response['base_fee'],
            "fee_per_byte": response['fee_per_byte']
        }
