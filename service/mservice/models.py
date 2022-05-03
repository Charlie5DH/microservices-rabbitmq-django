from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ProductUser(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()

    models.UniqueConstraint(name='user_product_unique', fields=['user_id', 'product_id'])
    
    def __str__(self):
        return self.product_id