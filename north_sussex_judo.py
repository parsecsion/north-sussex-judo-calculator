#!/usr/bin/env python3
"""
North Sussex Judo Training Fee Calculator
A comprehensive desktop application for managing judo training fees and athlete information.

License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Dict, List, Optional
import sys


class TrainingConfig:
    """Configuration constants for the judo training facility."""
    
    TRAINING_PLANS = {
        "Beginner": {"sessions_per_week": 2, "weekly_fee": 25.00},
        "Intermediate": {"sessions_per_week": 3, "weekly_fee": 30.00},
        "Elite": {"sessions_per_week": 5, "weekly_fee": 35.00}
    }
    
    WEIGHT_CATEGORIES = {
        "Flyweight": 66,
        "Lightweight": 73,
        "Light-Middleweight": 81,
        "Middleweight": 90,
        "Light-Heavyweight": 100,
        "Heavyweight": float('inf')
    }
    
    PRIVATE_COACHING_RATE = 9.50
    COMPETITION_ENTRY_FEE = 22.00
    MAX_PRIVATE_COACHING_HOURS = 5
    WEEKS_PER_MONTH = 4


class Athlete:
    """
    Represents a judo athlete with training details and fee calculation capabilities.
    """
    
    def __init__(self, name: str, training_plan: str, current_weight: float,
                 competitions: int = 0, private_coaching_hours: int = 0):
        self.name = self._validate_name(name)
        self.training_plan = self._validate_training_plan(training_plan)
        self.current_weight = self._validate_weight(current_weight)
        self.competitions = self._validate_competitions(competitions, training_plan)
        self.private_coaching_hours = self._validate_coaching_hours(private_coaching_hours)
        self.weight_category = self._determine_weight_category()
    
    def _validate_name(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Athlete name cannot be empty")
        return name
    
    def _validate_training_plan(self, plan: str) -> str:
        if plan not in TrainingConfig.TRAINING_PLANS:
            raise ValueError(f"Training plan must be one of: {list(TrainingConfig.TRAINING_PLANS.keys())}")
        return plan
    
    def _validate_weight(self, weight: float) -> float:
        if weight <= 0:
            raise ValueError("Weight must be greater than 0 kg")
        if weight > 200:
            raise ValueError("Weight value seems unrealistic")
        return weight
    
    def _validate_competitions(self, competitions: int, training_plan: str) -> int:
        if competitions < 0:
            raise ValueError("Number of competitions cannot be negative")
        
        if training_plan == "Beginner" and competitions > 0:
            raise ValueError("Beginner athletes cannot enter competitions")
        
        if competitions > 4:
            raise ValueError("Maximum 4 competitions per month allowed")
        
        return competitions
    
    def _validate_coaching_hours(self, hours: int) -> int:
        if hours < 0:
            raise ValueError("Private coaching hours cannot be negative")
        if hours > TrainingConfig.MAX_PRIVATE_COACHING_HOURS:
            raise ValueError(f"Maximum {TrainingConfig.MAX_PRIVATE_COACHING_HOURS} hours of private coaching per week")
        return hours
    
    def _determine_weight_category(self) -> str:
        for category, upper_limit in TrainingConfig.WEIGHT_CATEGORIES.items():
            if self.current_weight <= upper_limit:
                return category
        return "Heavyweight"
    
    def calculate_monthly_fees(self) -> Dict[str, float]:
        """Calculate total monthly fees broken down by component."""
        training_cost = TrainingConfig.TRAINING_PLANS[self.training_plan]["weekly_fee"] * TrainingConfig.WEEKS_PER_MONTH
        coaching_cost = self.private_coaching_hours * TrainingConfig.WEEKS_PER_MONTH * TrainingConfig.PRIVATE_COACHING_RATE
        competition_cost = self.competitions * TrainingConfig.COMPETITION_ENTRY_FEE
        total_cost = training_cost + coaching_cost + competition_cost
        
        return {
            "training_cost": training_cost,
            "coaching_cost": coaching_cost,
            "competition_cost": competition_cost,
            "total_cost": total_cost
        }
    
    def get_weight_analysis(self) -> str:
        """Get detailed weight category analysis for the athlete."""
        category_limit = TrainingConfig.WEIGHT_CATEGORIES[self.weight_category]
        
        if self.weight_category == "Heavyweight":
            return f"Weight: {self.current_weight:.1f}kg - Heavyweight category (no upper limit)"
        
        weight_difference = category_limit - self.current_weight
        
        if weight_difference > 5:
            return f"Weight: {self.current_weight:.1f}kg - Well within {self.weight_category} limit ({category_limit}kg)"
        elif weight_difference > 0:
            return f"Weight: {self.current_weight:.1f}kg - Close to {self.weight_category} limit ({category_limit}kg)"
        else:
            return f"Weight: {self.current_weight:.1f}kg - Over {self.weight_category} limit ({category_limit}kg)"


def format_currency(amount: float) -> str:
    """Format monetary amounts with proper currency symbol."""
    return f"£{amount:.2f}"


def validate_number_input(value: str, field_name: str, min_val: float = 0, max_val: float = float('inf')) -> float:
    """Validate and convert string input to numeric value."""
    try:
        num_val = float(value)
        if num_val < min_val:
            raise ValueError(f"{field_name} must be at least {min_val}")
        if num_val > max_val:
            raise ValueError(f"{field_name} cannot exceed {max_val}")
        return num_val
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"{field_name} must be a valid number")
        raise e


def generate_fee_report(athlete: Athlete) -> str:
    """Generate detailed fee report for an athlete."""
    fees = athlete.calculate_monthly_fees()
    
    report = f"\n{'='*55}\n"
    report += f"MONTHLY FEE REPORT - {athlete.name.upper()}\n"
    report += f"{'='*55}\n\n"
    
    report += f"Training Plan: {athlete.training_plan}\n"
    report += f"Sessions per week: {TrainingConfig.TRAINING_PLANS[athlete.training_plan]['sessions_per_week']}\n\n"
    
    report += "FEE BREAKDOWN:\n"
    report += f"• Training fees (4 weeks): {format_currency(fees['training_cost'])}\n"
    
    if athlete.private_coaching_hours > 0:
        report += f"• Private coaching ({athlete.private_coaching_hours}h/week): {format_currency(fees['coaching_cost'])}\n"
    
    if athlete.competitions > 0:
        report += f"• Competition entries ({athlete.competitions}): {format_currency(fees['competition_cost'])}\n"
    
    report += f"\nTOTAL MONTHLY FEE: {format_currency(fees['total_cost'])}\n\n"
    
    report += f"ATHLETE DETAILS:\n"
    report += f"• {athlete.get_weight_analysis()}\n"
    
    return report


class JudoManagementSystem:
    """Main application class for the judo training fee calculator."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.athletes: List[Athlete] = []
        self.setup_main_window()
        self.create_interface()
        self.load_initial_data()
    
    def setup_main_window(self):
        """Configure the main application window."""
        self.root.title("North Sussex Judo - Training Fee Calculator")
        self.root.geometry("950x720")
        self.root.configure(bg='#34495e')
        
        # Configure styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Header.TLabel', 
                           background='#34495e', 
                           foreground='#ecf0f1', 
                           font=('Arial', 18, 'bold'))
        
        self.style.configure('Section.TLabel', 
                           background='#2c3e50', 
                           foreground='#ecf0f1', 
                           font=('Arial', 11, 'bold'),
                           padding=8)
        
        self.style.configure('Action.TButton', 
                           font=('Arial', 10),
                           padding=8)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_interface(self):
        """Build the main user interface."""
        # Main container
        main_frame = tk.Frame(self.root, bg='#34495e', padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)
        
        # Application header
        header_label = ttk.Label(main_frame, 
                               text="North Sussex Judo Training Fee Calculator",
                               style='Header.TLabel')
        header_label.pack(pady=(0, 20))
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Initialize all tabs
        self.create_registration_tab()
        self.create_athlete_overview_tab()
        self.create_fee_calculation_tab()
    
    def create_registration_tab(self):
        """Create the athlete registration interface."""
        reg_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(reg_frame, text="Register Athlete")
        
        # Registration form
        form_container = ttk.Frame(reg_frame)
        form_container.pack(fill='x', pady=(0, 15))
        
        # Name field
        ttk.Label(form_container, text="Full Name:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', padx=(0, 10), pady=8)
        self.name_field = ttk.Entry(form_container, font=('Arial', 10), width=35)
        self.name_field.grid(row=0, column=1, padx=(0, 20), pady=8, sticky='ew')
        
        # Training plan selection
        ttk.Label(form_container, text="Training Plan:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=8)
        self.plan_var = tk.StringVar(value="Beginner")
        plan_selector = ttk.Combobox(form_container, textvariable=self.plan_var,
                                   values=list(TrainingConfig.TRAINING_PLANS.keys()),
                                   state='readonly', font=('Arial', 10), width=32)
        plan_selector.grid(row=1, column=1, padx=(0, 20), pady=8, sticky='ew')
        plan_selector.bind('<<ComboboxSelected>>', self.on_plan_change)
        
        # Weight input
        ttk.Label(form_container, text="Weight (kg):", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky='w', padx=(0, 10), pady=8)
        self.weight_field = ttk.Entry(form_container, font=('Arial', 10), width=35)
        self.weight_field.grid(row=2, column=1, padx=(0, 20), pady=8, sticky='ew')
        
        # Competition entries
        ttk.Label(form_container, text="Monthly Competitions:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky='w', padx=(0, 10), pady=8)
        self.competitions_field = ttk.Entry(form_container, font=('Arial', 10), width=35)
        self.competitions_field.grid(row=3, column=1, padx=(0, 20), pady=8, sticky='ew')
        self.competitions_field.insert(0, "0")
        
        # Private coaching
        ttk.Label(form_container, text="Private Coaching (hrs/week):", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky='w', padx=(0, 10), pady=8)
        self.coaching_field = ttk.Entry(form_container, font=('Arial', 10), width=35)
        self.coaching_field.grid(row=4, column=1, padx=(0, 20), pady=8, sticky='ew')
        self.coaching_field.insert(0, "0")
        
        # Configure grid weights
        form_container.columnconfigure(1, weight=1)
        
        # Action buttons
        button_container = ttk.Frame(reg_frame)
        button_container.pack(fill='x', pady=(0, 15))
        
        register_btn = ttk.Button(button_container, text="Register Athlete", 
                                command=self.register_athlete,
                                style='Action.TButton')
        register_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ttk.Button(button_container, text="Clear Form", 
                             command=self.clear_registration_form,
                             style='Action.TButton')
        clear_btn.pack(side='left')
        
        # Information display
        info_container = ttk.LabelFrame(reg_frame, text="Training Program Information", padding=10)
        info_container.pack(fill='both', expand=True)
        
        self.info_display = tk.Text(info_container, wrap='word', height=18, 
                                  font=('Consolas', 9), 
                                  bg='#ecf0f1', fg='#2c3e50', state='disabled')
        info_scrollbar = ttk.Scrollbar(info_container, orient='vertical', command=self.info_display.yview)
        self.info_display.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_display.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
        
        # Load initial information
        self.update_program_info()
    
    def create_athlete_overview_tab(self):
        """Create the athlete management overview."""
        overview_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(overview_frame, text="Athlete Management")
        
        # Control panel
        controls = ttk.Frame(overview_frame)
        controls.pack(fill='x', pady=(0, 15))
        
        ttk.Label(controls, text="Registered Athletes", 
                 font=('Arial', 14, 'bold')).pack(side='left')
        
        refresh_btn = ttk.Button(controls, text="Refresh List", 
                               command=self.refresh_athlete_display,
                               style='Action.TButton')
        refresh_btn.pack(side='right', padx=(10, 0))
        
        remove_btn = ttk.Button(controls, text="Remove Selected", 
                              command=self.remove_athlete,
                              style='Action.TButton')
        remove_btn.pack(side='right')
        
        # Athlete listing
        columns = ('Name', 'Plan', 'Weight', 'Category', 'Competitions', 'Coaching', 'Monthly Fee')
        self.athlete_display = ttk.Treeview(overview_frame, columns=columns, show='headings', height=18)
        
        # Configure column headers and widths
        headers = {
            'Name': ('Athlete Name', 140),
            'Plan': ('Training Plan', 110),
            'Weight': ('Weight (kg)', 90),
            'Category': ('Weight Category', 130),
            'Competitions': ('Competitions', 100),
            'Coaching': ('Coaching (h/wk)', 110),
            'Monthly Fee': ('Monthly Fee', 100)
        }
        
        for col, (header, width) in headers.items():
            self.athlete_display.heading(col, text=header)
            self.athlete_display.column(col, width=width)
        
        # Scrollbar for athlete list
        display_scrollbar = ttk.Scrollbar(overview_frame, orient='vertical', command=self.athlete_display.yview)
        self.athlete_display.configure(yscrollcommand=display_scrollbar.set)
        
        self.athlete_display.pack(side='left', fill='both', expand=True)
        display_scrollbar.pack(side='right', fill='y')
    
    def create_fee_calculation_tab(self):
        """Create the fee calculation and reporting interface."""
        calc_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(calc_frame, text="Fee Reports")
        
        # Selection interface
        selection_container = ttk.LabelFrame(calc_frame, text="Generate Reports", padding=10)
        selection_container.pack(fill='x', pady=(0, 15))
        
        ttk.Label(selection_container, text="Select Athlete:", font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.selected_athlete_var = tk.StringVar()
        self.athlete_selector = ttk.Combobox(selection_container, 
                                           textvariable=self.selected_athlete_var,
                                           state='readonly', font=('Arial', 10), width=30)
        self.athlete_selector.pack(side='left', padx=(0, 15))
        
        individual_btn = ttk.Button(selection_container, text="Individual Report", 
                                  command=self.generate_individual_report,
                                  style='Action.TButton')
        individual_btn.pack(side='left', padx=(0, 8))
        
        summary_btn = ttk.Button(selection_container, text="Full Summary", 
                               command=self.generate_summary_report,
                               style='Action.TButton')
        summary_btn.pack(side='left')
        
        # Report display
        report_container = ttk.LabelFrame(calc_frame, text="Generated Reports", padding=10)
        report_container.pack(fill='both', expand=True)
        
        self.report_display = tk.Text(report_container, wrap='word', 
                                    font=('Consolas', 10), 
                                    bg='#ecf0f1', fg='#2c3e50', state='disabled')
        report_scrollbar = ttk.Scrollbar(report_container, orient='vertical', command=self.report_display.yview)
        self.report_display.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_display.pack(side='left', fill='both', expand=True)
        report_scrollbar.pack(side='right', fill='y')
    
    def on_plan_change(self, event=None):
        """Handle training plan selection changes."""
        self.update_program_info()
        if self.plan_var.get() == "Beginner":
            self.competitions_field.delete(0, tk.END)
            self.competitions_field.insert(0, "0")
    
    def register_athlete(self):
        """Process new athlete registration."""
        try:
            name = self.name_field.get().strip()
            if not name:
                raise ValueError("Please enter the athlete's name")
            
            # Check for duplicate names
            if any(athlete.name.lower() == name.lower() for athlete in self.athletes):
                raise ValueError("An athlete with this name is already registered")
            
            training_plan = self.plan_var.get()
            
            weight = validate_number_input(
                self.weight_field.get(), 
                "Weight", 
                min_val=30, 
                max_val=200
            )
            
            competitions = int(validate_number_input(
                self.competitions_field.get(), 
                "Competitions", 
                min_val=0, 
                max_val=4
            ))
            
            coaching_hours = int(validate_number_input(
                self.coaching_field.get(), 
                "Private coaching hours", 
                min_val=0, 
                max_val=TrainingConfig.MAX_PRIVATE_COACHING_HOURS
            ))
            
            athlete = Athlete(name, training_plan, weight, competitions, coaching_hours)
            self.athletes.append(athlete)
            
            self.refresh_athlete_display()
            self.update_athlete_selector()
            self.clear_registration_form()
            
            messagebox.showinfo("Registration Complete", f"{athlete.name} has been successfully registered!")
            
        except ValueError as e:
            messagebox.showerror("Registration Error", str(e))
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {str(e)}")
    
    def clear_registration_form(self):
        """Reset all registration form fields."""
        self.name_field.delete(0, tk.END)
        self.plan_var.set("Beginner")
        self.weight_field.delete(0, tk.END)
        self.competitions_field.delete(0, tk.END)
        self.competitions_field.insert(0, "0")
        self.coaching_field.delete(0, tk.END)
        self.coaching_field.insert(0, "0")
        self.update_program_info()
    
    def refresh_athlete_display(self):
        """Update the athlete overview display."""
        for item in self.athlete_display.get_children():
            self.athlete_display.delete(item)
        
        for athlete in self.athletes:
            fees = athlete.calculate_monthly_fees()
            values = (
                athlete.name,
                athlete.training_plan,
                f"{athlete.current_weight:.1f}",
                athlete.weight_category,
                athlete.competitions,
                athlete.private_coaching_hours,
                format_currency(fees['total_cost'])
            )
            self.athlete_display.insert('', 'end', values=values)
    
    def remove_athlete(self):
        """Remove selected athlete from the system."""
        selection = self.athlete_display.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an athlete to remove")
            return
        
        item = selection[0]
        athlete_name = self.athlete_display.item(item, 'values')[0]
        
        if messagebox.askyesno("Confirm Removal", 
                              f"Remove {athlete_name} from the system?\n\nThis action cannot be undone."):
            self.athletes = [a for a in self.athletes if a.name != athlete_name]
            self.refresh_athlete_display()
            self.update_athlete_selector()
            messagebox.showinfo("Athlete Removed", f"{athlete_name} has been removed from the system")
    
    def update_athlete_selector(self):
        """Update the athlete selection dropdown."""
        athlete_names = [athlete.name for athlete in self.athletes]
        self.athlete_selector['values'] = athlete_names
        if athlete_names:
            self.athlete_selector.set(athlete_names[0])
        else:
            self.athlete_selector.set("")
    
    def generate_individual_report(self):
        """Generate detailed report for selected athlete."""
        if not self.athletes:
            messagebox.showinfo("No Athletes", "Please register athletes before generating reports")
            return
        
        selected_name = self.selected_athlete_var.get()
        if not selected_name:
            messagebox.showwarning("No Selection", "Please select an athlete for the report")
            return
        
        athlete = next((a for a in self.athletes if a.name == selected_name), None)
        if not athlete:
            messagebox.showerror("Error", "Selected athlete not found")
            return
        
        report = generate_fee_report(athlete)
        
        self.report_display.config(state='normal')
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)
        self.report_display.config(state='disabled')
    
    def generate_summary_report(self):
        """Generate comprehensive summary of all athletes."""
        if not self.athletes:
            messagebox.showinfo("No Athletes", "Please register athletes before generating reports")
            return
        
        all_reports = ""
        total_monthly_revenue = 0
        
        for athlete in self.athletes:
            report = generate_fee_report(athlete)
            all_reports += report + "\n"
            
            fees = athlete.calculate_monthly_fees()
            total_monthly_revenue += fees['total_cost']
        
        # Add summary section
        summary = f"\n{'='*55}\n"
        summary += f"FACILITY MONTHLY SUMMARY\n"
        summary += f"{'='*55}\n"
        summary += f"Total Registered Athletes: {len(self.athletes)}\n"
        summary += f"Total Monthly Revenue: {format_currency(total_monthly_revenue)}\n"
        summary += f"Average Fee per Athlete: {format_currency(total_monthly_revenue / len(self.athletes))}\n"
        summary += f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
        
        # Plan breakdown
        plan_counts = {}
        for athlete in self.athletes:
            plan_counts[athlete.training_plan] = plan_counts.get(athlete.training_plan, 0) + 1
        
        summary += f"\nTRAINING PLAN DISTRIBUTION:\n"
        for plan, count in plan_counts.items():
            summary += f"• {plan}: {count} athletes\n"
        
        all_reports += summary
        
        self.report_display.config(state='normal')
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, all_reports)
        self.report_display.config(state='disabled')
    
    def update_program_info(self):
        """Update the training program information display."""
        selected_plan = self.plan_var.get()
        plan_details = TrainingConfig.TRAINING_PLANS.get(selected_plan, {})
        
        info_text = f"""NORTH SUSSEX JUDO TRAINING PROGRAMS

AVAILABLE TRAINING PLANS:
{'='*50}

BEGINNER PROGRAM:
• Target: New students learning judo fundamentals
• Sessions: 2 per week
• Weekly Fee: £25.00
• Monthly Fee: £100.00
• Competition Participation: Not permitted

INTERMEDIATE PROGRAM:
• Target: Students with basic judo experience
• Sessions: 3 per week  
• Weekly Fee: £30.00
• Monthly Fee: £120.00
• Competition Participation: Encouraged

ELITE PROGRAM:
• Target: Advanced students training for competition
• Sessions: 5 per week
• Weekly Fee: £35.00
• Monthly Fee: £140.00
• Competition Participation: Highly encouraged

ADDITIONAL SERVICES:
{'='*50}
• Private Coaching: £9.50 per hour
  - Maximum 5 hours per week per athlete
  - Personalized instruction and technique refinement
  
• Competition Entry: £22.00 per competition
  - Available for Intermediate and Elite athletes only
  - Maximum 4 competitions per month
  - Includes entry fees and basic equipment

WEIGHT CATEGORIES:
{'='*50}
• Flyweight: Up to 66kg
• Lightweight: 66.1 - 73kg  
• Light-Middleweight: 73.1 - 81kg
• Middleweight: 81.1 - 90kg
• Light-Heavyweight: 90.1 - 100kg
• Heavyweight: Over 100kg

CURRENTLY SELECTED: {selected_plan.upper()}
{'='*50}
• Weekly Sessions: {plan_details.get('sessions_per_week', 'N/A')}
• Weekly Cost: {format_currency(plan_details.get('weekly_fee', 0))}
• Monthly Cost: {format_currency(plan_details.get('weekly_fee', 0) * 4)}

FACILITY POLICIES:
{'='*50}
• Monthly fees calculated as 4-week periods
• Competition eligibility restricted by training level
• Private coaching sessions scheduled separately
• Weight categories follow international judo standards
• All fees include facility usage and basic equipment"""

        self.info_display.config(state='normal')
        self.info_display.delete(1.0, tk.END)
        self.info_display.insert(1.0, info_text)
        self.info_display.config(state='disabled')
    
    def load_initial_data(self):
        """Load sample athletes for demonstration purposes."""
        sample_data = [
            ("James Mitchell", "Elite", 78.5, 3, 4),
            ("Sarah Chen", "Intermediate", 67.2, 2, 2),
            ("Robert Taylor", "Beginner", 85.1, 0, 1),
            ("Emma Rodriguez", "Elite", 72.8, 4, 5),
            ("Michael Johnson", "Intermediate", 81.5, 1, 0),
            ("Lisa Anderson", "Beginner", 69.3, 0, 0)
        ]
        
        for name, plan, weight, competitions, coaching in sample_data:
            try:
                athlete = Athlete(name, plan, weight, competitions, coaching)
                self.athletes.append(athlete)
            except ValueError:
                continue
        
        self.refresh_athlete_display()
        self.update_athlete_selector()


def main():
    """Initialize and run the application."""
    try:
        root = tk.Tk()
        app = JudoManagementSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()