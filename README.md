1) Create a Postgresql database (like "earthquake_db").
2) Create a ".env" file in the project root and write this: (ex. for earthquake_db in step 1)
DATABASE_URL=postgresql+psycopg2://USERNAME:PASSWORD@localhost:5432/earthquake_db
3) Install dependencies:
pip install -r requirements.txt
4) Run the pipeline:
python main.py

During execution:
- Data gets extracted from sources to CSV files
- Preprocessing applies to the CSV files
- Table with "earthquakes" name gets created
- All CSV files insert into the table
- Reports and charts will be available in the end 