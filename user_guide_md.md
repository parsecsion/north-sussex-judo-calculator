# North Sussex Judo - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Adding Athletes](#adding-athletes)
3. [Managing Athletes](#managing-athletes)
4. [Calculating Fees](#calculating-fees)
5. [Understanding Reports](#understanding-reports)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- Windows 10+, macOS 10.14+, or Linux Ubuntu 18.04+
- Python 3.8 or higher
- 900x700 minimum screen resolution

### First Launch
1. Double-click `north_sussex_judo.py` or run `python north_sussex_judo.py`
2. The application loads with 6 sample athletes for demonstration
3. Three main tabs are available: Add New Athlete, Athlete List, and Fee Calculator

## Adding Athletes

### Step-by-Step Process
1. **Navigate to "Add New Athlete" tab**
2. **Fill in required information:**
   - **Athlete Name**: Full name (required)
   - **Training Plan**: Select from Beginner, Intermediate, or Elite
   - **Current Weight**: Weight in kilograms
   - **Competitions**: Number of competitions this month (0-4)
   - **Private Coaching**: Hours per week (0-5)

3. **Click "Add Athlete"** to save
4. **Use "Clear Form"** to reset all fields

### Training Plan Guidelines
- **Beginner**: 2 sessions/week, £25 weekly, cannot compete
- **Intermediate**: 3 sessions/week, £30 weekly, can compete  
- **Elite**: 5 sessions/week, £35 weekly, can compete

### Input Validation
The system automatically validates:
- Names cannot be empty or duplicate
- Weight must be between 30-200 kg
- Only Intermediate/Elite athletes can enter competitions
- Maximum 5 hours private coaching per week
- Maximum 4 competitions per month

## Managing Athletes

### Viewing Athletes
1. **Go to "Athlete List" tab**
2. **View all registered athletes** in a table format
3. **Information displayed**:
   - Name and training plan
   - Current weight and weight category
   - Competition entries and coaching hours

### Removing Athletes
1. **Select athlete** in the list
2. **Click "Remove Selected"**
3. **Confirm deletion** in the popup dialog
4. **Click "Refresh"** to update the display

## Calculating Fees

### Individual Athlete Fees
1. **Go to "Fee Calculator" tab**
2. **Select athlete** from dropdown menu
3. **Click "Calculate Fees"**
4. **View detailed breakdown**:
   - Training fees (weekly rate × 4 weeks)
   - Private coaching costs
   - Competition entry fees
   - Total monthly cost

### All Athletes Summary
1. **Click "Calculate All"** for complete report
2. **View comprehensive summary**:
   - Individual athlete breakdowns
   - Total athletes count
   - Total monthly revenue
   - Generation timestamp

## Understanding Reports

### Fee Breakdown Components
- **Training Fees**: Based on weekly plan rate × 4 weeks
- **Private Coaching**: Hours per week × 4 weeks × £9.50/hour
- **Competition Entries**: Number of competitions × £22.00 each
- **Total Cost**: Sum of all components

### Weight Category Information
Athletes are automatically classified into weight categories:
- Flyweight: Up to 66kg
- Lightweight: Up to 73kg  
- Light-Middleweight: Up to 81kg
- Middleweight: Up to 90kg
- Light-Heavyweight: Up to 100kg
- Heavyweight: Over 100kg (unlimited)

### Monthly Calculation Rules
- Month = 4 weeks for all fee calculations
- All prices displayed to 2 decimal places (£XX.XX)
- Competitions held on 2nd Saturday of each month

## Troubleshooting

### Common Issues

#### Application Won't Start
- **Check Python installation**: Run `python --version`
- **Test tkinter**: Run `python -c "import tkinter; print('OK')"`
- **Use debug version**: Run `debug_north_sussex_judo.py`

#### Input Errors
- **"Weight must be greater than 0"**: Enter valid weight in kg
- **"Beginner athletes cannot compete"**: Change plan or set competitions to 0
- **"Maximum 5 hours coaching"**: Reduce coaching hours to 5 or less
- **"Name already exists"**: Use a different athlete name

#### Display Issues
- **Window too small**: Minimum 900x700 resolution required
- **Text too small**: Use system display scaling settings
- **Window hidden**: Check taskbar or try Alt+Tab

### Getting Help
1. **Check error messages** - they provide specific guidance
2. **Use sample data** - pre-loaded athletes show correct formats
3. **Try debug version** - provides detailed error information
4. **Check GitHub issues** - common problems and solutions

### Best Practices
- **Regular backups**: Export athlete data regularly
- **Consistent naming**: Use full names for professional records
- **Weight accuracy**: Use precise weight measurements
- **Monthly updates**: Update competition entries monthly
- **Data verification**: Double-check entries before saving

## Tips for Efficient Use

### Keyboard Shortcuts
- **Tab**: Navigate between form fields
- **Enter**: Submit forms (when cursor in text field)
- **Escape**: Close error dialogs
- **F5**: Refresh displays (in some contexts)

### Data Entry Tips
- **Use consistent naming**: "John Smith" not "john smith"
- **Round weights**: Use one decimal place (e.g., 68.5 kg)
- **Plan competitions**: Update monthly for accurate fees
- **Track coaching**: Record actual hours used

### Reporting Best Practices
- **Generate monthly**: Create reports at month-end
- **Save reports**: Copy text to external documents
- **Verify totals**: Cross-check calculations
- **Archive data**: Keep historical records