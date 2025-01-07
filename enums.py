from enum import Enum

class ScenesSort(str, Enum):
    rating = "rating"
    date = 'date'
    views = 'views'
    title = 'title'
    likes = 'likes'

class ActorsSort(str, Enum):
    alpha = 'alpha'
    rating = 'rating'
    lastScene = 'lastScene'
    views = 'views'
    likes = 'likes'

class GenderSort(str, Enum):
    all = 'all'
    male = 'male'
    female = 'female'
