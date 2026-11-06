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
		self.assertContains(response, "$5.000")

	def test_homepage_searches_by_title_and_filters_by_genre_together(self):
		action = Genre.objects.create(name="Acción")
		other_movie = Movie.objects.create(
			title="Otra película",
			synopsis="Otra sinopsis",
			duration_minutes=100,
			release_date=date(2025, 2, 1),
			genre=action,
			poster="posters/other.jpg",
			ticket_price=6000,
			is_showing=True,
		)

		response = self.client.get("/", {"q": "Otra", "genre": action.pk})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, other_movie.title)
		self.assertNotContains(response, self.movie.title)

	def test_homepage_does_not_show_movies_outside_showtime(self):
		self.movie.is_showing = False
		self.movie.save()

		response = self.client.get("/")

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, self.movie.title)

	def test_movie_detail_displays_all_details(self):
		response = self.client.get(f"/peliculas/{self.movie.pk}/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.movie.title)
		self.assertContains(response, self.movie.synopsis)
		self.assertContains(response, self.genre.name)
		self.assertContains(response, "120 minutos")
		self.assertContains(response, "$5.000 CLP")
		self.assertContains(response, 'src="/media/posters/test.jpg"')

	def test_movie_detail_returns_404_for_missing_or_inactive_movie(self):
		inactive_movie = Movie.objects.create(
			title="Fuera de cartelera",
			synopsis="Sinopsis",
			duration_minutes=90,
			release_date=date(2025, 3, 1),
			genre=self.genre,
			poster="posters/inactive.jpg",
			ticket_price=4000,
			is_showing=False,
		)

		self.assertEqual(
			self.client.get(f"/peliculas/{inactive_movie.pk}/").status_code,
			404,
		)
		self.assertEqual(self.client.get("/peliculas/999999/").status_code, 404)

	def test_ticket_purchase_creates_ticket_and_redirects_to_confirmation(self):
		ticket_count = Ticket.objects.count()

		response = self.client.post(
			f"/peliculas/{self.movie.pk}/",
			{
				"buyer_name": "Carlos Díaz",
				"buyer_email": "carlos@example.com",
				"quantity": 3,
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.wsgi_request.user.is_authenticated)
		self.assertEqual(Ticket.objects.count(), ticket_count + 1)
		ticket = Ticket.objects.latest("purchased_at")
		self.assertEqual(ticket.unit_price, 5000)
		self.assertEqual(response.redirect_chain, [(f"/tickets/{ticket.code}/", 302)])
		self.assertContains(response, str(ticket.code))
		self.assertContains(response, self.movie.title)
		self.assertContains(response, "Carlos Díaz")
		self.assertContains(response, "carlos@example.com")
		self.assertContains(response, "$15.000 CLP")

	def test_ticket_confirmation_shows_purchase_and_reload_does_not_duplicate(self):
		ticket = Ticket.objects.create(
			movie=self.movie,
			buyer_name="Carlos Díaz",
			buyer_email="carlos@example.com",
			quantity=3,
			unit_price=5000,
		)
		ticket_count = Ticket.objects.count()
		self.movie.ticket_price = 7000
		self.movie.save()

		for _ in range(2):
			response = self.client.get(f"/tickets/{ticket.code}/")
			self.assertEqual(response.status_code, 200)
			self.assertContains(response, str(ticket.code))
			self.assertContains(response, self.movie.title)
			self.assertContains(response, "Carlos Díaz")
			self.assertContains(response, "carlos@example.com")
			self.assertContains(response, "3 entradas")
			self.assertContains(response, "$15.000 CLP")
			self.assertContains(response, "Fecha y hora de compra")

		self.assertEqual(Ticket.objects.count(), ticket_count)

	def test_ticket_purchase_rejects_invalid_email_and_quantity(self):
		ticket_count = Ticket.objects.count()
		for buyer_name, email, quantity, expected_errors in (
			("", "", "", {"buyer_name", "buyer_email", "quantity"}),
			("Carlos Díaz", "no-es-un-correo", "2", {"buyer_email"}),
			("Carlos Díaz", "carlos@example.com", "0", {"quantity"}),
			("Carlos Díaz", "carlos@example.com", "11", {"quantity"}),
		):
			with self.subTest(email=email, quantity=quantity):
				response = self.client.post(
					f"/peliculas/{self.movie.pk}/",
					{
						"buyer_name": buyer_name,
						"buyer_email": email,
						"quantity": quantity,
					},
				)

				self.assertEqual(response.status_code, 200)
				self.assertSetEqual(
					set(response.context["form"].errors),
					expected_errors,
				)
				self.assertEqual(Ticket.objects.count(), ticket_count)

	def test_ticket_purchase_accepts_quantity_boundaries(self):
		for quantity in (1, 10):
			with self.subTest(quantity=quantity):
				response = self.client.post(
					f"/peliculas/{self.movie.pk}/",
					{
						"buyer_name": f"Comprador {quantity}",
						"buyer_email": f"comprador{quantity}@example.com",
						"quantity": str(quantity),
					},
				)

				self.assertEqual(response.status_code, 302)
				ticket = Ticket.objects.get(
					buyer_email=f"comprador{quantity}@example.com"
				)
				self.assertEqual(ticket.quantity, quantity)
				self.assertEqual(ticket.total_price, quantity * 5000)


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
