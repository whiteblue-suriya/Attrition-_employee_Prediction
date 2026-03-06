# Employee Attrition Prediction Project
## Step-by-Step Guide

---

## What is Employee Attrition?

**Employee Attrition** = When employees leave a company over time.

This ML project predicts which employees are likely to leave, helping HR take preventive action.

---

## Project Overview

```
EMPLOYEE ATTRITION PREDICTION
│
├── attrition_schema.sql      → Database tables
├── attrition_model.py        → ML model training
├── attrition_dashboard.py    → Prediction UI
└── models/
    └── attrition_model.pkl   → Trained model
```

---

## Step 1: Prerequisites

### Install Required Packages
```bash
pip install pandas numpy scikit-learn sqlalchemy pyodbc python-dotenv plotly dash
```

### Verify SQL Server
- Make sure SQL Server is running
- Create database: `employee_performance`

---

## Step 2: Database Setup

### 2.1 Create Database Tables

Open SQL Server Management Studio (SSMS) and run `attrition_schema.sql`:

```sql
-- This creates:
-- 1. attrition_data       → Historical employee data
-- 2. attrition_predictions → Model predictions
-- 3. model_performance    → Track model accuracy
```

### 2.2 Verify Tables Created
```sql
USE employee_performance;
GO
SELECT * FROM attrition_data;
SELECT * FROM attrition_predictions;
```

You should see 20 sample employee records!

---

## Step 3: Configure Environment

### 3.1 Update .env File
```env
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=employee_performance
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### 3.2 Test Database Connection
```bash
python -c "from database import DatabaseConnection; db = DatabaseConnection(); print('Connected!' if db.connect() else 'Failed')"
```

---

## Step 4: Train the ML Model

### 4.1 Run Training Script
```bash
python attrition_model.py
```

### 4.2 What Happens During Training?

1. **Data Loading**: Reads 20 employee records from database
2. **Preprocessing**: 
   - Converts categorical data (gender, department) to numbers
   - Handles missing values
3. **Model Comparison**: Tests 3 algorithms:
   - Random Forest
   - Gradient Boosting
   - Logistic Regression
4. **Evaluation**: Compares accuracy, precision, recall, F1-score
5. **Model Selection**: Picks the best one
6. **Saves Model**: Stores as `models/attrition_model.pkl`

### 4.3 Expected Output
```
EMPLOYEE ATTRITION PREDICTION MODEL TRAINING
============================================================
Loaded 20 records from database
Features used: 19
Total samples: 20
Attrition rate: 50.00%

MODEL COMPARISON
------------------------------------------------------------

Random Forest:
  Accuracy:  0.7500
  Precision: 0.6667
  Recall:    0.6667
  F1 Score:  0.6667
  ROC-AUC:   0.7500

Gradient Boosting:
  Accuracy:  0.7500
  Precision: 0.6667
  Recall:    0.7500
  F1 Score:  0.7083
  ROC-AUC:   0.7917

BEST MODEL: Gradient Boosting (ROC-AUC: 0.7917)
```

### 4.4 Check Generated Files
```bash
dir models
```

Should show:
- `attrition_model.pkl` - Trained model
- `feature_importance.csv` - Key factors

---

## Step 5: Launch Prediction Dashboard

### 5.1 Run Dashboard
```bash
python attrition_dashboard.py
```

### 5.2 Access Dashboard
Open browser: **http://localhost:8051**

### 5.3 Dashboard Features

| Feature | Description |
|---------|-------------|
| Employee Input Form | Enter employee details |
| Predict Button | Click to get prediction |
| Risk Gauge | Visual risk percentage |
| Factor Analysis | Key metrics chart |
| Historical Data | Past attrition records |

---

## Step 6: Make Predictions

### 6.1 Enter Employee Data

Example: Young engineer with low satisfaction
```
Age: 25
Monthly Income: $40,000
Gender: Male
Marital Status: Single
Education: Bachelor
Department: Engineering
Job Role: Developer
Years at Company: 1
Job Satisfaction: 2/5
Work-Life Balance: 2/5
Overtime: Yes
Business Travel: Frequently
```

### 6.2 View Results

The dashboard will show:
- **Prediction**: Yes/No (Will they leave?)
- **Risk Probability**: 0-100%
- **Risk Level**: Low/Medium/High/Critical
- **Confidence**: How sure is the model?

---

## Understanding the Results

### Risk Levels
| Probability | Risk Level | Color | Action |
|-------------|------------|-------|--------|
| 0-30% | Low | Green | Monitor |
| 30-50% | Medium | Blue | Stay alert |
| 50-70% | High | Orange | Interview |
| 70-100% | Critical | Red | Immediate action |

### Key Factors That Increase Attrition Risk
1. **Low Job Satisfaction** (1-2/5)
2. **Poor Work-Life Balance**
3. **Overtime** (Yes)
4. **Low Income**
5. **Short Tenure** (< 2 years)
6. **Frequent Business Travel**

---

## Step 7: Integrate with Main Dashboard

### 7.1 Add to Existing Dashboard

You can add attrition predictions to your main dashboard:

```python
# In dashboard_app.py, add:
from attrition_model import AttritionPredictor

