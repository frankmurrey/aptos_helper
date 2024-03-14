WEIGHTED_POOL_SCRIPTS_ABI = {
    "address": "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af",
    "name": "weighted_pool_scripts",
    "friends": [],
    "exposed_functions": [
        {
            "name": "add_liquidity",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(8)],
            "params": ["&signer", "u64", "u64", "u64", "u64", "u64", "u64", "u64", "u64"],
            "return": [],
        },
        {
            "name": "remove_liquidity",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(8)],
            "params": ["&signer", "u64", "u64", "u64", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_in",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(12)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_out",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(12)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        }
    ],
    "structs": []
}

STABLE_POOL_SCRIPTS_ABI = {
    "address": "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af",
    "name": "stable_pool_scripts",
    "friends": [],
    "exposed_functions": [
        {
            "name": "add_liquidity",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(4)],
            "params": ["&signer", "u64", "u64", "u64", "u64"],
            "return": [],
        },
        {
            "name": "remove_liquidity",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(4)],
            "params": ["&signer", "u64", "u64", "u64", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_in",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(6)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_out",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(6)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        }
    ],
    "structs": []
}

MULTIHOP_ROUTER_ABI = {
    "address": "0x60955b957956d79bc80b096d3e41bad525dd400d8ce957cdeb05719ed1e4fc26",
    "name": "router",
    "friends": [],
    "exposed_functions": [
        {
            "name": "swap_exact_in_2",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(19)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_in_3",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(29)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_out_2",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(19)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        },
        {
            "name": "swap_exact_out_3",
            "visibility": "public",
            "is_entry": True,
            "is_view": False,
            "generic_type_params": [{} for _ in range(29)],
            "params": ["&signer", "u64", "u64"],
            "return": [],
        }
    ],
    "structs": []
}

