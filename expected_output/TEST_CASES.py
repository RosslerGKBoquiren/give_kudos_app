#!/usr/bin/env python3
"""
Unit Tests for Data Processing Script
Tests the DataProcessor class functionality and bug fixes.
"""

import unittest
import tempfile
import os
import json
import csv
from process_data_final import DataProcessor


class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create test customer data
        self.customers_file = os.path.join(self.temp_dir, "test_customers.csv")
        with open(self.customers_file, "w", newline="") as f:
            f.write("customer_id,name,email,join_date\n")
            f.write("C001,John Smith,john.smith@email.com,2023-01-15\n")
            f.write("C002,Jane Doe,jane.doe@email.com,2023-02-20\n")
            f.write("C003,Bob Johnson,bob.johnson@email.com,2023-03-10\n")

        # Create test transaction data
        self.transactions_file = os.path.join(self.temp_dir, "test_transactions.csv")
        with open(self.transactions_file, "w", newline="") as f:
            f.write("transaction_id,customer_id,amount,date,category\n")
            f.write("T001,C001,150.50,2024-01-10,electronics\n")
            f.write("T002,C002,75.25,2024-01-11,clothing\n")
            f.write("T003,C001,200.00,2024-01-12,electronics\n")
            f.write("T004,C003,45.75,2024-01-13,food\n")
            f.write("T005,C002,120.00,2024-01-14,clothing\n")

        # Initialize processor
        self.processor = DataProcessor(self.customers_file)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_load_data_success(self):
        """Test successful data loading."""
        result = self.processor.load_data()
        self.assertTrue(result)
        self.assertEqual(len(self.processor.customers), 3)
        self.assertIn("C001", self.processor.customers)
        self.assertEqual(self.processor.customers["C001"]["name"], "John Smith")

    def test_load_data_file_not_found(self):
        """Test data loading with non-existent file."""
        processor = DataProcessor("nonexistent.csv")
        result = processor.load_data()
        self.assertFalse(result)

    def test_process_transactions_success(self):
        """Test successful transaction processing."""
        self.processor.load_data()
        result = self.processor.process_transactions(self.transactions_file)

        self.assertTrue(result)
        self.assertEqual(len(self.processor.transactions), 5)

        # Check customer totals updated correctly
        self.assertEqual(self.processor.customers["C001"]["total_spent"], 350.50)
        self.assertEqual(self.processor.customers["C001"]["transaction_count"], 2)
        self.assertEqual(self.processor.customers["C002"]["total_spent"], 195.25)
        self.assertEqual(self.processor.customers["C002"]["transaction_count"], 2)

    def test_process_transactions_file_not_found(self):
        """Test transaction processing with non-existent file."""
        self.processor.load_data()
        result = self.processor.process_transactions("nonexistent.csv")
        self.assertFalse(result)

    def test_calculate_customer_metrics(self):
        """Test customer metrics calculation."""
        self.processor.load_data()
        self.processor.process_transactions(self.transactions_file)
        metrics = self.processor.calculate_customer_metrics()

        # Check basic metrics
        self.assertEqual(metrics["total_customers"], 3)
        self.assertEqual(metrics["total_transactions"], 5)
        self.assertEqual(metrics["total_revenue"], 545.75)
        self.assertEqual(metrics["average_transaction_value"], 109.15)

        # Check top customers
        self.assertEqual(len(metrics["top_customers"]), 3)
        self.assertEqual(
            metrics["top_customers"][0][0], "C001"
        )  # John Smith has highest total

        # Check category breakdown
        expected_categories = {"electronics": 2, "clothing": 2, "food": 1}
        self.assertEqual(metrics["category_breakdown"], expected_categories)

    def test_calculate_metrics_no_data(self):
        """Test metrics calculation with no customer data."""
        metrics = self.processor.calculate_customer_metrics()
        self.assertEqual(metrics, {})

    def test_find_matches_by_name(self):
        """Test customer search by name."""
        self.processor.load_data()
        matches = self.processor.find_matches("john", "name")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["customer_id"], "C001")
        self.assertEqual(matches[0]["name"], "John Smith")

    def test_find_matches_by_email(self):
        """Test customer search by email."""
        self.processor.load_data()
        matches = self.processor.find_matches("jane.doe", "email")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["customer_id"], "C002")
        self.assertEqual(matches[0]["email"], "jane.doe@email.com")

    def test_find_matches_no_results(self):
        """Test customer search with no matches."""
        self.processor.load_data()
        matches = self.processor.find_matches("nonexistent", "name")
        self.assertEqual(len(matches), 0)

    def test_find_matches_empty_search_term(self):
        """Test customer search with empty search term."""
        self.processor.load_data()
        matches = self.processor.find_matches("", "name")
        self.assertEqual(len(matches), 0)

    def test_find_matches_case_insensitive(self):
        """Test that search is case insensitive."""
        self.processor.load_data()
        matches = self.processor.find_matches("JANE", "name")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["customer_id"], "C002")

    def test_generate_report_customer_summary(self):
        """Test customer summary report generation."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "customer_summary.json")
        result = self.processor.generate_report("customer_summary", output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check report content
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIn("generated_at", data)
            self.assertIn("customers", data)
            self.assertEqual(len(data["customers"]), 3)

    def test_generate_report_metrics(self):
        """Test metrics report generation."""
        self.processor.load_data()
        self.processor.process_transactions(self.transactions_file)
        output_file = os.path.join(self.temp_dir, "metrics.json")
        result = self.processor.generate_report("metrics", output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check report content
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIn("generated_at", data)
            self.assertIn("metrics", data)
            self.assertEqual(data["metrics"]["total_customers"], 3)

    def test_generate_report_transactions(self):
        """Test transactions report generation."""
        self.processor.load_data()
        self.processor.process_transactions(self.transactions_file)
        output_file = os.path.join(self.temp_dir, "transactions.json")
        result = self.processor.generate_report("transactions", output_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check report content
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIn("generated_at", data)
            self.assertIn("transactions", data)
            self.assertEqual(len(data["transactions"]), 5)

    def test_generate_report_unknown_type(self):
        """Test report generation with unknown report type."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "unknown.json")
        result = self.processor.generate_report("unknown", output_file)
        self.assertFalse(result)

    def test_export_customer_data_csv(self):
        """Test CSV export functionality."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "customers_export.csv")
        result = self.processor.export_customer_data(output_file, "csv")

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check CSV content
        with open(output_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)

            # Check first row
            first_row = rows[0]
            self.assertEqual(first_row["customer_id"], "C001")
            self.assertEqual(first_row["name"], "John Smith")
            self.assertEqual(first_row["email"], "john.smith@email.com")

    def test_export_customer_data_json(self):
        """Test JSON export functionality."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "customers_export.json")
        result = self.processor.export_customer_data(output_file, "json")

        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

        # Check JSON content
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 3)
            self.assertIn("C001", data)
            self.assertEqual(data["C001"]["name"], "John Smith")

    def test_export_customer_data_unsupported_format(self):
        """Test export with unsupported format."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "customers_export.xml")
        result = self.processor.export_customer_data(output_file, "xml")
        self.assertFalse(result)

    def test_export_customer_data_no_customers(self):
        """Test export when no customers are loaded."""
        output_file = os.path.join(self.temp_dir, "customers_export.csv")
        result = self.processor.export_customer_data(output_file, "csv")
        self.assertFalse(result)

    def test_bug_fix_export_customer_data_json(self):
        """Test that the original bug is fixed - JSON export should work without errors."""
        self.processor.load_data()
        output_file = os.path.join(self.temp_dir, "customers_export.json")

        # This should not raise the "'dict' object has no attribute 'keys'" error
        result = self.processor.export_customer_data(output_file, "json")
        self.assertTrue(result)

        # Verify the file was created and contains valid JSON
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIsInstance(data, dict)
            self.assertEqual(len(data), 3)


class TestDataProcessorPerformance(unittest.TestCase):
    """Test cases for performance optimizations."""

    def setUp(self):
        """Set up test fixtures for performance tests."""
        self.temp_dir = tempfile.mkdtemp()

        # Create larger test dataset
        self.customers_file = os.path.join(self.temp_dir, "test_customers.csv")
        with open(self.customers_file, "w", newline="") as f:
            f.write("customer_id,name,email,join_date\n")
            for i in range(100):
                f.write(
                    f"C{i:03d},Customer {i},customer{i}@email.com,2023-01-{i+1:02d}\n"
                )

        self.transactions_file = os.path.join(self.temp_dir, "test_transactions.csv")
        with open(self.transactions_file, "w", newline="") as f:
            f.write("transaction_id,customer_id,amount,date,category\n")
            for i in range(500):
                customer_id = f"C{i % 100:03d}"
                category = ["electronics", "clothing", "food", "books"][i % 4]
                f.write(
                    f"T{i:03d},{customer_id},{100 + i},{2024}-01-{i % 28 + 1:02d},{category}\n"
                )

        self.processor = DataProcessor(self.customers_file)
        self.processor.load_data()
        self.processor.process_transactions(self.transactions_file)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_find_matches_performance(self):
        """Test that find_matches performs efficiently with larger datasets."""
        import time

        # Test search performance
        start_time = time.time()
        matches = self.processor.find_matches("customer", "name")
        end_time = time.time()

        # Should find all 100 customers
        self.assertEqual(len(matches), 100)

        # Should complete quickly (less than 1 second for 100 customers)
        execution_time = end_time - start_time
        self.assertLess(
            execution_time, 1.0, f"Search took {execution_time:.3f} seconds"
        )

    def test_calculate_metrics_performance(self):
        """Test that calculate_customer_metrics performs efficiently."""
        import time

        start_time = time.time()
        metrics = self.processor.calculate_customer_metrics()
        end_time = time.time()

        # Should complete quickly
        execution_time = end_time - start_time
        self.assertLess(
            execution_time,
            1.0,
            f"Metrics calculation took {execution_time:.3f} seconds",
        )

        # Verify metrics are correct
        self.assertEqual(metrics["total_customers"], 100)
        self.assertEqual(metrics["total_transactions"], 500)
        self.assertEqual(len(metrics["top_customers"]), 10)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