predictor = AttritionPredictor()

# Get predictions for all employees
@callback
def get_predictions():
    # Add prediction logic here
    pass
```

---

## Common Issues & Solutions

### Issue 1: "Model not found"
**Solution**: Run training first
```bash
python attrition_model.py
```

### Issue 2: "Database connection failed"
**Solution**: Check .env settings and SQL Server

### Issue 3: "No data in table"
**Solution**: Run attrition_schema.sql to insert sample data

### Issue 4: "Port 8051 in use"
**Solution**: Change port in attrition_dashboard.py
```python
app.run_server(port=8052)
```

---

## Project Files Explained

### attrition_schema.sql
Creates 3 database tables:
- `attrition_data` - Training data (20 employees)
- `attrition_predictions` - Predictions storage
- `model_performance` - Model accuracy tracking

### attrition_model.py
ML pipeline:
1. Loads data from SQL
2. Preprocesses features
3. Trains 3 models
4. Selects best model
5. Saves as pickle file

### attrition_dashboard.py
Web interface:
1. Employee input form
2. Prediction button
3. Risk gauge visualization
4. Historical data table

---

## How the ML Model Works

### Features Used (Input Variables)
```
Numerical:
- age, monthly_income
- years_at_company, years_in_role
- job_satisfaction (1-5)
- work_life_balance (1-5)
- performance_rating (1-5)
- distance_from_home
- total_experience
- training_times_last_year

Categorical (encoded to numbers):
- gender, marital_status
- education_level
- department, job_role
- overtime, business_travel
```

### Target Variable
```
attrition = "Yes" or "No"
```

### Algorithm: Gradient Boosting
- Combines multiple decision trees
- Each tree learns from previous errors
- Excellent for structured data
- Good at handling imbalanced classes

---

## Measuring Model Success

### Metrics Explained
| Metric | What it means | Good value |
|--------|---------------|------------|
| Accuracy | % correct predictions | > 80% |
| Precision | % of predicted "Yes" that are correct | > 70% |
| Recall | % of actual "Yes" we found | > 70% |
| F1 Score | Harmonic mean of precision/recall | > 70% |
| ROC-AUC | Ability to distinguish classes | > 0.80 |

---

## Real-World Application

### How to Use This in Production

1. **Collect More Data**
   - Add more employees (100+)
   - Include more features

2. **Retrain Regularly**
   - Run `python attrition_model.py` monthly
   - Update model with new data

3. **Take Action**
   - High risk employees → Schedule 1-on-1
   - Review compensation
   - Improve work-life balance

4. **Track Results**
   - Monitor prediction accuracy
   - Track if employees actually left

---

## Next Steps to Improve

1. **Add More Features**
   - Salary history
   - Promotion history
   - Manager feedback
   - Remote work status

2. **Try Deep Learning**
   - Use Neural Networks
   - Better for complex patterns

3. **Deploy to Production**
   - Use FastAPI
   - Docker container
   - Connect to HR system

---

## Summary

✅ **Step 1**: Install packages  
✅ **Step 2**: Create database tables  
✅ **Step 3**: Configure .env  
✅ **Step 4**: Train model  
✅ **Step 5**: Launch dashboard  
✅ **Step 6**: Make predictions  

**Your Employee Attrition Prediction system is ready!**

---

## Quick Commands Reference

```bash
# Test database
python -c "from database import DatabaseConnection; print('OK')"

# Train model
python attrition_model.py

# Run dashboard
python attrition_dashboard.py

# Open dashboard
http://localhost:8051
```

---

## Need Help?

If stuck:
1. Check SQL Server is running
2. Verify .env credentials
3. Ensure sample data exists
4. Check model file exists in models/