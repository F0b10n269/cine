from django.shortcuts import render

from .models import Movie


def movie_list(request):
	movies = Movie.objects.filter(is_showing=True).select_related("genre")
	return render(request, "cine/movie_list.html", {"movies": movies})
