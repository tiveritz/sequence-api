import re
from django.test import TestCase
from api.models import HowTo, HowToUriId
from api.uri_id_generator import generate

class HowToTitleTestCase(TestCase):
    def test_creation_of_how_to(self):
        """
        How To's are correctly saved
        """
        normal_title = HowTo.objects.create(title = 'How to Write Test Cases')
        empty_title = HowTo.objects.create(title = '')

        msg = 'How To has not been created correctly'
        self.assertEqual(normal_title.title, 'How to Write Test Cases', msg)
        self.assertEqual(empty_title.title, '', msg)

class HowToUriIdTestCase(TestCase):
    def test_auto_build_uri_id(self):
        """
        Uri Id's are correctly built, assigned to each How To and unique
        """

        # Automatic creation does not work here, because this is done by
        # the API framework serializer
        how_to = HowTo.objects.create()
        uri_id = generate(how_to.id)
        how_to_uri_id = HowToUriId(
            uri_id = uri_id,
            how_to_id = how_to
        )
        how_to_uri_id.save()

        uri_id = HowToUriId.objects.get(pk = how_to.id) # Get from db

        # Matches any word with lower letters, numbers with a exact length of
        # 8 characters
        pattern = re.compile(r'^[a-z0-9]{8}$')
        is_match = True if re.match(pattern, str(uri_id)) else False

        msg_1 = 'How To Uri Id has not been created correctly'
        self.assertTrue(is_match, msg_1)

