from sqlalchemy import text
from database_setup import get_engine

# Convert columns from text type to proper database types
def convert_column_types(engine):
    try:
        with engine.begin() as conn:

            # Convert time column to timestamp
            conn.execute(text("""
                ALTER TABLE earthquakes
                ALTER COLUMN time TYPE TIMESTAMP USING time::timestamp;
            """))

            # Convert magnitude to float
            conn.execute(text("""
                ALTER TABLE earthquakes
                ALTER COLUMN magnitude TYPE FLOAT USING magnitude::float;        
            """))

            # Convert depth to float
            conn.execute(text("""
                ALTER TABLE earthquakes
                ALTER COLUMN depth TYPE FLOAT USING depth::float;
            """))

            # Optional convert latitude to float
            conn.execute(text("""
                ALTER TABLE earthquakes
                ALTER COLUMN latitude TYPE FLOAT USING latitude::float;
            """))

            # Optional convert longitude to float
            conn.execute(text("""
                ALTER TABLE earthquakes
                ALTER COLUMN longitude TYPE FLOAT USING longitude::float;
            """))

        return True
    
    except Exception as e:
        print(f"Column type conversion failed: {e}")
        return False

# Remove invalid values, handle missing values
def remove_missing_values(engine):
    try:
        with engine.begin() as conn:

            # Remove unrealistic values (Noise)
            conn.execute(text("""
                DELETE FROM earthquakes
                WHERE depth < 0
                    OR depth > 700
                    OR magnitude < 0
                    OR magnitude > 10;
            """))

            print("\nInvalid values removed")

            # Generate missing values report
            result = conn.execute(text("""
                SELECT
                    COUNT(*) FILTER (WHERE time is NULL) AS time_null,
                    COUNT(*) FILTER (WHERE latitude is NULL) AS latitude_null,
                    COUNT(*) FILTER (WHERE longitude is NULL) AS longitude_null,
                    COUNT(*) FILTER (WHERE depth is NULL) AS depth_null,
                    COUNT(*) FILTER (WHERE magnitude is NULL) AS magnitude_null,
                    COUNT(*) FILTER (WHERE place is NULL) AS place_null,
                    COUNT(*) FILTER (WHERE source is NULL) AS source_null
                FROM earthquakes;
            """)).mappings().one()

            print("\nMissing values report:")

            for column, count in result.items():
                print(f"{column}: {count}")

            # Replace missing depth values with median
            conn.execute(text("""
                UPDATE earthquakes
                SET depth = (
                    SELECT percentile_cont(0.5)
                    WITHIN GROUP (ORDER BY depth)
                    FROM earthquakes
                    WHERE depth IS NOT NULL)
                WHERE depth IS NULL;
            """))

            # Replace missing magnitude values with median
            conn.execute(text("""
                UPDATE earthquakes
                SET magnitude = (
                    SELECT percentile_cont(0.5)
                    WITHIN GROUP (ORDER BY magnitude)
                    FROM earthquakes
                    WHERE magnitude IS NOT NULL)
                WHERE magnitude IS NULL;
            """))

            print("\nDepth and Magnitude NULL values replaced with median")

            # Count rows with critical missing values before deletion
            invalid_rows = conn.execute(text("""
                SELECT COUNT(*)
                FROM earthquakes
                WHERE time IS NULL
                    OR latitude IS NULL
                    OR longitude IS NULL
                    OR place IS NULL
                    OR source IS NULL;
            """)).scalar_one()

            print(f"\nInvalid rows before delete: {invalid_rows}")

            # Delete rows with critical missing values
            conn.execute(text("""
                DELETE FROM earthquakes
                WHERE time IS NULL
                    OR latitude IS NULL
                    OR longitude IS NULL
                    OR place IS NULL
                    OR source IS NULL
            """))

            # Check remaining invalid rows
            invalid_rows = conn.execute(text("""
                SELECT COUNT(*)
                FROM earthquakes
                WHERE time IS NULL
                    OR latitude IS NULL
                    OR longitude IS NULL
                    OR place IS NULL
                    OR source IS NULL;
            """)).scalar_one()

            print(f"\nInvalid rows after delete: {invalid_rows}")            

        return True
    
    except Exception as e:
        print(f"Remove missing values failed: {e}")
        return False

# Remove duplicated records    
def remove_duplicate_rows(engine):
    try:
        with engine.begin() as conn:

            # Count duplicate groups
            duplicates = conn.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT time, latitude, longitude, depth, magnitude, place, source,
                        COUNT(*) AS cnt
                    FROM earthquakes
                    GROUP BY time, latitude, longitude, depth, magnitude, place, source
                    HAVING COUNT(*) > 1) AS d;
            """)).scalar_one()

            print(f"\nDuplicate groups found: {duplicates}")

            # Delete duplicated rows and keep the row with the smallest id
            conn.execute(text("""
                DELETE FROM earthquakes
                WHERE id NOT IN(
                    SELECT MIN(id)
                    FROM earthquakes
                    GROUP BY time, latitude, longitude, depth, magnitude, place, source);
            """))

        return True
    
    except Exception as e:
        print(f"Removing duplicates failed: {e}")
        return False

# Create month feature from earthquakes time
def create_month_column(engine):
    try:
        with engine.begin() as conn:

            conn.execute(text("""
                ALTER TABLE earthquakes
                ADD COLUMN IF NOT EXISTS month INT;
            """))

            conn.execute(text("""
                UPDATE earthquakes
                SET month = EXTRACT(MONTH FROM time)::INT;
            """))

        return True
    
    except Exception as e:
        print(f"Creating month column failed: {e}")
        return False

# Create earthquake magnitude category
def create_category_column(engine):
    try:
        with engine.begin() as conn:

            conn.execute(text("""
                ALTER TABLE earthquakes
                ADD COLUMN IF NOT EXISTS category VARCHAR(20);
            """))

            conn.execute(text("""
                UPDATE earthquakes
                SET category = CASE
                    WHEN magnitude < 4 THEN 'Weak'
                    WHEN magnitude BETWEEN 4 AND 6 THEN 'Moderate'
                    WHEN magnitude > 6 THEN 'Strong'
                    ELSE 'Unknown'
                END;
            """))

        return True
    
    except Exception as e:
        print(f"Creating category Column failed: {e}")
        return False

# Extract region from place column
def create_region_column(engine):
    try:
        with engine.begin() as conn:

            conn.execute(text("""
                ALTER TABLE earthquakes
                ADD COLUMN IF NOT EXISTS region VARCHAR(255);
            """))

            conn.execute(text("""
                UPDATE earthquakes
                SET region = SPLIT_PART(place, ',', 1);
            """))

        return True
    
    except Exception as e:
        print(f"Creating region column failed: {e}")
        return False

# Run complete cleaning pipeine
def database_cleanup():

    engine, res = get_engine()

    if not res:
        print("Database connection failed")
        return False

    if not convert_column_types(engine):
        print("Column type conversion failed")
        return False

    print("\nColumn types converted")


    if not remove_missing_values(engine):
        print("Removing missing values failed")
        return False

    print("\nMissing values cleaned")

    if not remove_duplicate_rows(engine):
        print("Removing duplicates failed")
        return False

    print("\nDuplicated rows removed")

    if not create_month_column(engine):
        print("Creating month column failed")
        return False

    print("\nMonth column created")

    if not create_category_column(engine):
        print("Creating category column failed")
        return False

    print("\nCategory column created")

    if not create_region_column(engine):
        print("Creating region column failed")
        return False

    print("\nRegion column created")

    print("\nDatabase cleanup completed successfully")

    return True

if __name__ == "__main__":
    database_cleanup()
    