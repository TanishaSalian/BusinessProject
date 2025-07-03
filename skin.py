import pandas as pd
import streamlit as st
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud

@st.cache_data
def load_data():
    reviews = pd.read_csv("sephora_review.csv", low_memory=False)
    products = pd.read_csv("product_info.csv", low_memory=False)

    
    reviews.columns = reviews.columns.str.strip().str.lower()
    products.columns = products.columns.str.strip().str.lower()




    for df in [reviews, products]:
        if "product_id" not in df.columns:
            st.error("Missing 'product_id' column.")
            st.stop()
        df["product_id"] = df["product_id"].astype(str)

    if "price_usd" not in products.columns:
        if "sale_price_usd" in products.columns:
            products["price_usd"] = products["sale_price_usd"]
        elif "value_price_usd" in products.columns:
            products["price_usd"] = products["value_price_usd"]
        else:
            products["price_usd"] = 0.0

  
    default_cols = {
        "sephora_exclusive": False,
        "limited_edition": False,
        "new": False,
        "size": "unknown",
        "primary_category": "unknown"
    }
    for col, default in default_cols.items():
        if col not in products.columns:
            products[col] = default

    return reviews, products


st.set_page_config(page_title="Sephora Review Explorer", layout="wide", page_icon="💄")

st.image("sephora.png", use_column_width=True)


reviews, products = load_data()

merged_columns = [col for col in products.columns if col in [
    "product_id", "brand_name", "product_name", "price_usd",
    "sephora_exclusive", "limited_edition", "new", "size", "primary_category"
]]


data = reviews.drop(columns=["brand_name", "product_name"], errors="ignore").merge(
    products[merged_columns], on="product_id", how="left"
)


if "price_usd_y" in data.columns:
    data["price_usd"] = pd.to_numeric(data["price_usd_y"], errors="coerce").fillna(0.0)
elif "price_usd_x" in data.columns:
    data["price_usd"] = pd.to_numeric(data["price_usd_x"], errors="coerce").fillna(0.0)
else:
    data["price_usd"] = 0.0


data = data.drop(columns=["price_usd_x", "price_usd_y"], errors="ignore")


data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
data["review_text"] = data["review_text"].astype(str)
data["sentiment_score"] = data["review_text"].apply(lambda x: TextBlob(x).sentiment.polarity)
data["submission_time"] = pd.to_datetime(data["submission_time"], errors="coerce")


with st.sidebar:
    st.title("Filters")
    brands = ["All"] + sorted(data["brand_name"].dropna().unique())
    selected_brand = st.selectbox("Brand", brands)

    skins = ["All"]
    if "skin_type" in data.columns:
        skins += sorted(data["skin_type"].dropna().unique())
    selected_skin = st.selectbox("Skin Type", skins)

    exclusive_only = st.checkbox("Sephora Exclusive")
    limited_edition = st.checkbox("Limited Edition")
    new_only = st.checkbox("New Products")

    min_price = float(data["price_usd"].min())
    max_price = float(data["price_usd"].max())
    price_range = st.slider("Price Range (USD)", min_price, max_price, (min_price, max_price))

    min_rating = st.slider("Minimum Rating", 1.0, 5.0, 1.0, 0.5)
    search_query = st.text_input("Search Keyword")

    min_date = data["submission_time"].min()
    max_date = data["submission_time"].max()
    date_range = st.date_input("Review Date Range", (min_date, max_date))


filtered_data = data.copy()
if selected_brand != "All":
    filtered_data = filtered_data[filtered_data["brand_name"] == selected_brand]
if selected_skin != "All":
    filtered_data = filtered_data[filtered_data["skin_type"] == selected_skin]
if exclusive_only:
    filtered_data = filtered_data[filtered_data["sephora_exclusive"] == True]
if limited_edition:
    filtered_data = filtered_data[filtered_data["limited_edition"] == True]
if new_only:
    filtered_data = filtered_data[filtered_data["new"] == True]

filtered_data = filtered_data[
    (filtered_data["price_usd"] >= price_range[0]) &
    (filtered_data["price_usd"] <= price_range[1]) &
    (filtered_data["rating"] >= min_rating) &
    (filtered_data["submission_time"] >= pd.to_datetime(date_range[0])) &
    (filtered_data["submission_time"] <= pd.to_datetime(date_range[1]))
]

