import os
import json

from typing import Union, List

from src.paths import (APTOS_WALLETS_FILE,
                       EVM_ADDRESSES_FILE)
from src.schemas.wallet_data import (WalletData,
                                     ProxyData)


class FileManager:
    wallet_length: int

    def __init__(self):
        self.wallet_length = 66

    def read_data_from_txt_file(self, file_path) -> Union[list, None]:
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as file:
            data = file.read().splitlines()
            return data

    def read_data_from_json_file(self, file_path) -> Union[list, None]:
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data
        except Exception as e:
            return None

    def write_data_to_json_file(self, file_path, data) -> None:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def get_wallets(self,
                    aptos_wallets_file_data=None,
                    evm_addresses_file_data=None) -> Union[List[WalletData], None]:
        if not aptos_wallets_file_data:
            aptos_wallets_data = self.read_data_from_txt_file(APTOS_WALLETS_FILE)
            evm_addresses_data = self.read_data_from_txt_file(EVM_ADDRESSES_FILE)
        else:
            aptos_wallets_data = aptos_wallets_file_data
            evm_addresses_data = evm_addresses_file_data

        if not aptos_wallets_data:
            return None

        all_evm_addresses = []
        if evm_addresses_data:
            all_evm_addresses = [evm_address for evm_address in evm_addresses_data if len(evm_address) == 42]

        all_wallets = []
        for index, wallet in enumerate(aptos_wallets_data):
            evm_pair_address = all_evm_addresses[index] if len(all_evm_addresses) > index else None
            if len(wallet) == self.wallet_length:
                wallet_data = WalletData(wallet=wallet,
                                         evm_pair_address=evm_pair_address)
                all_wallets.append(wallet_data)

            if len(wallet) > self.wallet_length:
                try:
                    split_wallet = wallet.split(":")
                    if len(split_wallet[0]) != self.wallet_length:
                        continue

                    if len(split_wallet) == 3:
                        proxy_data = ProxyData(host=split_wallet[1],
                                               port=split_wallet[2])
                        wallet_data = WalletData(wallet=split_wallet[0],
                                                 proxy=proxy_data,
                                                 evm_pair_address=evm_pair_address)
                        all_wallets.append(wallet_data)

                    if len(split_wallet) == 5:
                        proxy_data = ProxyData(host=split_wallet[1],
                                               port=split_wallet[2],
                                               username=split_wallet[3],
                                               password=split_wallet[4],
                                               auth=True)
                        wallet_data = WalletData(wallet=split_wallet[0],
                                                 proxy=proxy_data,
                                                 evm_pair_address=evm_pair_address)
                        all_wallets.append(wallet_data)

                except Exception as e:
                    print(e)
                    return None

        return all_wallets
