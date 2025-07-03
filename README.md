 ## Sephora Dashboard

The Sephora Review Explorer is a Streamlit-based interactive dashboard that analyzes customer reviews from Sephora. The application merges review data with product information to generate insights such as average sentiment, top-rated products, and trends over time.

## Features

- Filter reviews by brand, skin type, product category, price range, and other attributes
- Analyzes review sentiment using TextBlob
- Visualizes rating distribution and sentiment trends over time
- Identifies top-rated and most positively reviewed products
- Display frequently used words in positive reviews using a WordCloud
- Exports filtered reviews as a CSV file

## Dataset Description

This application relies on two CSV files:

1. `sephora_review.csv`: Contains customer review details such as rating, review text, skin type, and product ID
2. `product_info.csv`: Contains product metadata including brand name, price, size, category, and other attributes

Make sure both files are placed in the same directory as the Python script.



### Prerequisites

Make sure you have Python 3.7 or later installed. Then, install the required Python libraries:

pip install streamlit pandas textblob matplotlib wordcloud
