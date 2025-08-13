#!/usr/bin/env python3
"""
Unit tests for North Sussex Judo Training Fee Calculator

Test coverage includes:
- Configuration validation
- Athlete creation and validation
- Fee calculations
- Utility functions
- Error handling

Run with: python -m pytest test_judo_calculator.py -v
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch

# Import modules under test
from north_sussex_judo import (
        TrainingConfig, Athlete, format_currency, 
        validate_number_input, generate_fee_report, JudoManagementSystem
    )



class TestTrainingConfig(unittest.TestCase):
    """Test configuration constants and structure."""
    
    def test_training_plans_exist(self):
        """Verify all required training plans are defined."""
        expected_plans = ['Beginner', 'Intermediate', 'Elite']
        for plan in expected_plans:
            self.assertIn(plan, TrainingConfig.TRAINING_PLANS)
    
    def test_training_plan_structure(self):
        """Ensure training plans have correct structure."""
        for plan_name, details in TrainingConfig.TRAINING_PLANS.items():
            self.assertIn('sessions_per_week', details)
            self.assertIn('weekly_fee', details)
            self.assertIsInstance(details['sessions_per_week'], int)
            self.assertIsInstance(details['weekly_fee'], float)
            self.assertGreater(details['sessions_per_week'], 0)
            self.assertGreater(details['weekly_fee'], 0)
    
    def test_weight_categories_ordering(self):
        """Test weight categories are properly ordered."""
        categories = list(TrainingConfig.WEIGHT_CATEGORIES.items())
        
        # Check that limits are ascending (except Heavyweight)
        for i in range(len(categories) - 2):
            self.assertLess(categories[i][1], categories[i+1][1])
        
        # Heavyweight should be infinite
        self.assertEqual(categories[-1][0], 'Heavyweight')
        self.assertEqual(categories[-1][1], float('inf'))
    
    def test_constants_values(self):
        """Verify configuration constants."""
        self.assertEqual(TrainingConfig.PRIVATE_COACHING_RATE, 9.50)
        self.assertEqual(TrainingConfig.COMPETITION_ENTRY_FEE, 22.00)
        self.assertEqual(TrainingConfig.MAX_PRIVATE_COACHING_HOURS, 5)
        self.assertEqual(TrainingConfig.WEEKS_PER_MONTH, 4)


class TestAthlete(unittest.TestCase):
    """Test Athlete class functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'name': 'John Doe',
            'training_plan': 'Intermediate',
            'current_weight': 75.0,
            'competitions': 2,
            'private_coaching_hours': 3
        }
    
    def test_valid_athlete_creation(self):
        """Test creating athlete with valid data."""
        athlete = Athlete(**self.valid_data)
        
        self.assertEqual(athlete.name, 'John Doe')
        self.assertEqual(athlete.training_plan, 'Intermediate')
        self.assertEqual(athlete.current_weight, 75.0)
        self.assertEqual(athlete.competitions, 2)
        self.assertEqual(athlete.private_coaching_hours, 3)
        self.assertEqual(athlete.weight_category, 'Light-Middleweight')
    
    def test_name_validation(self):
        """Test name validation rules."""
        test_cases = [
            ('', ValueError),           # Empty name
            ('   ', ValueError),        # Whitespace only
            ('  John  ', None),         # Valid with whitespace (should trim)
        ]
        
        for name, expected_error in test_cases:
            data = self.valid_data.copy()
            data['name'] = name
            
            if expected_error:
                with self.assertRaises(expected_error):
                    Athlete(**data)
            else:
                athlete = Athlete(**data)
                self.assertEqual(athlete.name.strip(), name.strip())
    
    def test_training_plan_validation(self):
        """Test training plan validation."""
        # Invalid plan
        data = self.valid_data.copy()
        data['training_plan'] = 'InvalidPlan'
        with self.assertRaises(ValueError):
            Athlete(**data)
        
        # Valid plans - adjust competitions for each plan type
        for plan in TrainingConfig.TRAINING_PLANS.keys():
            data = self.valid_data.copy()
            data['training_plan'] = plan
            # Beginners cannot have competitions
            if plan == 'Beginner':
                data['competitions'] = 0
            athlete = Athlete(**data)
            self.assertEqual(athlete.training_plan, plan)
    
    def test_weight_validation(self):
        """Test weight validation boundaries."""
        test_cases = [
            (0, ValueError),            # Zero weight
            (-5.0, ValueError),         # Negative weight  
            (250.0, ValueError),        # Unrealistic weight
            (75.0, None),               # Valid weight
        ]
        
        for weight, expected_error in test_cases:
            data = self.valid_data.copy()
            data['current_weight'] = weight
            
            if expected_error:
                with self.assertRaises(expected_error):
                    Athlete(**data)
            else:
                athlete = Athlete(**data)
                self.assertEqual(athlete.current_weight, weight)
    
    def test_competition_validation(self):
        """Test competition entry validation."""
        # Beginner cannot compete
        data = self.valid_data.copy()
        data['training_plan'] = 'Beginner'
        data['competitions'] = 1
        with self.assertRaises(ValueError):
            Athlete(**data)
        
        # Too many competitions
        data = self.valid_data.copy()
        data['competitions'] = 5
        with self.assertRaises(ValueError):
            Athlete(**data)
        
        # Negative competitions
        data = self.valid_data.copy()
        data['competitions'] = -1
        with self.assertRaises(ValueError):
            Athlete(**data)
    
    def test_coaching_hours_validation(self):
        """Test private coaching validation."""
        test_cases = [
            (-1, ValueError),           # Negative hours
            (6, ValueError),            # Too many hours
            (3, None),                  # Valid hours
        ]
        
        for hours, expected_error in test_cases:
            data = self.valid_data.copy()
            data['private_coaching_hours'] = hours
            
            if expected_error:
                with self.assertRaises(expected_error):
                    Athlete(**data)
            else:
                athlete = Athlete(**data)
                self.assertEqual(athlete.private_coaching_hours, hours)
    
    def test_weight_category_assignment(self):
        """Test weight category determination."""
        test_weights = [
            (65.0, 'Flyweight'),
            (66.0, 'Flyweight'),
            (70.0, 'Lightweight'),
            (73.0, 'Lightweight'),
            (80.0, 'Light-Middleweight'),
            (90.0, 'Middleweight'),
            (100.0, 'Light-Heavyweight'),
            (105.0, 'Heavyweight')
        ]
        
        for weight, expected_category in test_weights:
            data = self.valid_data.copy()
            data['current_weight'] = weight
            athlete = Athlete(**data)
            self.assertEqual(athlete.weight_category, expected_category)
    
    def test_fee_calculation(self):
        """Test monthly fee calculation accuracy."""
        athlete = Athlete('Test', 'Intermediate', 75.0, 
                         competitions=2, private_coaching_hours=3)
        fees = athlete.calculate_monthly_fees()
        
        # Expected calculations
        expected_training = 30.00 * 4       # £30/week * 4 weeks
        expected_coaching = 3 * 4 * 9.50    # 3h/week * 4 weeks * £9.50/h
        expected_competition = 2 * 22.00    # 2 competitions * £22 each
        expected_total = expected_training + expected_coaching + expected_competition
        
        self.assertEqual(fees['training_cost'], expected_training)
        self.assertEqual(fees['coaching_cost'], expected_coaching)
        self.assertEqual(fees['competition_cost'], expected_competition)
        self.assertEqual(fees['total_cost'], expected_total)
    
    def test_weight_analysis(self):
        """Test weight analysis output."""
        # Test heavyweight
        athlete = Athlete('Test', 'Elite', 105.0)
        analysis = athlete.get_weight_analysis()
        self.assertIn('Heavyweight', analysis)
        self.assertIn('no upper limit', analysis)
        
        # Test close to limit
        athlete = Athlete('Test', 'Elite', 88.5)  # Close to 90kg middleweight
        analysis = athlete.get_weight_analysis()
        self.assertIn('Close to', analysis)
        
        
