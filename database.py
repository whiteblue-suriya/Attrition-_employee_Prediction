import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        db_type = os.getenv('DB_TYPE', 'mysql').lower()
        
        if db_type == 'mysql':
            # URL encode the password to handle special characters
            password = quote_plus(os.getenv('DB_PASSWORD', ''))
            username = quote_plus(os.getenv('DB_USERNAME', 'root'))
            
            self.connection_string = (
                f"mysql+pymysql://{username}:{password}"
                f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
                f"/{os.getenv('DB_DATABASE', 'employee_performance')}"
            )
        else:
            self.connection_string = (
                f"mssql+pyodbc://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
                f"@{os.getenv('DB_SERVER')}/{os.getenv('DB_DATABASE')}"
                f"?driver={os.getenv('DB_DRIVER').replace(' ', '+')}"
            )
        
        self.engine = None
    
    def connect(self):
        try:
            self.engine = create_engine(self.connection_string)
            with self.engine.connect() as conn:
                pass
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def get_employee_data(self):
        try:
            query = """
            SELECT 
                e.employee_id,
                e.name,
                e.department,
                e.position,
                e.hire_date,
                p.tasks_completed,
                p.projects_delivered,
                p.productivity_score,
                p.time_efficiency,
                p.quality_rating,
                p.last_updated
            FROM employees e
            LEFT JOIN productivity_metrics p ON e.employee_id = p.employee_id
            ORDER BY e.employee_id
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error fetching employee data: {e}")
            return pd.DataFrame()
    
    def get_department_performance(self):
        try:
            query = """
            SELECT 
                e.department,
                COUNT(e.employee_id) as employee_count,
                AVG(p.productivity_score) as avg_productivity,
                AVG(p.time_efficiency) as avg_time_efficiency,
                AVG(p.quality_rating) as avg_quality,
                SUM(p.tasks_completed) as total_tasks,
                SUM(p.projects_delivered) as total_projects
            FROM employees e
            LEFT JOIN productivity_metrics p ON e.employee_id = p.employee_id
            GROUP BY e.department
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error fetching department data: {e}")
            return pd.DataFrame()
    
    def get_monthly_trends(self):
        try:
            query = """
            SELECT 
                YEAR(last_updated) as year,
                MONTH(last_updated) as month,
                AVG(productivity_score) as avg_productivity,
                SUM(tasks_completed) as total_tasks,
                COUNT(employee_id) as active_employees
            FROM productivity_metrics
            WHERE last_updated >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
            GROUP BY YEAR(last_updated), MONTH(last_updated)
            ORDER BY year, month
            """
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error fetching trend data: {e}")
            return pd.DataFrame()
    
    def get_attrition_data(self):
        try:
            query = "SELECT * FROM attrition_data"
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error fetching attrition data: {e}")
            return pd.DataFrame()
    
    def save_prediction(self, employee_id, prediction_data):
        try:
            query = """
            INSERT INTO attrition_predictions 
            (employee_id, attrition_probability, attrition_prediction, 
             risk_level, confidence_score, model_version)
            VALUES (:employee_id, :probability, :prediction, 
                   :risk_level, :confidence, :version)
            """
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'employee_id': employee_id,
                    'probability': prediction_data['probability'],
                    'prediction': prediction_data['prediction'],
                    'risk_level': prediction_data['risk_level'],
                    'confidence': prediction_data['confidence'],
                    'version': 'v1.0.0'
                })
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving prediction: {e}")
            return False