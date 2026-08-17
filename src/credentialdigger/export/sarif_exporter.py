"""
SARIF Exporter for Credential Digger
Converts Credential Digger discoveries into SARIF v2.1.0 format.
Schema URL: https://json.schemastore.org/sarif-2.1.0.json
"""

import json


def export_to_sarif(discoveries, rules=None):
    """ Transforms Credential Digger discoveries into a SARIF v2.1.0 JSON dictionary.

    Parameters
    ----------
    discoveries: list of dict
        List of discovery dictionaries.
    rules: list of dict, optional
        List of rule dictionaries. If provided, rule details will be added to driver.rules.

    Returns
    -------
    dict
        SARIF v2.1.0 compliant dictionary.
    """
    sarif_rules = []
    rules_index_map = {}

    if rules:
        for idx, r in enumerate(rules):
            rule_id = str(r.get('id', ''))
            rules_index_map[rule_id] = idx
            sarif_rules.append({
                "id": rule_id,
                "shortDescription": {
                    "text": r.get('description') or f"Rule {rule_id}"
                },
                "fullDescription": {
                    "text": r.get('description') or f"Regex category: {r.get('category', '')}"
                },
                "properties": {
                    "category": r.get('category', ''),
                    "regex": r.get('regex', '')
                }
            })

    results = []
    for d in discoveries:
        rule_id = str(d.get('rule_id', ''))
        message_text = f"Credential Digger detected a potential secret matching rule '{rule_id}'."
        snippet_text = d.get('snippet', '')
        file_name = d.get('file_name', '')
        line_number = d.get('line_number', 1)
        if line_number is None or line_number < 1:
            line_number = 1

        result_obj = {
            "ruleId": rule_id,
            "message": {
                "text": message_text
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_name
                        },
                        "region": {
                            "startLine": line_number,
                            "snippet": {
                                "text": snippet_text
                            }
                        }
                    }
                }
            ],
            "properties": {
                "state": d.get('state', 'new'),
                "commit_id": d.get('commit_id', '')
            }
        }

        if rule_id in rules_index_map:
            result_obj["ruleIndex"] = rules_index_map[rule_id]

        results.append(result_obj)

    sarif_doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Credential Digger",
                        "informationUri": "https://github.com/SAP/credential-digger",
                        "rules": sarif_rules
                    }
                },
                "results": results
            }
        ]
    }

    return sarif_doc
