import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import pickle
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, classification_report,
                             confusion_matrix)
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

class AttritionModelTrainer:
    def __init__(self):
        db_type = os.getenv('DB_TYPE', 'mysql').lower()
        
        if db_type == 'mysql':
            from urllib.parse import quote_plus
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
        
        self.engine = create_engine(self.connection_string)
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'age', 'monthly_income', 'years_at_company', 'years_in_role',
            'job_satisfaction', 'work_life_balance', 'environment_satisfaction',
            'relationship_satisfaction', 'performance_rating', 'distance_from_home',
            'num_companies_worked', 'total_experience', 'training_times_last_year'
        ]
        self.categorical_columns = ['gender', 'marital_status', 'education_level', 
                                    'department', 'job_role', 'overtime', 'business_travel']
        
    def load_data(self):
        query = """
        SELECT * FROM attrition_data
        """
        df = pd.read_sql(query, self.engine)
        print(f"Loaded {len(df)} records from database")
        return df
    
    def preprocess_data(self, df):
        df_processed = df.copy()
        
        for col in self.categorical_columns:
            if col in df_processed.columns:
                le = LabelEncoder()
                df_processed[col + '_encoded'] = le.fit_transform(df_processed[col].astype(str))
                self.label_encoders[col] = le
        
        if 'attrition' in df_processed.columns:
            df_processed['attrition_encoded'] = df_processed['attrition'].map({'Yes': 1, 'No': 0})
        
        return df_processed
    
    def prepare_features(self, df):
        feature_cols = self.feature_columns.copy()
        
        for col in self.categorical_columns:
            feature_cols.append(col + '_encoded')
        
        X = df[feature_cols].copy()
        X = X.fillna(X.median())
        
        return X
    
    def train_model(self):
        print("\n" + "="*60)
        print("EMPLOYEE ATTRITION PREDICTION MODEL TRAINING")
        print("="*60)
        
        df = self.load_data()
        df_processed = self.preprocess_data(df)
        
        X = self.prepare_features(df_processed)
        y = df_processed['attrition_encoded']
        
        print(f"\nFeatures used: {len(X.columns)}")
        print(f"Total samples: {len(X)}")
        print(f"Attrition rate: {y.mean()*100:.2f}%")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, class_weight='balanced'
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100, max_depth=5, random_state=42
            ),
            'Logistic Regression': LogisticRegression(
                random_state=42, class_weight='balanced', max_iter=1000
            )
        }
        
        best_model = None
        best_score = 0
        best_name = ""
        
        print("\n" + "-"*60)
        print("MODEL COMPARISON")
        print("-"*60)
        
        for name, model in models.items():
            if name == 'Logistic Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_prob = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_prob = model.predict_proba(X_test)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            roc_auc = roc_auc_score(y_test, y_prob)
            
            print(f"\n{name}:")
            print(f"  Accuracy:  {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1 Score:  {f1:.4f}")
            print(f"  ROC-AUC:   {roc_auc:.4f}")
            
            if roc_auc > best_score:
                best_score = roc_auc
                best_model = model
                best_name = name
        
        print("\n" + "-"*60)
        print(f"BEST MODEL: {best_name} (ROC-AUC: {best_score:.4f})")
        print("-"*60)
        
        self.model = best_model
        self.model_name = best_name
        
        if best_name == 'Logistic Regression':
            self.model.fit(X_train_scaled, y_train)
        else:
            self.model.fit(X, y)
        
        self.save_model()
        self.save_feature_importance()
        self.log_performance(X_train, X_test, y_train, y_test)
        
        print("\n" + "="*60)
        print("MODEL TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return best_model
    
    def save_model(self):
        os.makedirs('models', exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'categorical_columns': self.categorical_columns,
            'model_name': self.model_name
        }
        
        with open('models/attrition_model.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\nModel saved to: models/attrition_model.pkl")
    
    def save_feature_importance(self):
        if hasattr(self.model, 'feature_importances_'):
            # Get the actual feature columns used in training
            feature_cols = self.feature_columns.copy()
            for col in self.categorical_columns:
                feature_cols.append(col + '_encoded')
            
            # Match lengths
            num_features = len(self.model.feature_importances_)
            actual_features = feature_cols[:num_features]
            
            importances = pd.DataFrame({
                'feature': actual_features,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            importances.to_csv('models/feature_importance.csv', index=False)
            
            print("\nTop 5 Important Features:")
            print("-"*40)
            for idx, row in importances.head(5).iterrows():
                print(f"  {row['feature']}: {row['importance']:.4f}")
    
    def log_performance(self, X_train, X_test, y_train, y_test):
        if self.model_name == 'Logistic Regression':
            y_pred = self.model.predict(self.scaler.transform(X_test))
            y_prob = self.model.predict_proba(self.scaler.transform(X_test))[:, 1]
        else:
            y_pred = self.model.predict(X_test)
            y_prob = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        performance_data = pd.DataFrame({
            'model_version': ['v1.0.0'],
            'accuracy': [accuracy],
            'precision_score': [precision],
            'recall_score': [recall],
            'f1_score': [f1],
            'roc_auc_score': [roc_auc],
            'training_samples': [len(X_train)],
            'test_samples': [len(X_test)],
            'features_used': [','.join(self.feature_columns)]
        })
        
        try:
            performance_data.to_sql('model_performance', self.engine, 
                                   if_exists='append', index=False)
            print("\nPerformance logged to database")
        except Exception as e:
            print(f"Could not log to database: {e}")


class AttritionPredictor:
    def __init__(self):
        self.loaded = False
        self.load_model()
    
    def load_model(self):
        try:
            with open('models/attrition_model.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_columns = model_data['feature_columns']
            self.categorical_columns = model_data['categorical_columns']
            self.model_name = model_data['model_name']
            
            self.loaded = True
            print(f"Model loaded successfully: {self.model_name}")
        except FileNotFoundError:
            print("Model not found. Please train the model first.")
            self.loaded = False
    
    def predict(self, employee_data):
        if not self.loaded:
            return None
        
        features = self.prepare_features(employee_data)
        
        if self.model_name == 'Logistic Regression':
            features_scaled = self.scaler.transform(features)
            probability = self.model.predict_proba(features_scaled)[0][1]
        else:
            probability = self.model.predict_proba(features)[0][1]
        
        prediction = 'Yes' if probability >= 0.5 else 'No'
        
        if probability >= 0.7:
            risk_level = 'Critical'
        elif probability >= 0.5:
            risk_level = 'High'
        elif probability >= 0.3:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'prediction': prediction,
            'probability': probability,
            'risk_level': risk_level,
            'confidence': abs(probability - 0.5) * 2 * 100
        }
    
    def prepare_features(self, employee_data):
        features = pd.DataFrame([employee_data])
        
        for col in self.categorical_columns:
            if col in features.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                features[col + '_encoded'] = le.transform(features[col].astype(str))
        
        feature_cols = self.feature_columns.copy()
        for col in self.categorical_columns:
            feature_cols.append(col + '_encoded')
        
        X = features[feature_cols].fillna(0)
        
        return X


if __name__ == "__main__":
    print("Starting Employee Attrition Prediction Model Training...")
    trainer = AttritionModelTrainer()
    trainer.train_model()
    
    print("\n" + "="*60)
    print("TESTING PREDICTION")
    print("="*60)
    
    predictor = AttritionPredictor()
    
    test_employee = {
        'age': 28,
        'monthly_income': 45000,
        'years_at_company': 1,
        'years_in_role': 1,
        'job_satisfaction': 2,
        'work_life_balance': 2,
        'environment_satisfaction': 2,
        'relationship_satisfaction': 2,
        'performance_rating': 3,
        'distance_from_home': 25,
        'num_companies_worked': 3,
        'total_experience': 4,
        'training_times_last_year': 2,
        'gender': 'Male',
        'marital_status': 'Single',
        'education_level': 'Bachelor',
        'department': 'Engineering',
        'job_role': 'Developer',
        'overtime': 'Yes',
        'business_travel': 'Frequently'
    }
    
    result = predictor.predict(test_employee)
    print(f"\nTest Employee Prediction:")
    print(f"  Attrition Risk: {result['prediction']}")
    print(f"  Probability: {result['probability']*100:.1f}%")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Confidence: {result['confidence']:.1f}%")