if search_query:
    filtered_data = filtered_data[filtered_data["review_text"].str.contains(search_query, case=False, na=False)]

if filtered_data.empty:
    st.warning("No data found for the selected filters.")
    st.stop()


st.title("Analytics Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Avg Rating", f"{filtered_data['rating'].mean():.2f}")
col2.metric("Avg Sentiment", f"{filtered_data['sentiment_score'].mean():.2f}")
col3.metric("Total Reviews", len(filtered_data))

avg_score = filtered_data["sentiment_score"].mean()
summary = "Mostly Neutral"
if avg_score > 0.5:
    summary = "Overall Positive"
elif avg_score < -0.2:
    summary = "Generally Negative"

st.success(f"Sentiment Summary: **{summary}**")

st.markdown("### Rating Distribution")
st.bar_chart(filtered_data["rating"].value_counts().sort_index())

if selected_brand == "All":
    st.markdown("### Top 10 Brands by Rating")
    st.bar_chart(filtered_data.groupby("brand_name")["rating"].mean().nlargest(10))

    st.markdown("### Top 10 Brands by Sentiment")
    st.bar_chart(filtered_data.groupby("brand_name")["sentiment_score"].mean().nlargest(10))

st.markdown("### Top 10 Products by Rating")
st.bar_chart(filtered_data.groupby("product_name")["rating"].mean().nlargest(10))


st.markdown("### Sentiment Trend Over Time")
filtered_data["review_month"] = filtered_data["submission_time"].dt.to_period("M")
trend = filtered_data.groupby("review_month")["sentiment_score"].mean()
fig, ax = plt.subplots()
trend.plot(ax=ax, color="lime")
ax.set_ylabel("Average Sentiment")
st.pyplot(fig)

if "size" in filtered_data.columns:
    st.markdown("### Sentiment by Product Size")
    st.bar_chart(filtered_data.groupby("size")["sentiment_score"].mean().nlargest(10))

if "primary_category" in data.columns:
    categories = ["All"] + sorted(data["primary_category"].dropna().unique())
    selected_cat = st.sidebar.selectbox("Primary Category", categories)
    if selected_cat != "All":
        filtered_data = filtered_data[filtered_data["primary_category"] == selected_cat]

    st.markdown("### Top Categories by Rating")
    st.bar_chart(filtered_data.groupby("primary_category")["rating"].mean().nlargest(10))


st.markdown("### WordCloud of Positive Reviews")
text = " ".join(filtered_data[filtered_data["sentiment_score"] > 0.5]["review_text"].dropna())
if text.strip():
    wc = WordCloud(width=800, height=400, background_color="white", colormap="plasma").generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)
else:
    st.info("No positive reviews found.")


st.markdown("### Most Positive Reviews")
top_reviews = filtered_data.sort_values("sentiment_score", ascending=False).head(3)
for _, row in top_reviews.iterrows():
    st.write(f"**Sentiment Score: {row['sentiment_score']:.2f}**")
    st.write(row["review_text"])
    st.markdown("---")

st.markdown("### Most Controversial Reviews")
cont_reviews = filtered_data[(filtered_data["sentiment_score"] > 0.5) & (filtered_data["rating"] <= 2)].sort_values("sentiment_score", ascending=False).head(3)
for _, row in cont_reviews.iterrows():
    st.write(f"**Sentiment Score: {row['sentiment_score']:.2f}**")
    st.write(row["review_text"])
    st.markdown("---")


if "total_pos_feedback_count" in filtered_data.columns:
    st.markdown("### Most Helpful Reviews")
    helpful = filtered_data.sort_values("total_pos_feedback_count", ascending=False).head(3)
    for _, row in helpful.iterrows():
        st.info(f"{row['total_pos_feedback_count']} helpful votes | {row['rating']} Stars")
        st.write(row["review_text"])
        st.markdown("---")


st.markdown("### Download Filtered Data")
csv = filtered_data.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_reviews.csv", "text/csv")
