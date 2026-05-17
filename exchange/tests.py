from django.test import TestCase
from django.urls import reverse

from .models import Item, Rating, User


class AppHealthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='password123',
            first_name='Owner',
            last_name='User',
        )

    def test_add_item_page_has_template_for_fresh_clone(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('exchange:add_item'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exchange/add_item.html')
        self.assertContains(response, 'Add Item')

    def test_delete_item_get_returns_permission_denied(self):
        item = Item.objects.create(
            user=self.user,
            title='Desk Lamp',
            description='Working lamp',
            category='Home and Kitchen',
            condition='Used',
            price='250.00',
            listing_type='Sell',
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('exchange:delete_item', args=[item.item_id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Item.objects.filter(item_id=item.item_id).exists())

    def test_users_api_serializes_profile_fields(self):
        response = self.client.get('/api/users/', HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload[0]['email'], 'owner@example.com')
        self.assertEqual(payload[0]['full_name'], 'Owner User')
        self.assertIsNone(payload[0]['profile_picture_url'])

    def test_rating_updates_average_rating(self):
        rater = User.objects.create_user(
            email='rater@example.com',
            username='rater',
            password='password123',
        )

        Rating.objects.create(rater=rater, ratee=self.user, rating=4)

        self.user.refresh_from_db()
        self.assertEqual(self.user.average_rating, 4)