class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        test_cases = [
            (100.0, '£100.00'),
            (99.99, '£99.99'),
            (0, '£0.00'),
            (1234.567, '£1234.57')
        ]
        
        for amount, expected in test_cases:
            self.assertEqual(format_currency(amount), expected)
    
    def test_validate_number_input(self):
        """Test number input validation."""
        # Valid input
        result = validate_number_input('75.5', 'Weight')
        self.assertEqual(result, 75.5)
        
        # Invalid input
        with self.assertRaises(ValueError):
            validate_number_input('not_a_number', 'Weight')
        
        # Below minimum
        with self.assertRaises(ValueError):
            validate_number_input('5', 'Weight', min_val=10)
        
        # Above maximum
        with self.assertRaises(ValueError):
            validate_number_input('15', 'Weight', max_val=10)
    
    def test_generate_fee_report(self):
        """Test report generation."""
        athlete = Athlete('John Doe', 'Elite', 80.0, competitions=3, 
                         private_coaching_hours=4)
        report = generate_fee_report(athlete)
        
        # Check report contains expected elements
        self.assertIn('JOHN DOE', report)
        self.assertIn('Elite', report)
        self.assertIn('TOTAL MONTHLY FEE', report)
        self.assertIn('£', report)
        self.assertIn('80.0kg', report)


