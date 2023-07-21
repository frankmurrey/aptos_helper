from aptos_rest_client.client import CustomRestClient
from modules.the_aptos_bridge.src_lz.executor import Executor
from modules.the_aptos_bridge.src_lz.executor_config import ExecutorConfig
from modules.the_aptos_bridge.src_lz.uln.uln_config import UlnConfig


class Endpoint:
    executor_address = '0x1d8727df513fa2a8785d0834e40b34223daff1affc079574082baadb74b66ee4'
    oracle_address = '0x12e12de0af996d9611b0b78928cd9f4cbf50d94d972043cdd829baa77a78929b'
    layerzero_address = '0x54ad3d30af77b60d939ae356e6606de9a4da67583f02b962d2d3f2e481484e90'
    bridge_address = '0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa'
    module = f'{layerzero_address}::endpoint'
    module_name = 'layerzero::endpoint'

    def __init__(self, sdk: CustomRestClient):
        self.sdk = sdk
        self.uln_module = UlnConfig(sdk)
        self.executor = Executor(sdk)
        self.executor_config = ExecutorConfig(sdk)

    def get_UA_type_info(self, ua_address: str):
        resource = self.sdk.account_resource(
            self.layerzero_address,
            f"{self.module}::UaRegistry"
        )

        type_info = self.sdk.get_table_item(
            resource['data']['handle'],
            key_type='address',
            value_type='0x1::type_info::TypeInfo',
            key=ua_address
        )

        return {
            "account_address": type_info["account_address"],
            "module_name": type_info["module_name"],
            "struct_name": type_info["struct_name"],
            "type": f"{type_info['account_address']}::{type_info['module_name']}::{type_info['struct_name']}"
        }

    def get_oracle_fee(self, dst_chain_id: str):
        resource = self.sdk.account_resource(
            self.layerzero_address,
            f"{self.module}::FeeStore"
        )

        response = self.sdk.get_table_item(
            resource['data']['handle'],
            key_type=f"{self.module}::QuoteKey",
            value_type="u64",
            key={
                "agent": self.oracle_address,
                "chain_id": dst_chain_id,
            }
        )

        return response

    def quote_fee(self, ua_address: str, dst_chain_id: int, adapter_params, payload_size):
        total_fee = self.uln_module.quote_fee(ua_address, dst_chain_id, payload_size)
        executor, _ = self.executor_config.get_executor(ua_address, dst_chain_id)
        total_fee += self.executor.quote_fee(executor, dst_chain_id, adapter_params)
        return total_fee



