import re
import streamlit as st
import pandas as pd

# ---------- DATA LOADING ----------
@st.cache_data
def load_data():
    """
    Load the CSV you uploaded and pull out the four fields we need:
    drug_name, dose (strength), form, route.
    """
    df = pd.read_csv("drugs.csv")          # ← file you just uploaded

    # 1️⃣  Rename columns we care about
    df = df.rename(
        columns={
            "brand_name": "drug_name",
            "dosage_form": "form"
        }
    )

    # 2️⃣  Extract the first strength that appears inside parentheses
    #     in the "active_ingredients" field  → e.g., "(30MG)" or "(0.125MG)"
    strength_re = re.compile(r"\(([^)]+)\)")
    df["dose"] = (
        df["active_ingredients"]
        .str.extract(strength_re, expand=False)  # returns NaN if no match
        .fillna("")                              # keep blanks if no strength
        .str.replace(r"\s+", "", regex=True)     # trim stray spaces
    )

    # 3️⃣  Keep the four columns we need and drop duplicates
    return (
        df[["drug_name", "dose", "form", "route"]]
        .dropna(subset=["drug_name"])
        .drop_duplicates()
        .reset_index(drop=True)
    )

data = load_data()

# ---------- STREAMLIT UI ----------
st.title("💊 Prescription Generator")

# Build a friendly label: "Morphine Sulfate 30MG (Tablet, ORAL)"
data["label"] = (
    data["drug_name"]
    + " "
    + data["dose"]
    + " (" + data["form"].fillna("") + ", " + data["route"].fillna("") + ")"
)

# Dropdown of all available drugs
choice = st.selectbox("Select a medication:", sorted(data["label"]))

# Retrieve the chosen row
drug = data[data["label"] == choice].iloc[0]

# ---------- PRESCRIPTION TEMPLATE ----------
rx_text = f"""
RX: {drug.drug_name} {drug.dose}
TAKE: 1 {drug.form} via {drug.route} every 6 hours as needed for pain.
"""

st.subheader("📝 Generated Prescription")
st.code(rx_text.strip(), language="markdown")