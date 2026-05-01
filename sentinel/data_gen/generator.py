import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()

def generate_sentinel_data(client_name="Marlow & Finch Coffee", num_records=10000):
    """
    Generates realistic Gift Card Network data.
    """
    merchant_list = ["Marlow & Finch Coffee", "Marlow & Finch Express", "M&F Airport", "M&F Drive-Thru"]
    locations = ["Urban Centers", "Suburban", "Airport", "Drive-Thru", "Pacific NW", "East Coast"]
    
    data = []
    start_date = datetime.now() - timedelta(days=180) # 6 months of data
    
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 180))
        location = random.choice(locations)
        merchant = random.choice(merchant_list)
        
        # Gift card amounts: Standard denominations
        amount = random.choice([5, 10, 20, 25, 50, 100])
        
        # Seed Seasonality: Holiday spikes in Nov/Dec
        if date.month in [11, 12]:
            amount *= 1.4
            
        data.append({
            "TransactionID": f"GC-{random.randint(100000, 999999)}",
            "Date": date,
            "Merchant": merchant,
            "Location": location,
            "Amount": round(amount, 2),
            "Type": "Redemption" if random.random() > 0.3 else "Issuance"
        })
        
    df = pd.DataFrame(data)
    os.makedirs("data/synthetic", exist_ok=True)
    df.to_parquet("data/synthetic/gift_card_network.parquet")
    return df

if __name__ == "__main__":
    generate_sentinel_data()
