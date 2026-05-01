import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_rewards_data():
    np.random.seed(42)
    rows = 250 # More data for better visuals
    
    categories = ['Coffee & Treats', 'Electronics', 'Wellness', 'Amazon/Retail', 'Dining', 'Merchant Network']
    teams = ['Engineering', 'Marketing', 'Sales', 'HR']
    
    managers = {
        'Engineering': 'David Chen',
        'Marketing': 'Alex Rodriguez',
        'Sales': 'Maria Santos',
        'HR': 'Sarah Jenkins'
    }
    
    team_assignments = {
        'Engineering': ['Sam', 'Chris'],
        'Marketing': ['Alex', 'Kevin'],
        'Sales': ['Maria', 'Jordan'],
        'HR': ['Sarah', 'Pallavi']
    }
    
    data = {
        'Date': [datetime(2026, 1, 1) + timedelta(days=np.random.randint(0, 120)) for _ in range(rows)],
        'Amount': [np.random.uniform(20, 800) for _ in range(rows)],
        'Category': [np.random.choice(categories) for _ in range(rows)]
    }
    
    # Assign teams
    generated_teams = [np.random.choice(teams) for _ in range(rows)]
    data['Team'] = generated_teams
    
    # Assign employees strictly from their respective teams
    data['Employee'] = [np.random.choice(team_assignments[t]) for t in generated_teams]
    
    df = pd.DataFrame(data)
    df['Manager'] = df['Team'].map(managers)
    
    # --- CALIBRATE SPENDING PATTERNS ---
    
    # David (Engineering): Healthy Budget, March Dip
    eng_mask = (df['Team'] == 'Engineering')
    df.loc[eng_mask, 'Amount'] *= 0.8 # Lower overall spend
    march_mask = (df['Date'].dt.month == 3) & eng_mask
    df.loc[march_mask, 'Amount'] *= 0.1 # Sharp dip for demo
    
    # Alex (Marketing): Near Limit (High Burn)
    mkt_mask = (df['Team'] == 'Marketing')
    df.loc[mkt_mask, 'Amount'] *= 4.5 # Heavy spending
    
    # Maria (Sales): Moderate Spend
    sales_mask = (df['Team'] == 'Sales')
    df.loc[sales_mask, 'Amount'] *= 2.0
    
    return df.sort_values('Date')
