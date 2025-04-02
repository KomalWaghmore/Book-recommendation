from flask import Flask, render_template, request, redirect
import pickle
import numpy as np
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)

# Load pickled data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# User Ratings CSV File
ratings_file = "user_ratings.csv"

# Load or create user ratings DataFrame
if os.path.exists(ratings_file):
    user_ratings = pd.read_csv(ratings_file)
else:
    user_ratings = pd.DataFrame(columns=["Book-Title", "User-Rating"])
    user_ratings.to_csv(ratings_file, index=False)

# 🏠 Home Route - Display Popular Books with Ratings
@app.route('/')
def index():
    # Calculate average user ratings
    avg_ratings = user_ratings.groupby('Book-Title')['User-Rating'].mean().reset_index()
    
    # Merge with popular books data
    popular_df_with_ratings = popular_df.merge(avg_ratings, on="Book-Title", how="left").fillna(0)

    return render_template('index.html',
                           book_name=list(popular_df_with_ratings['Book-Title'].values),
                           author=list(popular_df_with_ratings['Book-Author'].values),
                           image=list(popular_df_with_ratings['Image-URL-M'].values),
                           votes=list(popular_df_with_ratings['num_ratings'].values),
                           rating=list(popular_df_with_ratings['avg_rating'].values),
                           user_rating=list(popular_df_with_ratings['User-Rating'].values)  # New column for user ratings
                           )

# 📚 Recommendation Page Route
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

# 🔍 Book Recommendation Logic
@app.route('/recommend_books', methods=['POST'])
def recommend():
    title_input = request.form.get('title')
    author_input = request.form.get('author')
    genre_input = request.form.get('genre')

    data = []

    # Filter based on book title
    if title_input and title_input in pt.index:
        index = np.where(pt.index == title_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]

        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['num_ratings'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['avg_rating'].values))
            data.append(item)

    # Filter based on author
    if author_input:
        author_books = books[books['Book-Author'].str.contains(author_input, case=False, na=False)].head(5)
        for _, row in author_books.iterrows():
            data.append([row['Book-Title'], row['Book-Author'], row['Image-URL-M'], row['num_ratings'], row['avg_rating']])

    # Filter based on genre (if available)
    if genre_input and 'Genre' in books.columns:
        genre_books = books[books['Genre'].str.contains(genre_input, case=False, na=False)].head(5)
        for _, row in genre_books.iterrows():
            data.append([row['Book-Title'], row['Book-Author'], row['Image-URL-M'], row['num_ratings'], row['avg_rating']])

    # Remove duplicates
    data = list(map(list, {tuple(i) for i in data}))

    return render_template('recommend.html', data=data)

# ⭐ Book Rating Route
@app.route('/rate_book', methods=['POST'])
def rate_book():
    book_title = request.form['book_title']
    user_rating = float(request.form['user_rating'])

    # Append new rating to the DataFrame
    new_rating = pd.DataFrame({"Book-Title": [book_title], "User-Rating": [user_rating]})
    global user_ratings
    user_ratings = pd.concat([user_ratings, new_rating], ignore_index=True)

    # Save ratings to CSV
    user_ratings.to_csv(ratings_file, index=False)

    return redirect(request.referrer)  # Reload the page after rating submission

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
