from django.shortcuts import get_object_or_404, redirect, render

from .forms import TicketPurchaseForm
from .models import Genre, Movie, Ticket


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
	form = TicketPurchaseForm(
		request.POST if request.method == "POST" else None
	)
	if request.method == "POST" and form.is_valid():
		ticket = Ticket.objects.create(
			movie=movie,
			buyer_name=form.cleaned_data["buyer_name"],
			buyer_email=form.cleaned_data["buyer_email"],
			quantity=form.cleaned_data["quantity"],
			unit_price=movie.ticket_price,
		)
		return redirect("ticket_detail", code=ticket.code)
	return render(
		request,
		"cine/movie_detail.html",
		{"movie": movie, "form": form},
	)


def ticket_detail(request, code):
	ticket = get_object_or_404(
		Ticket.objects.select_related("movie", "movie__genre"),
		code=code,
	)
	return render(request, "cine/ticket_detail.html", {"ticket": ticket})
