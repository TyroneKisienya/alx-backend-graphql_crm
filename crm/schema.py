import graphene
from graphene import Field, List
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Product, Customer, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model =  Customer
        fields = ('id', 'name', 'email', 'phone')

class ProductType(DjangoObjectType):
    class Meta:
        model= Product
        fields= ('id', 'name', 'price', 'stock')

class OrderType(DjangoObjectType):
    class Meta:
        model= Order
        fields= ('id', 'customer', 'products', 'order_date', 'total_amount')



class CustomerInput(graphene.InputObjectType):
    name= graphene.String(required=True)
    email= graphene.String(required=True)
    phone= graphene.String(required=True)

class ProductInput(graphene.InputObjectType):
    name= graphene.String(required=True)
    price= graphene.Float(required=True)
    stock= graphene.Int(required=False)

class OrderInput(graphene.InputObjectType):
    customer_id= graphene.ID(required=True)
    product_ids= graphene.List(graphene.ID, required=True)
    order_date= graphene.DateTime(required=False)



class CreateCustomer(graphene.Mutation):
    class Arguments:
        input= CustomerInput(required=True)
    
    customer= Field(CustomerType)
    message= graphene.String()

    def validate_phone(self, phone):
        import re
        if phone is None:
            return True
        pattern = r"^\+?\d[\d\-]{7,}$"
        return re.match(pattern, phone)
    
    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError ("Email already exists")
        
        if input.phone and not self.validate_phone(input.phone):
            raise ValidationError ("Invalid phone number format")
        
        customer= Customer.objects.create(
            name = input.name,
            email = input.email,
            phone = input.phone
        )
        return CreateCustomer(
            customer= customer,
            message= "Customer Created"
        )
    
class BulkCreateCustomer(graphene.Mutation):
    class Arguments:
        input = List(CustomerInput, required=True)
    
    customer = List(CustomerType)
    errors = List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []

        for idx, customer_data in enumerate(input):
            try:
                if Customer.objects.filter(email= customer_data.email).exists():
                    raise ValidationError (f"Row {idx + 1}: invalid Phone '{customer_data.phone}'")
                
                c = Customer(
                    name= customer_data.name,
                    email = customer_data.email,
                    phone = customer_data.phone
                )
                customers.append(c)

            except ValidationError as e:
                errors.append(str(e))

        Customer.objects.bulk_create(customers)

        return BulkCreateCustomer(customers=customers, errors=errors)
    
class CreateProducts(graphene.Mutation):
    class Arguments:
        input=ProductInput(required=True)
    
    product= Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise ValidationError ("Price must be postive")
        
        if input.stock is not None and input.stock < 0:
            raise ValidationError ("Stock cannot be negative")
        
        product= Product.objects.create(
            name= input.name,
            price= input.price,
            stock= input.stock or 0
        )

        return CreateProducts(product=product)
    
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = Field(OrderType)

    def mutate (self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError ("Invalid, Customer ID")
        
        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise ValidationError ("One or more Product IDs are invalid")
        if not products:
            raise ValidationError ("At least one product must be selected")
        order_date = input.order_date or timezone.now()

        total = sum(p.price for p in products)

        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            total_amount=total
        )
        order.products.set(products)

        return CreateOrder(order=order)

class CRMQuery(graphene.ObjectType):
    customers = List(CustomerType)
    orders = List(OrderType)
    products = List(ProductType)

    def resolve_customer(root, info):
        return Customer.objects.all()
    
    def resolve_products(root, info):
        return Product.objects.all()
    
    def resolver_orders(root, info):
        return Order.objects.all()
    


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customer = BulkCreateCustomer.Field()
    create_product = CreateProducts.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    all_customers= graphene.List(CustomerType)

    def resolver_all_customers(self, info):
        return Customer.objects.all()