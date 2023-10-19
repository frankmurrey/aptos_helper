import binascii
import struct
from typing import Optional

from aptos_rest_client.client import CustomRestClient


class Executor:
    executor_address = '0x1d8727df513fa2a8785d0834e40b34223daff1affc079574082baadb74b66ee4'
    oracle_address = '0x12e12de0af996d9611b0b78928cd9f4cbf50d94d972043cdd829baa77a78929b'
    layerzero_address = '0x54ad3d30af77b60d939ae356e6606de9a4da67583f02b962d2d3f2e481484e90'
    module = f'{layerzero_address}::executor_v1'
    module_name = 'layerzero::executor_v1'
    type = f'${module}::Executor'

    def __init__(self, sdk: CustomRestClient):
        self.sdk = sdk

    def decode_adapter_params(self, adapter_params: str):
        byte_array = bytes.fromhex(adapter_params[2:])
        type_ = struct.unpack('>H', byte_array[:2])[0]
        if type_ == 1:
            # default
            assert len(byte_array) == 10, "invalid adapter params"
            return [type_, struct.unpack('!Q', byte_array[2:])[0], 0, '']
        elif type_ == 2:
            # airdrop
            assert len(byte_array) > 18, "invalid adapter params"
            ua_gas, airdrop_amount = struct.unpack('!QQ', byte_array[2:18])
            airdrop_address = "0x" + binascii.hexlify(byte_array[18:]).decode("utf-8")
            return [type_, ua_gas, airdrop_amount, airdrop_address]
        else:
            assert False, "invalid adapter params"

    def get_default_adapter_params(self, dst_chain_id: int):
        resource = self.sdk.account_resource(
            self.layerzero_address,
            f"{self.module}::AdapterParamsConfig"
        )

        response = self.sdk.get_table_item(
            resource['data']['params']['handle'],
            'u64',
            'vector<u8>',
            str(dst_chain_id)
        )

        return response

    def get_fee(self, executor: str, dst_chain_id: int):
        resource = self.sdk.account_resource(
            executor,
            f"{self.layerzero_address}::executor_v1::ExecutorConfig"
        )

        response = self.sdk.get_table_item(
            resource['data']['fee']['handle'],
            'u64',
            f'{self.module}::Fee',
            str(dst_chain_id)
        )

        return {
            "airdrop_amt_cap": response['airdrop_amt_cap'],
            "gas_price": response["gas_price"],
            "price_ratio": response["price_ratio"]
        }

    def quote_fee(self, executor: str, dst_chain_id: int, adapter_params: Optional[list] = None) -> int:
        if not adapter_params:
            adapter_params = self.get_default_adapter_params(dst_chain_id)

        fee = self.get_fee(executor, dst_chain_id)
        _, ua_gas, airdrop_amount, _ = self.decode_adapter_params(adapter_params)

        return ((ua_gas * int(fee['gas_price']) + airdrop_amount) * int(fee['price_ratio'])) / 10000000000
