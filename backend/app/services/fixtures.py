from typing import Dict, Any

FIXTURES: Dict[str, Dict[str, Any]] = {
    "valid_single_field": {
        "user_input": "My brother James Smith is my executor.",
        "expected_updates": {
            "executor": {
                "name": "James Smith",
                "relationship": "brother"
            }
        },
        "ambiguities": [],
        "response": "I have appointed your brother, James Smith, as your executor."
    },
    "valid_multi_field": {
        "user_input": "I am Jane Doe living at 10 Downing St, London. I want worldwide coverage and I don't have children.",
        "expected_updates": {
            "full_name": "Jane Doe",
            "home_address": "10 Downing St, London",
            "covers_worldwide_assets": True,
            "has_children": False,
            "children": []
        },
        "ambiguities": [],
        "response": "Thank you, Jane Doe. I have recorded your address (10 Downing St, London), worldwide asset coverage, and noted that you have no children."
    },
    "ambiguous_executor_missing_name": {
        "user_input": "I want to appoint my brother as executor.",
        "expected_updates": {
            "executor": {
                "name": None,
                "relationship": "brother"
            }
        },
        "ambiguities": [
            "Executor name is missing (only relationship 'brother' provided)."
        ],
        "response": "Understood, you would like to appoint your brother. Could you please provide his full legal name?"
    },
    "ambiguous_worldwide_scope": {
        "user_input": "I own some property abroad but I'm not sure.",
        "expected_updates": {},
        "ambiguities": [
            "Asset coverage scope is unclear (overseas property mentioned without explicit decision)."
        ],
        "response": "Since you mentioned having property abroad, would you like this Personal Wishes Document to cover all your worldwide assets, or strictly domestic assets?"
    },
    "correction_executor": {
        "user_input": "Actually, change my executor to my sister Sarah Jenkins.",
        "expected_updates": {
            "executor": {
                "name": "Sarah Jenkins",
                "relationship": "sister"
            }
        },
        "ambiguities": [],
        "response": "I have updated your executor to your sister, Sarah Jenkins."
    },
    "correction_children": {
        "user_input": "Actually, I don't have any children.",
        "expected_updates": {
            "has_children": False,
            "children": []
        },
        "ambiguities": [],
        "response": "I have updated your details to reflect that you do not have children."
    },
    "malformed_raw_payload": {
        # Raw string simulating a malformed LLM response (e.g. JSON truncation or schema violation)
        "raw_json": '{"assistant_message": "Broken JSON missing closing braces',
        "corrupted_schema": {
            "full_name": 12345,  # Invalid type: integer instead of string
            "covers_worldwide_assets": "MAYBE_OR_MAYBE_NOT",  # Invalid type: string instead of bool
            "executor": "James"  # Invalid type: string instead of object
        }
    }
}
