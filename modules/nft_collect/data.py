query = """
    query getOwnedTokens($whereCondition: current_token_ownerships_v2_bool_exp!, $offset: Int, $limit: Int, $orderBy: [current_token_ownerships_v2_order_by!]) {
      current_token_ownerships_v2(
        where: $whereCondition,
        offset: $offset,
        limit: $limit,
        order_by: $orderBy
      ) {
        token_standard
        token_properties_mutated_v1
        token_data_id
        table_type_v1
        storage_id
        property_version_v1
        owner_address
        last_transaction_version
        last_transaction_timestamp
        is_soulbound_v2
        is_fungible_v2
        amount
        current_token_data {
          collection_id
          description
          is_fungible_v2
          largest_property_version_v1
          last_transaction_timestamp
          last_transaction_version
          maximum
          supply
          token_data_id
          token_name
          token_properties
          token_standard
          token_uri
          current_collection {
            collection_id
            collection_name
            creator_address
            current_supply
            description
            last_transaction_timestamp
            last_transaction_version
            max_supply
            mutable_description
            mutable_uri
            table_handle_v1
            token_standard
            total_minted_v2
            uri
          }
        }
      }
    }
    """


def get_vars(wallet_address: str) -> dict:

    variables = {
        "whereCondition": {
            "owner_address": {"_eq": wallet_address},
            "amount": {"_gt": 0}
        },
        "offset": 0,
        "limit": 20,
        "orderBy": [
            {"last_transaction_version": "desc"},
            {"token_data_id": "desc"}
        ]
    }

    return variables