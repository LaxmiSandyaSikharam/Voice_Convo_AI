import pandas as pd
import re
from rapidfuzz import fuzz  # type: ignore # ✅ Using RapidFuzz (faster, better maintained)

# === Utility to clean $ and commas ===
def sanitize_currency_column(df, column):
    """Convert currency-like strings like '$847,890' -> 847890.0"""
    if column not in df.columns:
        print(f"⚠ Column '{column}' not found in dataset!")
        return df
    df[column] = (
        df[column]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)  # remove $, commas, etc.
        .replace("", "0")
        .astype(float)
    )
    return df

# === Extract numeric value from query ===
def extract_numeric_value(user_query: str):
    """Extract first numeric like '$70,000' -> 70000.0"""
    match = re.search(r"([\d,.]+)", user_query)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

# === Detect correct numeric column ===
def detect_rent_column(df, user_query):
    """Find the most relevant column based on the query text."""
    query = user_query.lower()

    if "gci" in query:
        return next((c for c in df.columns if "gci" in c.lower()), "GCI On 3 Years")
    elif "sf" in query or "per sf" in query:
        return next((c for c in df.columns if "sf/year" in c.lower()), "Rent/SF/Year")
    elif "monthly" in query:
        return next((c for c in df.columns if "monthly" in c.lower()), "Monthly Rent")
    else:
        # Default to Annual Rent
        return next((c for c in df.columns if "annual rent" in c.lower()), "Annual Rent")

# === Main price-based filtering ===
def match_price_filters(df, user_query):
    query = user_query.lower()
    df = df.copy()

    # ✅ Normalize columns (strip $, (), spaces)
    df.columns = df.columns.str.strip().str.replace(r'[$()]', '', regex=True)
    print(f"✅ Columns after normalization: {df.columns.tolist()}")

    # ✅ Detect column dynamically
    col = detect_rent_column(df, query)
    print(f"🛠 Filtering column: {col}")

    # ✅ Ensure numeric conversion
    df = sanitize_currency_column(df, col)
    print(f"🛠 Sample values in {col} after sanitize:\n{df[col].head()}")

    # ✅ highest/lowest keywords
    if "maximum" in query or "highest" in query:
        print("🛠 Detected: HIGHEST filter")
        return df[df[col] == df[col].max()]
    elif "minimum" in query or "lowest" in query:
        print("🛠 Detected: LOWEST filter")
        return df[df[col] == df[col].min()]

    # ✅ Extract numeric threshold
    numeric_value = extract_numeric_value(query)
    print(f"🛠 Extracted numeric value: {numeric_value}")

    if numeric_value:
        if any(x in query for x in ["below", "under", "less than"]):
            print(f"🛠 Applying <= {numeric_value}")
            return df[df[col] <= numeric_value]
        elif any(x in query for x in ["above", "over", "greater than", "more than"]):
            print(f"🛠 Applying >= {numeric_value}")
            return df[df[col] >= numeric_value]

    print("🛠 No numeric filtering applied.")
    return pd.DataFrame()

# === Filter by associate names ===
def match_associates(df, user_query):
    for i in range(1, 5):
        col = f"Associate {i}"
        if col in df.columns:
            for name in df[col].dropna().unique():
                if name.lower() in user_query.lower():
                    return df[df[col].str.lower() == name.lower()]
    return pd.DataFrame()

# === Filter by Floor/Suite ===
def match_floor_suite_property(df, user_query):
    floors = re.findall(r'floor\s+([a-zA-Z0-9]+)', user_query.lower())
    suites = re.findall(r'suite\s+([a-zA-Z0-9]+)', user_query.lower())

    floor_matches = df[df["Floor"].str.lower().isin(floors)] if floors else pd.DataFrame()
    suite_matches = df[df["Suite"].str.lower().isin(suites)] if suites else pd.DataFrame()

    return pd.concat([floor_matches, suite_matches]).drop_duplicates()

# === Fuzzy match property name ===
def match_property_name(df, user_query, threshold=80):
    property_matches = []
    if "Property Address" in df.columns:
        for address in df["Property Address"].dropna().unique():
            score = fuzz.partial_ratio(user_query.lower(), address.lower())
            if score >= threshold:
                property_matches.append(address)

    if property_matches:
        return df[df["Property Address"].isin(property_matches)]
    return pd.DataFrame()

# ✅ ADD THIS HELPER FUNCTION HERE
def format_property_results(df):
    """Format property rows into a clean bullet list for GPT."""
    results = []
    for _, row in df.iterrows():
        results.append(
            f"- {row['Property Address']} (Floor {row['Floor']}, Suite {row['Suite']}) → "
            f"${row['Monthly Rent']:,.0f}/month, Size {row['Size SF']} SF"
        )
    return "\n".join(results)


# === Main entry point ===
def parse_and_filter(df, user_query):
    """Try multiple filters and combine non-empty ones."""
    base_df = df.copy()

    # ✅ Normalize columns globally first
    base_df.columns = base_df.columns.str.strip().str.replace(r'[$()]', '', regex=True)
    print("✅ Normalized Columns:", base_df.columns.tolist())

    # ✅ Run all filters
    price_filtered = match_price_filters(base_df, user_query)
    associate_filtered = match_associates(base_df, user_query)
    floor_suite_filtered = match_floor_suite_property(base_df, user_query)
    property_filtered = match_property_name(base_df, user_query)

    filters = [price_filtered, associate_filtered, floor_suite_filtered, property_filtered]
    filters = [f for f in filters if not f.empty]

    if filters:
        combined_df = pd.concat(filters).drop_duplicates().reset_index(drop=True)
        print(f"✅ Returning {len(combined_df)} matching rows")
        return combined_df

    print("⚠ No filters matched, returning None")
    return None
