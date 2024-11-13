import pickle
import requests
from django.shortcuts import render

# Load your pre-trained movie recommendation model
movies = pickle.load(open('mrs/model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('mrs/model/similarity.pkl', 'rb'))

def load_models():
    # Ensure to use the correct path for your model files
    movie_list = pickle.load(open('mrs/model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('mrs/model/similarity.pkl', 'rb'))
    return movie_list, similarity

# Fetch poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return full_path

def fetch_overview(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    overview = data['overview']
    return overview

# Recommendation logic
def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies = []
    
    for i in distances[1:5]:  # Get the top 5 movie recommendations
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        movie_name = movies.iloc[i[0]].title
        description = fetch_overview(movie_id)
        recommended_movies.append((movie_name, poster_url, description))  # Append the name and poster as a tuple
    return recommended_movies


# The view that renders the home page
def index(request):
    movies, similarity = load_models()  # Load the movie list and similarity model

    movie_list = movies['title'].values  # Get the list of movie titles for the dropdown
    recommended_movies = []

    if request.method == 'POST':
        selected_movie = request.POST.get('movie')
        recommended_movies = recommend(selected_movie, movies, similarity)

        context = {
            'selected_movie': selected_movie,
            'recommended_movies': recommended_movies,
            'movie_list': movie_list,
        }
    else:
        context = {
            'movie_list': movie_list,
        }

    return render(request, 'recommender/index.html', context)
