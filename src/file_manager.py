import os
import json
import csv

from typing import Union, List

from src.paths import (APTOS_WALLETS_FILE,
                       EVM_ADDRESSES_FILE,
                       PROXY_FILE)
from src.schemas.wallet_data import (WalletData,
                                     ProxyData)


class FileManager:
    APTOS_KEY_LENGTH = 66
    EVM_ADDRESS_LENGTH = 42

    def read_data_from_txt_file(self, file_path) -> Union[list, None]:
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as file:
            data = file.read().splitlines()
            return data

    def read_data_from_json_file(self, file_path) -> Union[list, dict, None]:
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

    def write_data_to_csv(self,
                          path,
                          file_name,
                          data: list):
        if not os.path.exists(path):
            return

        file_path = f"{path}\\{file_name}"
        with open(file_path, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    def _extract_valid_proxy_data_from_str(self, proxy_data: str) -> Union[List[ProxyData], None]:
        if not proxy_data:
            return None

        if proxy_data == "##":
            return None

        try:
            if proxy_data.startswith('m$'):
                is_mobile = True
                proxy_data = proxy_data[2:]
            else:
                is_mobile = False

            proxy_data = proxy_data.split(":")
            if len(proxy_data) == 2:
                host, port = proxy_data
                proxy_data = ProxyData(host=host,
                                       port=port,
                                       is_mobile=is_mobile)

            elif len(proxy_data) == 4:
                host, port, username, password = proxy_data
                proxy_data = ProxyData(host=host,
                                       port=port,
                                       username=username,
                                       password=password,
                                       auth=True,
                                       is_mobile=is_mobile)

            else:
                proxy_data = None

            return proxy_data
        except Exception as e:
            return None

    def get_wallets(self,
                    aptos_wallets_data=None,
                    evm_addresses_data=None,
                    proxy_data=None) -> Union[List[WalletData], None]:

        if not aptos_wallets_data:
            return None
        all_evm_addresses = []
        if evm_addresses_data:
            all_evm_addresses = [addr for addr in evm_addresses_data if len(addr) == self.EVM_ADDRESS_LENGTH]

        all_proxy_data = []
        if proxy_data:
            all_proxy_data = [proxy for proxy in proxy_data]

        all_wallets = []
        for index, wallet in enumerate(aptos_wallets_data):
            evm_pair_address = all_evm_addresses[index] if len(all_evm_addresses) > index else None
            paired_proxy_data = all_proxy_data[index] if len(all_proxy_data) > index else None
            if len(wallet) != self.APTOS_KEY_LENGTH:
                continue
            proxy_data = self._extract_valid_proxy_data_from_str(paired_proxy_data)
            wallet_data = WalletData(wallet=wallet,
                                     evm_pair_address=evm_pair_address,
                                     proxy=proxy_data)
            all_wallets.append(wallet_data)
        print(all_wallets)
        return all_wallets

    def get_wallets_from_files(self):
        aptos_wallets_data = self.read_data_from_txt_file(APTOS_WALLETS_FILE)
        evm_addresses_data = self.read_data_from_txt_file(EVM_ADDRESSES_FILE)
        proxy_data = self.read_data_from_txt_file(PROXY_FILE)
        return self.get_wallets(aptos_wallets_data=aptos_wallets_data,
                                evm_addresses_data=evm_addresses_data,
                                proxy_data=proxy_data)
