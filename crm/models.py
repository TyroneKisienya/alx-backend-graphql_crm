from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal

# Create your models here.
class Customer(models.Model):
    name= models.CharField(max_length=100)
    email=models.EmailField(unique=True)

    phone= models.CharField(max_length=20, null= True, validators=[ RegexValidator(
        regex= r"^\+?\d[\d\-]{7,}$",
        message="Number must be valid (e.g., +1234567890 or 123-456-7890)",
    )],)

    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    
class Product(models.Model):
    name= models.CharField(max_length=100)

    price= models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(
        Decimal("0.01")
    )],)

    stock= models.PositiveIntegerField(default=0)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price}"
    
class Order(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product= models.ManyToManyField(Product, related_name='orders')
    order_date= models.DateTimeField(auto_now_add=True)

    total_amount= models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(
        Decimal("0.00")
    )],)

    created_at= models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total= sum([p.price for p in self.product.all()])
        self.total_amount = total
        self.save()
    
    def __str__(self):
        return f'Order #{self.id} - customer: {self.customer.name}'