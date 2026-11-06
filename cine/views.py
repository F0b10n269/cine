from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie


def movie_list(request):
	movies = Movie.objects.filter(is_showing=True).select_related("genre")
	search_query = request.GET.get("q", "").strip()
	selected_genre = request.GET.get("genre", "")

	if search_query:
		movies = movies.filter(title__icontains=search_query)
	if selected_genre.isdigit():
		movies = movies.filter(genre_id=selected_genre)

	genres = Genre.objects.filter(movies__is_showing=True).distinct()
	return render(
		request,
		"cine/movie_list.html",
		{
			"movies": movies,
			"genres": genres,
			"search_query": search_query,
			"selected_genre": selected_genre,
		},
	)


def movie_detail(request, pk):
	movie = get_object_or_404(
		Movie.objects.select_related("genre"),
		pk=pk,
		is_showing=True,
	)
	return render(request, "cine/movie_detail.html", {"movie": movie})