class TestJudoManagementSystem(unittest.TestCase):
    """Test GUI application logic."""
    
    def setUp(self):
        """Set up test GUI."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during testing
    
    def tearDown(self):
        """Clean up GUI."""
        self.root.destroy()
    
    @patch('tkinter.messagebox.showinfo')
    def test_system_initialization(self, mock_showinfo):
        """Test system initializes with sample data."""
        system = JudoManagementSystem(self.root)
        
        # Should have sample athletes loaded
        self.assertGreater(len(system.athletes), 0)
        
        # Check first athlete
        first_athlete = system.athletes[0]
        self.assertIsInstance(first_athlete, Athlete)
        self.assertTrue(first_athlete.name)
    
    def test_athlete_registration_validation(self):
        """Test athlete registration validation."""
        system = JudoManagementSystem(self.root)
        initial_count = len(system.athletes)
        
        # Set up form with valid data
        system.name_field.insert(0, 'Test Athlete')
        system.plan_var.set('Intermediate')
        system.weight_field.insert(0, '75.0')
        system.competitions_field.delete(0, tk.END)
        system.competitions_field.insert(0, '2')
        system.coaching_field.delete(0, tk.END)
        system.coaching_field.insert(0, '1')
        
        # Mock messagebox to prevent actual dialog
        with patch('tkinter.messagebox.showinfo'):
            system.register_athlete()
        
        # Should have one more athlete
        self.assertEqual(len(system.athletes), initial_count + 1)
        
        # Check the new athlete
        new_athlete = system.athletes[-1]
        self.assertEqual(new_athlete.name, 'Test Athlete')
    
    def test_duplicate_name_prevention(self):
        """Test duplicate athlete names are rejected."""
        system = JudoManagementSystem(self.root)
        existing_name = system.athletes[0].name
        
        # Try to register with existing name
        system.name_field.insert(0, existing_name)
        system.plan_var.set('Beginner')
        system.weight_field.insert(0, '70.0')
        
        with patch('tkinter.messagebox.showerror') as mock_error:
            system.register_athlete()
            mock_error.assert_called_once()
    
    def test_clear_form_functionality(self):
        """Test form clearing works correctly."""
        system = JudoManagementSystem(self.root)
        
        # Fill form
        system.name_field.insert(0, 'Test')
        system.weight_field.insert(0, '75')
        system.plan_var.set('Elite')
        
        # Clear form
        system.clear_registration_form()
        
        # Check fields are cleared
        self.assertEqual(system.name_field.get(), '')
        self.assertEqual(system.weight_field.get(), '')
        self.assertEqual(system.plan_var.get(), 'Beginner')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_minimum_weight_boundary(self):
        """Test weight at minimum boundary."""
        athlete = Athlete('Test', 'Beginner', 66.0)  # Exactly at flyweight limit
        self.assertEqual(athlete.weight_category, 'Flyweight')
    
    def test_maximum_competitions_intermediate(self):
        """Test maximum competitions for intermediate athlete."""
        athlete = Athlete('Test', 'Intermediate', 75.0, competitions=4)
        fees = athlete.calculate_monthly_fees()
        self.assertEqual(fees['competition_cost'], 4 * 22.00)
    
    def test_zero_optional_services(self):
        """Test athlete with no optional services."""
        athlete = Athlete('Test', 'Beginner', 75.0)
        fees = athlete.calculate_monthly_fees()
        
        self.assertEqual(fees['coaching_cost'], 0)
        self.assertEqual(fees['competition_cost'], 0)
        self.assertEqual(fees['total_cost'], fees['training_cost'])
    
    def test_maximum_coaching_hours(self):
        """Test maximum coaching hours boundary."""
        athlete = Athlete('Test', 'Elite', 75.0, 
                         private_coaching_hours=5)  # Maximum allowed
        fees = athlete.calculate_monthly_fees()
        expected_coaching = 5 * 4 * 9.50
        self.assertEqual(fees['coaching_cost'], expected_coaching)


if __name__ == '__main__':
    # Configure test runner for better output
    unittest.main(verbosity=2, buffer=True)