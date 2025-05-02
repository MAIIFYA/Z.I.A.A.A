import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings # Import settings
from health_cards.models import HealthCard

class Command(BaseCommand):
    help = 'Loads health cards from a JSON file into the database.'

    def handle(self, *args, **options):
        # Use settings.BASE_DIR to construct the path relative to the project root
        json_file_path = os.path.join(settings.BASE_DIR, 'health_cards_data.json')
        self.stdout.write(f"Loading health cards from {json_file_path}")

        if not os.path.exists(json_file_path):
            self.stderr.write(self.style.ERROR(f"Error: JSON file not found at {json_file_path}"))
            return

        try:
            with open(json_file_path, 'r') as f:
                cards_data = json.load(f)
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Error: Could not decode JSON from {json_file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading file {json_file_path}: {e}"))
            return

        # Clear existing health cards
        self.stdout.write("Clearing existing health cards...")
        deleted_count, _ = HealthCard.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} existing health cards."))

        created_count = 0
        updated_count = 0

        for card_data in cards_data:
            try:
                card, created = HealthCard.objects.update_or_create(
                    title=card_data['title'],
                    defaults={
                        'description': card_data['description'],
                        'example_green': card_data['example_green'],
                        'example_amber': card_data['example_amber'],
                        'example_red': card_data['example_red'],
                        'image_path': card_data.get('image_path', '') # Use .get for safety
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"Created health card: {card.title}")
                else:
                    updated_count += 1
                    # self.stdout.write(f"Updated health card: {card.title}") # Optional: uncomment to see updates
            except KeyError as e:
                self.stderr.write(self.style.ERROR(f"Missing key {e} in card data: {card_data.get('title', 'N/A')}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing card {card_data.get('title', 'N/A')}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully loaded/updated health cards. Created: {created_count}, Updated: {updated_count}"
        ))

