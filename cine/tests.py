from datetime import date

from django.contrib import admin
from django.contrib.auth.models import Group
from django.test import TestCase

from .admin import MovieAdmin, TicketAdmin
from .models import Genre, Movie, Ticket


class CatalogDeletionTests(TestCase):
	def setUp(self):
		self.genre = Genre.objects.create(name="Drama")
		self.movie = Movie.objects.create(
			title="Una película",
			synopsis="Sinopsis de prueba",
			duration_minutes=120,
			release_date=date(2025, 1, 1),
			genre=self.genre,
			poster="posters/test.jpg",
			ticket_price=5000,
			is_showing=True,
		)
		self.ticket = Ticket.objects.create(
			movie=self.movie,
			buyer_name="Ana Pérez",
			buyer_email="ana@example.com",
			quantity=2,
		)

	def test_deleting_genre_deletes_movies_and_tickets(self):
		self.genre.delete()

		self.assertFalse(Movie.objects.filter(pk=self.movie.pk).exists())
		self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

	def test_deleting_movie_deletes_its_tickets(self):
		self.movie.delete()

		self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

	def test_ticket_has_a_readable_identifier(self):
		self.assertIn(str(self.ticket.code), str(self.ticket))
		self.assertIn(self.movie.title, str(self.ticket))

	def test_homepage_displays_active_movie_poster(self):
		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.movie.title)
		self.assertContains(response, 'src="/media/posters/test.jpg"')


class AdminConfigurationTests(TestCase):
	def test_programming_group_has_only_requested_permissions(self):
		group = Group.objects.get(name="Programación")
		permissions = set(group.permissions.values_list("codename", flat=True))

		self.assertSetEqual(
			permissions,
			{
				"add_genre",
				"change_genre",
				"view_genre",
				"add_movie",
				"change_movie",
				"view_movie",
				"view_ticket",
			},
		)

	def test_movie_admin_formats_chilean_pesos_and_searches_by_title(self):
		movie_admin = MovieAdmin(Movie, admin.site)

		self.assertEqual(movie_admin.price_clp(Movie(ticket_price=4500)), "$4.500")
		self.assertEqual(movie_admin.search_fields, ("title",))
		self.assertIn("genre", movie_admin.list_filter)

	def test_ticket_admin_lists_purchase_details_and_filters_by_movie(self):
		ticket_admin = TicketAdmin(Ticket, admin.site)

		self.assertEqual(
			ticket_admin.list_display,
			("code", "movie", "buyer_name", "quantity", "purchased_at"),
		)
		self.assertEqual(ticket_admin.list_filter, ("movie",))
