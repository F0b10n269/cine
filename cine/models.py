import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Genre(models.Model):
	name = models.CharField("nombre", max_length=100, unique=True)

	class Meta:
		verbose_name = "género"
		verbose_name_plural = "géneros"
		ordering = ["name"]

	def __str__(self):
		return self.name


class Movie(models.Model):
	title = models.CharField("título", max_length=200)
	synopsis = models.TextField("sinopsis")
	duration_minutes = models.PositiveSmallIntegerField(
		"duración (minutos)", validators=[MinValueValidator(1)]
	)
	release_date = models.DateField("fecha de estreno")
	genre = models.ForeignKey(
		Genre,
		verbose_name="género",
		related_name="movies",
		on_delete=models.CASCADE,
	)
	poster = models.ImageField("afiche", upload_to="posters/")
	ticket_price = models.PositiveIntegerField(
		"precio de entrada (pesos)", validators=[MinValueValidator(1)]
	)
	is_showing = models.BooleanField("en cartelera", default=False)

	class Meta:
		verbose_name = "película"
		verbose_name_plural = "películas"
		ordering = ["title"]

	def __str__(self):
		return self.title


class Ticket(models.Model):
	movie = models.ForeignKey(
		Movie,
		verbose_name="película",
		related_name="tickets",
		on_delete=models.CASCADE,
	)
	buyer_name = models.CharField("nombre del comprador", max_length=200)
	buyer_email = models.EmailField("correo del comprador")
	quantity = models.PositiveIntegerField(
		"cantidad de entradas", validators=[MinValueValidator(1)]
	)
	purchased_at = models.DateTimeField("fecha y hora de compra", auto_now_add=True)
	code = models.UUIDField("código", default=uuid.uuid4, unique=True, editable=False)

	class Meta:
		verbose_name = "ticket"
		verbose_name_plural = "tickets"
		ordering = ["-purchased_at"]

	def __str__(self):
		return f"{self.code} - {self.movie}"
