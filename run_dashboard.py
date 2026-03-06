import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*50)
print("STARTING ATTRITION PREDICTION DASHBOARD")
print("="*50)
print("\nThe dashboard will open automatically in your browser.")
print("If it doesn't open, go to: http://localhost:8051")
print("\nPress CTRL+C to stop the dashboard")
print("="*50)

# Run the dashboard
subprocess.run([sys.executable, "attrition_dashboard.py"])