from django import forms


class TicketPurchaseForm(forms.Form):
	buyer_name = forms.CharField(
		label="Nombre",
		max_length=200,
		widget=forms.TextInput(attrs={"autocomplete": "name"}),
	)
	buyer_email = forms.EmailField(
		label="Correo electrónico",
		widget=forms.EmailInput(attrs={"autocomplete": "email"}),
	)
	quantity = forms.IntegerField(
		label="Cantidad de entradas",
		min_value=1,
		max_value=10,
		initial=1,
		widget=forms.NumberInput(attrs={"min": 1, "max": 10}),
	)
