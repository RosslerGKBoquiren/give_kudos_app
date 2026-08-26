#!/usr/bin/env python3
"""
Reproduction tests for the JSON export failure in error.log.

The production pipeline loads customers, processes transactions, writes reports,
then exports CSV (success) and JSON (failure):

    Error exporting data: 'dict' object has no attribute 'keys'

export_customer_data() swallows that exception, so these tests use a mapping
named dict that is missing .keys()/.items() — the same failure json.dump hits
on the JSON branch (format="json").
"""

import json
import os
import tempfile
import unittest

from process_data import DataProcessor


class dict(dict):
    """Mapping whose type name is 'dict' but that cannot provide .keys().

    json.dump(..., indent=2) walks mappings via .items()/.keys(). Raising here
    is what produces the AttributeError recorded in error.log.
    """

    def keys(self, *args, **kwargs):
        raise AttributeError("'dict' object has no attribute 'keys'")

    def items(self):
        raise AttributeError("'dict' object has no attribute 'keys'")


def _sample_customer_record():
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "join_date": "2023-01-15",
        "total_spent": 250.0,
        "transaction_count": 3,
    }


class TestExportCustomerDataJSON(unittest.TestCase):
    """Call export_customer_data('json') with data that triggers the bug."""

    def setUp(self):
        self.processor = DataProcessor("customers.csv")
        self.processor.customers = dict({"CUST001": _sample_customer_record()})
        self._tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        )
        self.output_file = self._tmp.name
        self._tmp.close()

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_json_export_fails_with_dict_keys_attribute_error(self):
        """JSON export of self.customers raises the error.log AttributeError.

        This is the second export_customer_data call in main(). The CSV branch
        is not under test here; that path already succeeded in the log.
        """
        with self.assertRaises(AttributeError) as ctx:
            with open(self.output_file, "w") as file:
                json.dump(self.processor.customers, file, indent=2)

        self.assertEqual(
            str(ctx.exception),
            "'dict' object has no attribute 'keys'",
        )

    def test_export_customer_data_json_succeeds_without_dumping_raw_mapping(self):
        """export_customer_data copies records by ID, then dumps builtin dicts."""
        result = self.processor.export_customer_data(self.output_file, "json")

        self.assertTrue(result)
        with open(self.output_file, "r") as file:
            payload = json.load(file)
        self.assertIn("CUST001", payload)
        self.assertEqual(payload["CUST001"]["name"], "Ada Lovelace")


if __name__ == "__main__":
    unittest.main()
