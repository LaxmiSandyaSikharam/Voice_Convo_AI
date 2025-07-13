import pandas as pd
import re
from fuzzywuzzy import fuzz

def sanitize_currency_column(df, column):
    df[column] = (
        df[column]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .replace("", "0")
        .astype(float)
    )
    return df

def match_price_filters(df, user_query):
    query = user_query.lower()
    df = df.copy()

    if "annual rent" in query:
        df = sanitize_currency_column(df, "Annual Rent")
        if "maximum" in query or "highest" in query:
            return df[df["Annual Rent"] == df["Annual Rent"].max()]
        elif "minimum" in query or "lowest" in query:
            return df[df["Annual Rent"] == df["Annual Rent"].min()]

    elif "gci" in query:
        df = sanitize_currency_column(df, "GCI On 3 Years")
        if "maximum" in query or "highest" in query:
            return df[df["GCI On 3 Years"] == df["GCI On 3 Years"].max()]
        elif "minimum" in query or "lowest" in query:
            return df[df["GCI On 3 Years"] == df["GCI On 3 Years"].min()]

    elif "rent/sf/year" in query:
        df = sanitize_currency_column(df, "Rent/SF/Year")
        if "maximum" in query or "highest" in query:
            return df[df["Rent/SF/Year"] == df["Rent/SF/Year"].max()]
        elif "minimum" in query or "lowest" in query:
            return df[df["Rent/SF/Year"] == df["Rent/SF/Year"].min()]

    return pd.DataFrame()

def match_associates(df, user_query):
    for i in range(1, 5):
        col = f"Associate {i}"
        for name in df[col].dropna().unique():
            if name.lower() in user_query.lower():
                return df[df[col].str.lower() == name.lower()]
    return pd.DataFrame()

def match_floor_suite_property(df, user_query):
    floors = re.findall(r'floor\s+([a-zA-Z0-9]+)', user_query.lower())
    suites = re.findall(r'suite\s+([a-zA-Z0-9]+)', user_query.lower())

    floor_matches = df[df["Floor"].str.lower().isin(floors)] if floors else pd.DataFrame()
    suite_matches = df[df["Suite"].str.lower().isin(suites)] if suites else pd.DataFrame()

    return pd.concat([floor_matches, suite_matches]).drop_duplicates()

def match_property_name(df, user_query, threshold=80):
    property_matches = []
    for address in df["Property Address"].dropna().unique():
        score = fuzz.partial_ratio(user_query.lower(), address.lower())
        if score >= threshold:
            property_matches.append(address)

    if property_matches:
        return df[df["Property Address"].isin(property_matches)]
    return pd.DataFrame()

def parse_and_filter(df, user_query):
    base_df = df.copy()
    price_filtered = match_price_filters(base_df, user_query)
    associate_filtered = match_associates(base_df, user_query)
    floor_suite_filtered = match_floor_suite_property(base_df, user_query)
    property_filtered = match_property_name(base_df, user_query)

    filters = [price_filtered, associate_filtered, floor_suite_filtered, property_filtered]
    filters = [f for f in filters if not f.empty]

    if filters:
        # Combine all non-empty filtered dataframes
        combined_df = pd.concat(filters).drop_duplicates().reset_index(drop=True)
        return combined_df

    return None
