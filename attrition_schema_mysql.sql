-- ============================================
-- EMPLOYEE ATTRITION PREDICTION - MySQL VERSION
-- ============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS employee_performance;
USE employee_performance;

-- Employee Attrition History Table
CREATE TABLE attrition_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    
    -- Features/Input Variables
    age INT,
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    education_level VARCHAR(50),
    department VARCHAR(50),
    job_role VARCHAR(100),
    years_at_company INT,
    years_in_role INT,
    monthly_income DECIMAL(10,2),
    job_satisfaction INT CHECK (job_satisfaction BETWEEN 1 AND 5),
    work_life_balance INT CHECK (work_life_balance BETWEEN 1 AND 5),
    environment_satisfaction INT CHECK (environment_satisfaction BETWEEN 1 AND 5),
    relationship_satisfaction INT CHECK (relationship_satisfaction BETWEEN 1 AND 5),
    performance_rating INT CHECK (performance_rating BETWEEN 1 AND 5),
    overtime VARCHAR(10),
    business_travel VARCHAR(20),
    distance_from_home INT,
    num_companies_worked INT,
    total_experience INT,
    training_times_last_year INT,
    
    -- Target Variable
    attrition VARCHAR(10),
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Attrition Predictions Table
CREATE TABLE attrition_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    attrition_probability DECIMAL(5,4),
    attrition_prediction VARCHAR(10),
    risk_level VARCHAR(20),
    confidence_score DECIMAL(5,2),
    model_version VARCHAR(20),
    feature_importance TEXT
);

-- Model Performance Tracking Table
CREATE TABLE model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_version VARCHAR(20),
    training_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    roc_auc_score DECIMAL(5,4),
    training_samples INT,
    test_samples INT,
    features_used TEXT
);

-- ============================================
-- SAMPLE DATA
-- ============================================

INSERT INTO attrition_data (
    employee_id, age, gender, marital_status, education_level, department,
    job_role, years_at_company, years_in_role, monthly_income,
    job_satisfaction, work_life_balance, environment_satisfaction,
    relationship_satisfaction, performance_rating, overtime, business_travel,
    distance_from_home, num_companies_worked, total_experience,
    training_times_last_year, attrition
) VALUES
-- High Risk Employees (Will Leave)
(1, 28, 'Male', 'Single', 'Bachelor', 'Engineering', 'Developer', 1, 1, 45000, 2, 2, 3, 3, 3, 'Yes', 'Frequently', 25, 3, 4, 2, 'Yes'),
(2, 32, 'Female', 'Single', 'Master', 'Sales', 'Sales Rep', 2, 1, 52000, 2, 2, 2, 3, 3, 'Yes', 'Frequently', 30, 4, 8, 1, 'Yes'),
(3, 25, 'Male', 'Single', 'Bachelor', 'Marketing', 'Specialist', 1, 1, 38000, 1, 2, 2, 2, 3, 'Yes', 'Rarely', 15, 2, 3, 3, 'Yes'),
(4, 35, 'Female', 'Married', 'Master', 'Engineering', 'Senior Dev', 4, 2, 75000, 3, 3, 3, 4, 4, 'Yes', 'Frequently', 20, 5, 10, 2, 'Yes'),
(5, 29, 'Male', 'Single', 'Bachelor', 'HR', 'HR Specialist', 1, 1, 42000, 2, 2, 3, 3, 3, 'Yes', 'Rarely', 10, 3, 5, 4, 'Yes'),

-- Low Risk Employees (Will Stay)
(6, 42, 'Male', 'Married', 'PhD', 'Engineering', 'Manager', 10, 5, 120000, 5, 4, 5, 5, 5, 'No', 'Rarely', 5, 1, 15, 3, 'No'),
(7, 38, 'Female', 'Married', 'Master', 'Marketing', 'Manager', 8, 4, 95000, 4, 4, 4, 4, 4, 'No', 'Rarely', 8, 2, 12, 2, 'No'),
(8, 45, 'Male', 'Married', 'Bachelor', 'Sales', 'Director', 12, 6, 150000, 5, 5, 5, 5, 5, 'No', 'Frequently', 15, 3, 18, 4, 'No'),
(9, 30, 'Female', 'Married', 'Master', 'Engineering', 'Developer', 3, 2, 68000, 4, 4, 4, 4, 4, 'No', 'Rarely', 12, 2, 6, 3, 'No'),
(10, 36, 'Male', 'Married', 'Bachelor', 'HR', 'HR Manager', 7, 3, 85000, 4, 4, 4, 5, 4, 'No', 'Rarely', 10, 1, 10, 2, 'No'),

-- More Sample Data
(11, 26, 'Female', 'Single', 'Bachelor', 'Engineering', 'Junior Dev', 1, 1, 40000, 2, 3, 3, 3, 3, 'Yes', 'Frequently', 20, 2, 3, 1, 'Yes'),
(12, 40, 'Male', 'Married', 'Master', 'Sales', 'Manager', 8, 4, 90000, 4, 4, 4, 4, 4, 'No', 'Rarely', 10, 3, 14, 3, 'No'),
(13, 33, 'Female', 'Single', 'Master', 'Marketing', 'Specialist', 2, 2, 58000, 3, 3, 3, 3, 4, 'Yes', 'Rarely', 18, 4, 7, 2, 'Yes'),
(14, 48, 'Male', 'Married', 'PhD', 'Engineering', 'Director', 15, 8, 180000, 5, 5, 5, 5, 5, 'No', 'Rarely', 3, 1, 20, 5, 'No'),
(15, 27, 'Male', 'Single', 'Bachelor', 'Sales', 'Sales Rep', 1, 1, 38000, 2, 2, 2, 2, 3, 'Yes', 'Frequently', 25, 3, 4, 2, 'Yes'),
(16, 37, 'Female', 'Married', 'Master', 'Engineering', 'Developer', 5, 3, 72000, 4, 4, 4, 4, 4, 'No', 'Rarely', 12, 2, 9, 3, 'No'),
(17, 31, 'Male', 'Married', 'Bachelor', 'HR', 'Recruiter', 3, 2, 55000, 3, 3, 3, 4, 3, 'No', 'Rarely', 8, 3, 7, 4, 'No'),
(18, 29, 'Female', 'Single', 'Master', 'Marketing', 'Content Lead', 2, 1, 52000, 3, 3, 3, 3, 4, 'Yes', 'Frequently', 22, 4, 6, 2, 'Yes'),
(19, 44, 'Male', 'Married', 'PhD', 'Engineering', 'Tech Lead', 12, 6, 140000, 5, 4, 5, 5, 5, 'No', 'Rarely', 6, 2, 16, 4, 'No'),
(20, 34, 'Female', 'Married', 'Bachelor', 'Sales', 'Account Manager', 4, 2, 68000, 4, 4, 4, 4, 4, 'No', 'Frequently', 15, 3, 8, 3, 'No');

-- Insert initial model performance record
INSERT INTO model_performance (
    model_version, accuracy, precision_score, recall_score,
    f1_score, roc_auc_score, training_samples, test_samples,
    features_used
) VALUES
('v1.0.0', 0.8500, 0.8200, 0.7800, 0.8000, 0.8900, 1000, 250,
'Age,Income,JobSatisfaction,WorkLifeBalance,PerformanceRating,Overtime,YearsAtCompany');

-- Verify data
SELECT * FROM attrition_data;
SELECT COUNT(*) as total_records FROM attrition_data;
SELECT attrition, COUNT(*) as count FROM attrition_data GROUP BY attrition;