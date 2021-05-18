#Script to generate the MovieLens relational database for structure learning
import os
import pandas as pd

NUMBER_USERS = 6040
NUMBER_MOVIES = 3952

num_age_categories =  2
num_rating_categories = 2
restrict_genres = True
restricted_genres = ['Romance', 'Horror', 'Animation', 'Documentary']
balance_users_and_movies = False
alternative_predicate_types = True

#(only used if restrict_genres = True) A list of movie ids that are not of the 
#genre of a resticted genre. This list gets populated automatically by the script.
banned_movies = []

def populate_banned_movies(data_frame, scale):
    write_movie_ground_atoms_to_file(data_frame, None, scale, suppress_output = True)

#ADD COMMENT
rated_movies = []

#ADD COMMENT
users_rating_movies = []


def read_movies_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['MovieID', 'MovieTitle', 'MovieGenres'], engine='python')
    return DataFrame 

def read_users_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'ZipCode'], engine='python')
    return DataFrame

def read_ratings_file(file_name):
    DataFrame = pd.read_csv(file_name, delimiter='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python')
    return DataFrame 

def write_movie_genre_predicate_to_file(genre, movieID, file, suppress_output):
    if not suppress_output and movieID in rated_movies:
        if alternative_predicate_types:
            file.write(f"Genre(M{movieID},{genre})\n")
        else:
            file.write(f"{genre}(M{movieID})\n")

def write_movie_to_file(row, file, suppress_output):
    movies_added = 0
    movieID = row['MovieID']
    genres = row['MovieGenres'].split('|')
    for genre in genres:
        if restrict_genres:
            if genre in restricted_genres:
                write_movie_genre_predicate_to_file(genre, movieID, file, suppress_output)
                movies_added = 1
            else:
                banned_movies.append(movieID)
        else:
            write_movie_genre_predicate_to_file(genre, movieID, file, suppress_output)
    
    return movies_added

def write_movie_ground_atoms_to_file(data_frame, file, scale, suppress_output = False):
    number_of_movies = 0
    for index,row in data_frame.iterrows():
        if balance_users_and_movies:
            if number_of_movies < NUMBER_USERS * scale * 1.7:
                movies_added = write_movie_to_file(row, file, suppress_output)
                number_of_movies += movies_added
        else:
            if row['MovieID'] < NUMBER_MOVIES * scale:
                movies_added = write_movie_to_file(row, file, suppress_output)
                number_of_movies += movies_added

def write_user_gender_predicate_to_file(gender, userID, file):
    male = "M"
    female = "F"
    if alternative_predicate_types:
        if gender == male:
            file.write(f"Gender(U{userID},Male)\n")
        elif gender == female:
            file.write(f"Gender(U{userID},Female)\n")
    else:
        if gender == male:
            file.write(f"Male(U{userID})\n")
        elif gender == female:
            file.write(f"Female(U{userID})\n")

def write_user_age_predicate_to_file(age, userID, file):
    if alternative_predicate_types:
        if num_age_categories == 3:
            if age in [1, 18, 25]:
                file.write(f"Age(U{userID},Youthful)\n")
            elif age in [35, 45, 50]:
                file.write(f"Age(U{userID},MiddleAged)\n")
            elif age == 56:
                file.write(f"Age(U{userID},Old)\n")
        elif num_age_categories == 2:
            if age in [1, 18, 25, 35]:
                file.write(f"Age(U{userID},Young)\n")
            elif age in [45, 50, 56]:
                file.write(f"Age(U{userID},Old)\n")
        else:
            raise ValueError('number_of_age_categories ({}) not supported'.format(num_age_categories))
    else:
        if num_age_categories == 3:
            if age in [1, 18, 25]:
                file.write(f"Youthful(U{userID})\n")
            elif age in [35, 45, 50]:
                file.write(f"MiddleAged(U{userID})\n")
            elif age == 56:
                file.write(f"Old(U{userID})\n")
        elif num_age_categories == 2:
            if age in [1, 18, 25, 35]:
                file.write(f"Young(U{userID})\n")
            elif age in [45, 50, 56]:
                file.write(f"Old(U{userID})\n")
        else:
            raise ValueError('number_of_age_categories ({}) not supported'.format(num_age_categories))

def write_user_ground_atoms_to_file(data_frame, file, scale):
    for index,row in data_frame.iterrows():
        gender = row['Gender']
        age = row['Age']
        userID = row['UserID']
        if userID < NUMBER_USERS * scale and userID in users_rating_movies:
            write_user_gender_predicate_to_file(gender, userID, file)
            write_user_age_predicate_to_file(age, userID, file)
            
def write_rating_predicate_to_file(rating, row, file):
    if num_rating_categories == 3:
        if rating >=4:
            rating = 'Positive'
        elif rating == 3:
            rating = 'Indifferent'
        elif rating <= 2:
            rating = 'Negative'
    elif num_rating_categories == 2:
        if rating >=4:
            rating = 'Positive'
        else:
            rating = 'Negative'
    else:
        raise ValueError('number_of_rating_categories ({}) not supported'.format(num_rating_categories))
    if restrict_genres:
        if row['MovieID'] not in banned_movies:
            rated_movies.append(row['MovieID'])
            users_rating_movies.append(row['UserID'])
            file.write(f"Rating(U{row['UserID']},M{row['MovieID']},{rating})\n")
    else:
        rated_movies.append(row['MovieID'])
        users_rating_movies.append(row['UserID'])
        file.write(f"Rating(U{row['UserID']},M{row['MovieID']},{rating})\n")

def write_ratings_ground_atoms_to_file_and_populate_rated_movies_and_users_rating_movies_arrays(data_frame, file, scale):
    for index,row in data_frame.iterrows():
        if row['UserID'] < NUMBER_USERS * scale and row['MovieID'] < NUMBER_MOVIES * scale:
            rating = row['Rating']
            write_rating_predicate_to_file(rating, row, file)

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

    if restrict_genres:
        print('Populating banned movies...')
        populate_banned_movies(movie_data_frame, scale)
    print('Writing ratings ground atoms...')
    write_ratings_ground_atoms_to_file_and_populate_rated_movies_and_users_rating_movies_arrays(ratings_data_frame, file, scale=scale)
    print('Writing movie ground atoms...')
    write_movie_ground_atoms_to_file(movie_data_frame, file, scale=scale)
    print('Writing user ground atoms...')
    write_user_ground_atoms_to_file(user_data_frame, file, scale=scale)
    


if __name__ == "__main__":
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    database_file = os.path.join(THIS_FOLDER, 'MovieLensMini.db')
    movie_data_frame, user_data_frame, ratings_data_frame = import_data(THIS_FOLDER)

    file = open(database_file,'w')
    write_to_database([movie_data_frame,user_data_frame,ratings_data_frame],file,scale=0.20)

    