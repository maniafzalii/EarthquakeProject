import os
from pathlib import Path
import pandas as pd

def emsc_cleanup():
    current_path = Path(__file__).resolve()  
    root=current_path.parent.parent
    file_csv_path=root/'data'/'raw'/'JAPAN_EMSC.csv'
    if file_csv_path.exists():
        data_frame=pd.read_csv(file_csv_path)
        data_frame.columns = (
            data_frame.columns
            .str.strip()
            .str.lower()
            .str.replace('\ufeff', '')
        )
        standard_columns = ['time', 'latitude', 'longitude', 'depth', 'magnitude', 'place', 'source']
        
        for col in standard_columns:
            if col not in data_frame.columns:
                if col=='source':
                   data_frame['source']='emsc'
                else:
                    data_frame[col]=None

        final_emsc=data_frame[standard_columns]
        
        clean_path=root/'data'/'clean'
        clean_path.mkdir(parents=True, exist_ok=True)
        clean_file_path=clean_path/'cleaned_emsc.csv'  
        final_emsc.to_csv(clean_file_path,index=False)             
      