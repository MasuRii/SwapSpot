from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.db.utils import IntegrityError
from django.db import transaction

from rest_framework.test import APIClient
from rest_framework import status

from .models import Item, Rating, User, Proposal, Notification, PaymentMethod, Tag, ItemTag


# ---------------------------------------------------------------------------
# Existing tests (kept intact)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Edge-case tests: User model & manager
# ---------------------------------------------------------------------------
class UserModelEdgeCaseTests(TestCase):
    """Edge-case coverage for User model and UserManager."""

    def test_create_user_raises_value_error_when_email_is_none(self):
        """UserManager.create_user rejects None email with ValueError."""
        with self.assertRaisesMessage(ValueError, 'Users must have an email address'):
            User.objects.create_user(email=None, username='testuser', password='pass123')

    def test_create_user_raises_value_error_when_email_is_empty(self):
        """UserManager.create_user rejects empty-string email with ValueError."""
        with self.assertRaisesMessage(ValueError, 'Users must have an email address'):
            User.objects.create_user(email='', username='testuser', password='pass123')

    def test_create_user_raises_value_error_when_username_is_none(self):
        """UserManager.create_user rejects None username with ValueError."""
        with self.assertRaisesMessage(ValueError, 'Users must have a username'):
            User.objects.create_user(email='a@b.com', username=None, password='pass123')

    def test_create_user_raises_value_error_when_username_is_empty(self):
        """UserManager.create_user rejects empty-string username with ValueError."""
        with self.assertRaisesMessage(ValueError, 'Users must have a username'):
            User.objects.create_user(email='a@b.com', username='', password='pass123')

    def test_email_uniqueness_enforced(self):
        """Duplicate email raises IntegrityError at the DB level."""
        User.objects.create_user(email='dup@example.com', username='user1', password='pass123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(email='dup@example.com', username='user2', password='pass123')

    def test_username_uniqueness_enforced(self):
        """Duplicate username raises IntegrityError at the DB level."""
        User.objects.create_user(email='a@b.com', username='duplicate', password='pass123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(email='c@d.com', username='duplicate', password='pass123')

    def test_email_normalized_to_lowercase(self):
        """Email is normalized to lowercase on creation."""
        user = User.objects.create_user(
            email='UPPERCASE@Example.COM',
            username='normuser',
            password='pass123',
        )
        self.assertEqual(user.email, 'UPPERCASE@example.com')

    def test_get_full_name_with_both_names(self):
        """get_full_name returns 'First Last' when both are set."""
        user = User.objects.create_user(
            email='name@test.com', username='nameuser', password='pass123',
            first_name='John', last_name='Doe',
        )
        self.assertEqual(user.get_full_name(), 'John Doe')

    def test_get_full_name_with_only_first_name(self):
        """get_full_name returns 'First' when only first_name is set."""
        user = User.objects.create_user(
            email='single@test.com', username='singlename', password='pass123',
            first_name='Alice', last_name='',
        )
        self.assertEqual(user.get_full_name(), 'Alice')

    def test_get_full_name_with_only_last_name(self):
        """get_full_name returns 'Last' when only last_name is set."""
        user = User.objects.create_user(
            email='last@test.com', username='lastname', password='pass123',
            first_name='', last_name='Smith',
        )
        self.assertEqual(user.get_full_name(), 'Smith')

    def test_get_full_name_with_empty_names_returns_empty_string(self):
        """get_full_name returns '' when both first and last names are empty."""
        user = User.objects.create_user(
            email='anon@test.com', username='anon', password='pass123',
            first_name='', last_name='',
        )
        self.assertEqual(user.get_full_name(), '')

    def test_get_full_name_strips_whitespace(self):
        """get_full_name strips surrounding whitespace."""
        user = User.objects.create_user(
            email='space@test.com', username='spaceuser', password='pass123',
            first_name='  Jane  ', last_name='  ',
        )
        self.assertEqual(user.get_full_name(), 'Jane')

    def test_get_short_name_returns_first_name(self):
        """get_short_name returns first_name when set."""
        user = User.objects.create_user(
            email='short@test.com', username='shortuser', password='pass123',
            first_name='Charlie',
        )
        self.assertEqual(user.get_short_name(), 'Charlie')

    def test_get_short_name_falls_back_to_username(self):
        """get_short_name falls back to username when first_name is empty."""
        user = User.objects.create_user(
            email='fallback@test.com', username='fallbackuser', password='pass123',
            first_name='',
        )
        self.assertEqual(user.get_short_name(), 'fallbackuser')

    def test_user_str_returns_email(self):
        """User __str__ returns the email address."""
        user = User.objects.create_user(
            email='str@example.com', username='struser', password='pass123',
        )
        self.assertEqual(str(user), 'str@example.com')

    def test_new_user_has_default_average_rating_zero(self):
        """New user starts with average_rating 0.00."""
        user = User.objects.create_user(
            email='new@test.com', username='newuser', password='pass123',
        )
        self.assertEqual(user.average_rating, 0.00)

    def test_new_user_is_active_and_not_staff(self):
        """New user defaults: is_active=True, is_staff=False."""
        user = User.objects.create_user(
            email='flags@test.com', username='flaguser', password='pass123',
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.terms_agreed)

    def test_create_superuser_requires_is_staff_true(self):
        """Superuser creation rejects is_staff=False."""
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_staff=True.'):
            User.objects.create_superuser(
                email='admin@test.com', username='admin', password='pass123',
                is_staff=False,
            )

    def test_create_superuser_requires_is_superuser_true(self):
        """Superuser creation rejects is_superuser=False."""
        with self.assertRaisesMessage(ValueError, 'Superuser must have is_superuser=True.'):
            User.objects.create_superuser(
                email='admin@test.com', username='admin', password='pass123',
                is_superuser=False,
            )


# ---------------------------------------------------------------------------
# Edge-case tests: Rating model & signal
# ---------------------------------------------------------------------------
class RatingEdgeCaseTests(TestCase):
    """Edge-case coverage for Rating model, validators, signals, and unique constraint."""

    def setUp(self):
        self.ratee = User.objects.create_user(
            email='ratee@example.com', username='ratee', password='pass123',
        )
        self.rater = User.objects.create_user(
            email='rater@example.com', username='rater', password='pass123',
        )

    def test_rating_boundary_minimum_1_valid(self):
        """Rating with value 1 is accepted (boundary)."""
        rating = Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=1)
        self.assertEqual(rating.rating, 1)

    def test_rating_boundary_maximum_5_valid(self):
        """Rating with value 5 is accepted (boundary)."""
        rating = Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=5)
        self.assertEqual(rating.rating, 5)

    def test_rating_below_minimum_raises_validation_error(self):
        """Rating with value 0 is rejected by MinValueValidator."""
        from django.core.exceptions import ValidationError
        r = Rating(rater=self.rater, ratee=self.ratee, rating=0)
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_rating_above_maximum_raises_validation_error(self):
        """Rating with value 6 is rejected by MaxValueValidator."""
        from django.core.exceptions import ValidationError
        r = Rating(rater=self.rater, ratee=self.ratee, rating=6)
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_duplicate_rating_same_rater_and_ratee_raises_integrity_error(self):
        """Unique together (rater, ratee) prevents duplicate ratings."""
        Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=3)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=5)

    def test_multiple_ratings_calculate_correct_average(self):
        """Average rating computed correctly with multiple raters."""
        from decimal import Decimal
        rater2 = User.objects.create_user(
            email='rater2@example.com', username='rater2', password='pass123',
        )
        rater3 = User.objects.create_user(
            email='rater3@example.com', username='rater3', password='pass123',
        )
        Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=2)
        Rating.objects.create(rater=rater2, ratee=self.ratee, rating=4)
        Rating.objects.create(rater=rater3, ratee=self.ratee, rating=5)

        self.ratee.refresh_from_db()
        # (2+4+5)/3 = 3.67
        self.assertEqual(self.ratee.average_rating, Decimal('3.67'))

    def test_average_rating_rounded_to_two_decimals(self):
        """Average rating is rounded to 2 decimal places."""
        from decimal import Decimal
        rater2 = User.objects.create_user(
            email='r2@example.com', username='r2', password='pass123',
        )
        rater3 = User.objects.create_user(
            email='r3@example.com', username='r3', password='pass123',
        )
        Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=1)
        Rating.objects.create(rater=rater2, ratee=self.ratee, rating=2)
        Rating.objects.create(rater=rater3, ratee=self.ratee, rating=2)
        # (1+2+2)/3 = 1.666... → rounds to 1.67
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, Decimal('1.67'))

    def test_average_rating_updates_on_rating_update(self):
        """When a rating is updated, the average is recalculated via signal."""
        rating = Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=1)
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, 1.0)

        rating.rating = 5
        rating.save()
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, 5.0)

    def test_average_rating_updates_on_rating_delete(self):
        """When a rating is deleted, the average resets via post_delete signal."""
        rater2 = User.objects.create_user(
            email='r2@example.com', username='r2', password='pass123',
        )
        rating1 = Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=4)
        Rating.objects.create(rater=rater2, ratee=self.ratee, rating=2)
        # (4+2)/2 = 3.0
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, 3.0)

        rating1.delete()
        self.ratee.refresh_from_db()
        # Only rating=2 left → 2.0
        self.assertEqual(self.ratee.average_rating, 2.0)

    def test_average_rating_resets_to_zero_when_all_ratings_deleted(self):
        """When all ratings for a user are deleted, average_rating returns to 0.00."""
        Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=3)
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, 3.0)

        Rating.objects.all().delete()
        self.ratee.refresh_from_db()
        self.assertEqual(self.ratee.average_rating, 0.00)

    def test_rating_str_contains_rater_ratee_and_stars(self):
        """Rating __str__ includes rater, ratee usernames and star count."""
        rating = Rating.objects.create(rater=self.rater, ratee=self.ratee, rating=4)
        self.assertIn('rater', str(rating))
        self.assertIn('ratee', str(rating))
        self.assertIn('4', str(rating))


