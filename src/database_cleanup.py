from sqlalchemy import text
from src.database_setup import get_engine
import unicodedata
import re

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

            def extract_region(place):

                if place is None:
                    return None

                place = place.strip()

                # Normalize unicode characters
                place = unicodedata.normalize("NFKD", place)
                place = "".join(
                    char for char in place
                    if not unicodedata.combining(char)
                )

                # Remove country only for Japan
                parts = place.split(",")

                if len(parts) > 1:
                    country = parts[1].strip().lower()

                    if country.startswith("japan"):
                        place = ",".join(parts[:-1]).strip()

                    else:
                        place = place.strip()

                else:
                    place = place.strip()

                # Convert abbreviation
                place = re.sub(r"\bisl\.", "islands", place, flags = re.I)
                lower_place = place.lower()

                # Keep special multi-word regions
                special_regions = [
                    "bonin islands",
                    "izu islands",
                    "ryukyu islands",
                    "volcano islands",
                    "sea of japan"
                ]

                if lower_place in special_regions:
                    return place.upper()

                # Remove distance + direction
                match = re.search(r"\bof\s+(.+)", place, flags=re.I)

                if match:
                    place = match.group(1).strip()

                lower_place = place.lower()

                # Remove near
                if lower_place.startswith("near "):
                    place = place[5:].strip()

                # Remove coast phrases
                match = re.search(r"coast of\s+(.+)", place, flags=re.I)

                if match:
                    place = match.group(1).strip()

                # Check special regions again
                lower_place = place.lower()

                if lower_place in special_regions:
                    return place.upper()

                # Remove directional prefixes
                words = place.split()

                if len(words) > 1 and words[0].lower() in [
                    "eastern",
                    "western",
                    "southern",
                    "northern",
                    "southwestern",
                    "northwestern",
                    "central"
                ]:
                    place = " ".join(words[1:])

                lower_place = place.lower()

                # Remove prefecture
                if lower_place.endswith(" prefecture"):
                    place = place.split()[0]


                # Remove region
                elif lower_place.endswith(" region"):
                    place = place.split(" ", 1)[0]

                # Remove year prefix
                words = place.split()

                if words and words[0].isdigit():
                    place = " ".join(words[1:])

                # Remove earthquake suffix
                place = re.sub(r",?\s*japan earthquake.*$", "", place, flags = re.I)

                # Remove extra commas
                place = place.strip(" ,")

                # Handle combined Japanese regions
                if "," in place:
                    parts = [p.strip() for p in place.split(",")]

                    if parts[-1].lower() in [
                        "ryukyu islands",
                        "bonin islands",
                        "izu islands",
                        "volcano islands",
                        "sea of japan"
                    ]:
                        place = parts[-1]

                return place.upper()

            rows = conn.execute(text("""
                SELECT id, place
                FROM earthquakes;
            """)).fetchall()


            for row in rows:

                region = extract_region(row.place)

                conn.execute(text("""
                    UPDATE earthquakes
                    SET region = :region
                    WHERE id = :id;
                """),
                {
                    "region": region,
                    "id": row.id
                })

            # Use to find patterns
            # result = conn.execute(text("""
            #     SELECT id, place, region
            #     FROM earthquakes
            #     WHERE region IS NOT NULL
            #         AND array_length(string_to_array(region, ' '), 1) > 1
            #     ORDER BY region;
            # """))

            # print("\nRegions that are still multi-word:\n")

            # for row in result:
            #     print(f"{row.id} | {row.region} | {row.place}")

            # Check final unique regions

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
    