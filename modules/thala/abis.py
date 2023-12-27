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

