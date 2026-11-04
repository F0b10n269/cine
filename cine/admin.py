from django.contrib import admin

from .models import Genre, Movie, Ticket


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
	list_display = ("title", "genre", "price_clp", "is_showing")
	list_filter = ("genre", "is_showing")
	search_fields = ("title",)

	@admin.display(description="Precio (CLP)", ordering="ticket_price")
	def price_clp(self, obj):
		return f"${obj.ticket_price:,}".replace(",", ".")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ("code", "movie", "buyer_name", "quantity", "purchased_at")
	list_filter = ("movie",)
	search_fields = ("code", "movie__title", "buyer_name", "buyer_email")
	readonly_fields = ("code", "purchased_at")
