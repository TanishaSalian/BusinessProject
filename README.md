# Sephora Dashboard

The Sephora Dashboard is a Streamlit-based interactive dashboard that analyzes customer reviews from Sephora. The application merges review data with product information to generate insights such as average sentiment, top-rated products, and trends over time.

## Features

- Filter reviews by brand, skin type, product category, price range, and other attributes
- Analyze review sentiment using TextBlob
- Visualize rating distribution and sentiment trends over time
- Identify top-rated and most positively reviewed products
- Display frequently used words in positive reviews using a WordCloud
- Export filtered reviews as a CSV file

## Dataset Description

This application relies on two CSV files:

1. `sephora_review.csv`: Contains customer review details such as rating, review text, skin type, and product ID
2. `product_info.csv`: Contains product metadata including brand name, price, size, category, and other attributes

Make sure both files are placed in the same directory as the Python script.
## Important Note
the csv file is bigger than 10MB, hence has been slpit into differnet chunks of csv. If the original file is requires. it can be found at https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews

## Future Scope
While code for dark mode toggle has been implemented, it was been able to apply in the dashboard due to Streamlitt restriction and time constraints to fulfil the code. This is still a ongoing project and would be requiring a lot of time to implment it.


## Setup Instructions

### Prerequisites

Make sure you have Python 3.7 or later installed. Then, install the required Python libraries:

```bash
pip install streamlit pandas textblob matplotlib wordcloud

