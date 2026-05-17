from django.core.management.base import BaseCommand
from mongoengine.connection import get_db


class Command(BaseCommand):
    help = 'Drop the legacy sku_1 unique index from the products collection'

    def handle(self, *args, **options):
        db = get_db()
        indexes = db.products.index_information()
        if 'sku_1' in indexes:
            db.products.drop_index('sku_1')
            self.stdout.write(self.style.SUCCESS('Dropped sku_1 index.'))
        else:
            self.stdout.write('sku_1 index not found — nothing to do.')
