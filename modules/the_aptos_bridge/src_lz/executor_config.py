from aptos_rest_client.client import CustomRestClient


class ExecutorConfig:
    executor_address = '0x1d8727df513fa2a8785d0834e40b34223daff1affc079574082baadb74b66ee4'
    oracle_address = '0x12e12de0af996d9611b0b78928cd9f4cbf50d94d972043cdd829baa77a78929b'
    layerzero_address = '0x54ad3d30af77b60d939ae356e6606de9a4da67583f02b962d2d3f2e481484e90'
    module = f'{layerzero_address}::executor_config'

    def __init__(self, sdk: CustomRestClient):
        self.sdk = sdk

    def get_executor(self, ua_address: str, dst_chain_id: int):
        resource = self.sdk.account_resource(
            self.layerzero_address,
            f"{self.module}::ConfigStore",
        )
        response = self.sdk.get_table_item(
            resource['data']['config']['handle'],
            key_type='u64',
            value_type=f"{self.module}::Config",
            key=str(dst_chain_id),
        )

        return [response['executor'], response['version']]

