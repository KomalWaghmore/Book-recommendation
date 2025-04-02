from flask import Flask, render_template, request, redirect, url_for, flash
import pickle
import numpy as np
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "Kw@814936"

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

@app.route('/recommend_books', methods=['POST'])
def recommend():
    title_input = request.form.get('title')
    author_input = request.form.get('author')
    genre_input = request.form.get('genre')

    data = []

    # 📚 Recommend based on book title
    if title_input and title_input in pt.index:
        index = np.where(pt.index == title_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:9]

        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

            title = temp_df['Book-Title'].values[0]
            author = temp_df['Book-Author'].values[0]
            image = temp_df['Image-URL-M'].values[0]

            # Get votes & rating
            book_details = popular_df[popular_df['Book-Title'] == title]
            votes = int(book_details['num_ratings'].values[0]) if not book_details.empty else 0
            rating = float(book_details['avg_rating'].values[0]) if not book_details.empty else 0

            data.append([title, author, image, votes, rating])

    # 👤 Recommend based on author
    if author_input:
        author_books = books[books['Book-Author'].str.contains(author_input, case=False, na=False)].drop_duplicates('Book-Title').head(8)
        for _, row in author_books.iterrows():
            title, author, image = row['Book-Title'], row['Book-Author'], row['Image-URL-M']
            book_details = popular_df[popular_df['Book-Title'] == title]
            votes = int(book_details['num_ratings'].values[0]) if not book_details.empty else 0
            rating = float(book_details['avg_rating'].values[0]) if not book_details.empty else 0
            data.append([title, author, image, votes, rating])

    # 🎭 Recommend based on genre
    if genre_input and 'Genre' in books.columns:
        genre_books = books[books['Genre'].str.contains(genre_input, case=False, na=False)].drop_duplicates('Book-Title').head(8)
        for _, row in genre_books.iterrows():
            title, author, image = row['Book-Title'], row['Book-Author'], row['Image-URL-M']
            book_details = popular_df[popular_df['Book-Title'] == title]
            votes = int(book_details['num_ratings'].values[0]) if not book_details.empty else 0
            rating = float(book_details['avg_rating'].values[0]) if not book_details.empty else 0
            data.append([title, author, image, votes, rating])

    # Remove duplicates
    data = list(map(list, {tuple(i) for i in data}))

    return render_template('recommend.html', data=data)



# ⭐ Book Rating Route
# @app.route('/rate_book', methods=['POST'])
# def rate_book():
#     book_title = request.form['book_title']
#     user_rating = float(request.form['user_rating'])

#     # Append new rating to the DataFrame
#     new_rating = pd.DataFrame({"Book-Title": [book_title], "User-Rating": [user_rating]})
#     global user_ratings
#     user_ratings = pd.concat([user_ratings, new_rating], ignore_index=True)

#     # Save ratings to CSV
#     user_ratings.to_csv(ratings_file, index=False)

#     return redirect(request.referrer)  # Reload the page after rating submission

# @app.route('/contact')
# def contact():
#     return render_template('contact.html')

# @app.route('/submit_contact', methods=['POST'])
# def submit_contact():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     message = request.form.get('message')

#     if not name or not email or not message:
#         flash('All fields are required!', 'danger')
#         return redirect(url_for('contact'))

#     # Here, you can save the data to a database or send an email

#     flash('Your message has been sent successfully!', 'success')
#     return redirect(url_for('contact'))

import csv

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required!', 'danger')
        return redirect(url_for('contact'))

    # Save the contact message to a CSV file
    with open("contact_messages.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, email, message])

    flash('Your message has been sent successfully!', 'success')
    return redirect(url_for('contact'))


# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
