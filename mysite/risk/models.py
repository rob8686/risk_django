from django.db import models


class Security(models.Model):
    name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=200)
    sector = models.CharField(max_length=200)
    industry = models.CharField(max_length=200)
    asset_class = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)

    def __str__(self):
        return self.ticker


class Fund(models.Model):
    name = models.CharField(max_length=200)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Position(models.Model):
    quantity = models.FloatField()
    last_price = models.FloatField()
    price_date = models.DateField()
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE)

    def __str__(self):
        return self.security.ticker
