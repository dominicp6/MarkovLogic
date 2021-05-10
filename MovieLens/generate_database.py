#Script to generate the MovieLens relational database for structure learning
import os
import pandas as pd

NUMBER_USERS = 6040
NUMBER_MOVIES = 3952

def read_movies_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['MovieID', 'MovieTitle', 'MovieGenres'], engine='python')
    return DataFrame 

def read_users_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'ZipCode'], engine='python')
    return DataFrame

def read_ratings_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python')
    return DataFrame 

def write_movie_ground_atoms_to_file(data_frame, file, scale):
    for index,row in data_frame.iterrows():
        if row['MovieID'] < NUMBER_MOVIES * scale:
            for genre in row['MovieGenres'].split('|'):
                file.write(f"{genre}(M{row['MovieID']})\n")

def write_user_ground_atoms_to_file(data_frame, file, scale):
    for index,row in data_frame.iterrows():
        if row['UserID'] < NUMBER_USERS * scale:
            male = "M"
            female = "F"
            if row['Gender'] == male:
                file.write(f"Male(U{row['UserID']})\n")
            elif row['Gender'] == female:
                file.write(f"Female(U{row['UserID']})\n")
            
            age = row['Age']
            if age in [1, 18, 25]:
                file.write(f"Youthful(U{row['UserID']})\n")
            elif age in [35, 45, 50]:
                file.write(f"MiddleAged(U{row['UserID']})\n")
            elif age == 56:
                file.write(f"Old(U{row['UserID']})\n")

def write_ratings_ground_atoms_to_file(data_frame, file, scale):
    for index,row in data_frame.iterrows():
        if row['UserID'] < NUMBER_USERS * scale and row['MovieID'] < NUMBER_MOVIES * scale:
            if row['Rating'] >=4:
                rating = 'Positive'
            elif row['Rating'] == 3:
                rating = 'Indifferent'
            elif row['Rating'] <= 2:
                rating = 'Negative'
            file.write(f"Rating(U{row['UserID']},M{row['MovieID']},{rating})\n")

def import_data(directory):
    movies_file = os.path.join(directory, 'movies.dat')
    users_file = os.path.join(directory, 'users.dat')
    ratings_file = os.path.join(directory, 'ratings.dat')

    print('Importing files...')
    movie_data_frame = read_movies_file(movies_file)
    user_data_frame = read_users_file(users_file)
    ratings_data_frame = read_ratings_file(ratings_file)

    return movie_data_frame, user_data_frame, ratings_data_frame

def write_to_database(data_frames, file, scale=1):
    movie_data_frame = data_frames[0]
    user_data_frame = data_frames[1]
    ratings_data_frame = data_frames[2]

    print('Writing movie ground atoms...')
    write_movie_ground_atoms_to_file(movie_data_frame, file, scale=scale)
    print('Writing user ground atoms...')
    write_user_ground_atoms_to_file(user_data_frame, file, scale=scale)
    print('Writing ratings ground atoms...')
    write_ratings_ground_atoms_to_file(ratings_data_frame, file, scale=scale)


if __name__ == "__main__":
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    database_file = os.path.join(THIS_FOLDER, 'MovieLens0.2.db')
    movie_data_frame, user_data_frame, ratings_data_frame = import_data(THIS_FOLDER)

    file = open(database_file,'w')
    write_to_database([movie_data_frame,user_data_frame,ratings_data_frame],file,scale=0.2)

    