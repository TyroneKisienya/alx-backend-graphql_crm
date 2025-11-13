import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from .filters import CustomerFilter, OrderFilter, ProductFilter

from .models import Customer, Product, Order


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = ("id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = ("id", "customer", "products", "order_date", "total_amount")



class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)



class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def validate_phone(self, phone):
        import re
        if not phone:
            return True
        return re.match(r"^\+?\d[\d\-]{7,}$", phone)

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise ValidationError("Email already exists.")

        if input.phone and not self.validate_phone(input.phone):
            raise ValidationError("Invalid phone format.")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created = []
        errors = []

        for idx, cust in enumerate(input):
            try:
                if Customer.objects.filter(email=cust.email).exists():
                    raise ValidationError(f"Row {idx+1}: Email '{cust.email}' already exists.")

                import re
                if cust.phone:
                    if not re.match(r"^\+?\d[\d\-]{7,}$", cust.phone):
                        raise ValidationError(f"Row {idx+1}: Invalid phone number '{cust.phone}'.")

                c = Customer(name=cust.name, email=cust.email, phone=cust.phone)
                created.append(c)

            except ValidationError as e:
                errors.append(str(e))

        Customer.objects.bulk_create(created)

        return BulkCreateCustomers(customers=created, errors=errors)
    

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive.")

        if input.stock is not None and input.stock < 0:
            raise ValidationError("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )

        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID.")

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise ValidationError("One or more product IDs are invalid.")

        if not products:
            raise ValidationError("Order must include at least one product.")

        order_date = input.order_date or timezone.now()

        total = sum([p.price for p in products])

        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            total_amount=total
        )
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)



class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType,order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))
    hello= graphene.String(descripton="I am alive")
    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
    
    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
    
    def resolver_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
    
    def resolver_hello(self, info):
        return "I am living"


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
