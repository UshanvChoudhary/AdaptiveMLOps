import pandas as pd
from pydantic import ValidationError
from app.ml.schema import TicketData

def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    
    df = df.dropna(subset=['text', 'intent'])
    df = df.drop_duplicates()
    
    valid_rows = []
    for record in df.to_dict(orient="records"):
        try:
            TicketData(**record)
            valid_rows.append(record)
        except ValidationError:
            pass
            
    return pd.DataFrame(valid_rows)
