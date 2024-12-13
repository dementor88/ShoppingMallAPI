from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Category
from .service import ProductService

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def handle_category_cache_invalidation(sender, instance, **kwargs):
    if sender == Category:
        product_service = ProductService()
        product_service.invalidate_category_cache(instance.id)

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def handle_product_cache_invalidation(sender, instance, **kwargs):
    if sender == Product:
        product_service = ProductService()
        product_service.invalidate_product_cache(instance.id, instance.category_id)