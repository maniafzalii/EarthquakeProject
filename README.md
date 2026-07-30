1) Create a Postgresql database (like "earthquake_db").
2) Create a ".env" file in the project root and add: (for earthquake_db in step 1)
DATABASE_URL=postgresql+psycopg2://USERNAME:PASSWORD@localhost:5432/earthquake_db
3) Install dependencies:
pip install -r requirements.txt
4) Run the pipeline:
python main.py

During execution:
- downloads data from sources
- cleans the CSVs and drops and recreates the "earthquakes" table
- inserts all cleaned files into Postgresql
- gives you the reports you wanted