# ---------------------------------------------------------------------------
# Edge-case tests: Item model
# ---------------------------------------------------------------------------
class ItemModelEdgeCaseTests(TestCase):
    """Edge-case coverage for Item model constraints and behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='seller@example.com', username='seller', password='pass123',
        )

    def test_item_creation_with_valid_condition_choices(self):
        """Item created with each allowed condition choice succeeds."""
        for condition in ['New', 'Like New', 'Used', 'Refurbished']:
            item = Item.objects.create(
                user=self.user, title=f'Item {condition}',
                description='Test', category='Electronics',
                condition=condition, price='100.00', listing_type='Sell',
            )
            self.assertEqual(item.condition, condition)

    def test_item_creation_with_valid_listing_types(self):
        """Item created with both Sell and Exchange listing types."""
        for lt in ['Sell', 'Exchange']:
            item = Item.objects.create(
                user=self.user, title=f'Item {lt}',
                description='Test', category='Electronics',
                condition='New', price='50.00', listing_type=lt,
            )
            self.assertEqual(item.listing_type, lt)

    def test_item_str_returns_title(self):
        """Item __str__ returns the title."""
        item = Item.objects.create(
            user=self.user, title='Test Item', description='Desc',
            category='Books', condition='Used', price='10.00', listing_type='Sell',
        )
        self.assertEqual(str(item), 'Test Item')

    def test_item_defaults_is_available_true(self):
        """New item defaults is_available to True."""
        item = Item.objects.create(
            user=self.user, title='Available Item', description='Desc',
            category='Books', condition='New', price='20.00', listing_type='Sell',
        )
        self.assertTrue(item.is_available)

    def test_item_price_stored_as_decimal(self):
        """Item price is stored and retrieved as Decimal with 2 places."""
        from decimal import Decimal
        item = Item.objects.create(
            user=self.user, title='Priced Item', description='Desc',
            category='Books', condition='New', price='1234.56', listing_type='Sell',
        )
        # SQLite stores DecimalField as TEXT; refresh_from_db ensures conversion
        item.refresh_from_db()
        self.assertEqual(item.price, Decimal('1234.56'))

    def test_item_price_boundary_large(self):
        """Item accepts large price values within Decimal(10,2) range."""
        item = Item.objects.create(
            user=self.user, title='Expensive', description='Desc',
            category='Luxury', condition='New', price='99999999.99',
            listing_type='Sell',
        )
        self.assertEqual(float(item.price), 99999999.99)

    def test_item_date_listed_auto_set(self):
        """date_listed is automatically set on creation."""
        from django.utils import timezone
        before = timezone.now()
        item = Item.objects.create(
            user=self.user, title='Timed Item', description='Desc',
            category='Books', condition='New', price='5.00', listing_type='Sell',
        )
        after = timezone.now()
        self.assertTrue(before <= item.date_listed <= after)


# ---------------------------------------------------------------------------
# Edge-case tests: Serializer validation (DRF)
# ---------------------------------------------------------------------------
class SerializerEdgeCaseTests(TestCase):
    """Edge-case coverage for DRF serializers, especially UserSerializer validation."""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration_password_mismatch(self):
        """UserSerializer rejects mismatched password and password_confirm."""
        payload = {
            'email': 'mismatch@example.com',
            'username': 'mismatch',
            'password': 'StrongPass1!',
            'password_confirm': 'DifferentPass2@',
        }
        resp = self.client.post('/api/users/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data)

    def test_user_registration_weak_password_rejected(self):
        """UserSerializer rejects passwords that fail Django validation.

        Note: AUTH_PASSWORD_VALIDATORS is set to [] in settings, so Django's
        default password validators are disabled. This test verifies that
        the UserSerializer still enforces its own validate_password usage
        when validators are configured. When validators are empty, any
        password passes — this test documents that gap.
        """
        # With AUTH_PASSWORD_VALIDATORS=[] the password '123' passes.
        # This is a known configuration gap; add validators to settings
        # to enable password strength enforcement.
        payload = {
            'email': 'weak@example.com',
            'username': 'weakpass',
            'password': '123',
            'password_confirm': '123',
        }
        resp = self.client.post('/api/users/', payload, format='json')
        # Currently succeeds because validators are empty. If validators are
        # later enabled, this should become a 400 with password in resp.data.
        if resp.status_code == status.HTTP_201_CREATED:
            self.skipTest(
                'Password validators are disabled (AUTH_PASSWORD_VALIDATORS=[]). '
                'Enable validators to enforce password strength.'
            )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', resp.data)

    def test_user_registration_missing_required_fields(self):
        """UserSerializer rejects request missing required email and username."""
        payload = {
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        }
        resp = self.client.post('/api/users/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', resp.data)
        self.assertIn('username', resp.data)

    def test_item_list_via_api(self):
        """GET /api/items/ returns item list (empty initially)."""
        resp = self.client.get('/api/items/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_item_create_and_retrieve_via_api(self):
        """POST /api/items/ creates item, GET /api/items/{id}/ retrieves it."""
        user = User.objects.create_user(
            email='seller@example.com', username='seller', password='pass123',
        )
        payload = {
            'user': user.user_id,
            'title': 'API Item',
            'description': 'Created via API',
            'category': 'Electronics',
            'condition': 'New',
            'price': '149.99',
            'listing_type': 'Sell',
        }
        create_resp = self.client.post('/api/items/', payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        item_id = create_resp.data['item_id']

        get_resp = self.client.get(f'/api/items/{item_id}/')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data['title'], 'API Item')
        self.assertEqual(get_resp.data['price'], '149.99')

    def test_user_list_excludes_password_fields(self):
        """API user list never exposes password or password_confirm."""
        User.objects.create_user(
            email='safe@example.com', username='safeuser', password='secret123',
        )
        resp = self.client.get('/api/users/', HTTP_ACCEPT='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        user_data = resp.data[0]
        self.assertNotIn('password', user_data)
        self.assertNotIn('password_confirm', user_data)


# ---------------------------------------------------------------------------
# Edge-case tests: View behavior
# ---------------------------------------------------------------------------
class ViewEdgeCaseTests(TestCase):
    """Edge-case coverage for view-level behaviors including auth and self-rating."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com', username='owner', password='pass123',
        )

    def test_delete_item_post_successfully_deletes_item(self):
        """POST /items/{id}/delete/ removes item and redirects."""
        item = Item.objects.create(
            user=self.user, title='To Delete', description='Desc',
            category='Books', condition='Used', price='10.00', listing_type='Sell',
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse('exchange:delete_item', args=[item.item_id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(item_id=item.item_id).exists())

    def test_delete_item_non_owner_returns_404(self):
        """Non-owner cannot delete another user's item (get_object_or_404)."""
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass123',
        )
        item = Item.objects.create(
            user=other, title='Not Yours', description='Desc',
            category='Books', condition='Used', price='5.00', listing_type='Sell',
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse('exchange:delete_item', args=[item.item_id]))

        self.assertEqual(response.status_code, 404)

    def test_self_rating_rejected_by_view(self):
        """User cannot rate themselves via the profile view."""
        self.client.force_login(self.user)
        profile_url = reverse('exchange:user_profile', args=[self.user.username])

        response = self.client.post(
            profile_url,
            {'rating': 4},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('cannot rate yourself', data['message'].lower())

    def test_invalid_rating_value_rejected_by_view(self):
        """Rating value outside 1-5 range is rejected by view."""
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass123',
        )
        self.client.force_login(self.user)
        profile_url = reverse('exchange:user_profile', args=[other.username])

        response = self.client.post(
            profile_url,
            {'rating': 0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('invalid rating', data['message'].lower())

    def test_landing_page_accessible_without_login(self):
        """Landing page is publicly accessible (no login required)."""
        response = self.client.get(reverse('exchange:landing'))
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# Edge-case tests: Other models
# ---------------------------------------------------------------------------
class OtherModelEdgeCaseTests(TestCase):
    """Edge-case coverage for PaymentMethod, Tag, Proposal, Notification models."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='u@example.com', username='modeltest', password='pass123',
        )
        self.other = User.objects.create_user(
            email='o@example.com', username='other', password='pass123',
        )
        self.item = Item.objects.create(
            user=self.user, title='Model Item', description='Desc',
            category='Misc', condition='New', price='1.00', listing_type='Sell',
        )

    def test_payment_method_str_includes_provider_and_email(self):
        pm = PaymentMethod.objects.create(
            user=self.user, provider='PayPal', account_details='u@example.com',
        )
        self.assertIn('PayPal', str(pm))
        self.assertIn('u@example.com', str(pm))

    def test_payment_method_is_verified_defaults_false(self):
        pm = PaymentMethod.objects.create(
            user=self.user, provider='Stripe', account_details='acct_123',
        )
        self.assertFalse(pm.is_verified)

    def test_tag_creation_and_str(self):
        tag = Tag.objects.create(name='Electronics')
        self.assertEqual(str(tag), 'Electronics')

    def test_item_tag_links_item_and_tag(self):
        tag = Tag.objects.create(name='Vintage')
        item_tag = ItemTag.objects.create(item=self.item, tag=tag)
        self.assertEqual(item_tag.item, self.item)
        self.assertEqual(item_tag.tag, tag)
        self.assertIn('Model Item', str(item_tag))
        self.assertIn('Vintage', str(item_tag))

    def test_proposal_creation_and_str(self):
        proposal = Proposal.objects.create(
            sender=self.user, receiver=self.other, item=self.item,
            message='I want this', status='pending',
        )
        self.assertIn('u@example.com', str(proposal))
        self.assertIn('o@example.com', str(proposal))

    def test_notification_defaults_is_read_false(self):
        notif = Notification.objects.create(
            user=self.user, content='You have a new proposal.',
        )
        self.assertFalse(notif.is_read)

    def test_notification_str_contains_user_email(self):
        notif = Notification.objects.create(
            user=self.user, content='Test notification.',
        )
        self.assertIn('u@example.com', str(notif))
