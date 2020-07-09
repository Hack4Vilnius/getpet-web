from django.contrib.auth import get_user_model
from faker import Factory
import factory

from web.models import Country, Mentor, Pet, PetGender, PetSize, PetStatus, Region, Shelter, TeamMember

faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('code',)

    name = 'Lithuania'
    code = 'lt'


class RegionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ('code',)

    name = factory.Faker('city')
    code = name
    country = factory.SubFactory(CountryFactory)


class ShelterFactory(factory.DjangoModelFactory):
    class Meta:
        model = Shelter

    name = factory.Faker('company')
    is_published = True
    square_logo = factory.django.ImageField(color='green')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    address = factory.Faker('address')
    latitude = factory.Faker('latitude')
    longitude = factory.Faker('longitude')
    region = factory.SubFactory(RegionFactory)

    @factory.post_generation
    def authenticated_users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for user in extracted:
                self.authenticated_users.add(user)


class PetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Pet

    name = factory.Faker('first_name')
    photo = factory.django.ImageField(color='blue')
    shelter = factory.SubFactory(ShelterFactory)
    status = PetStatus.AVAILABLE
    short_description = factory.Faker('text', max_nb_chars=64)
    description = factory.Faker('text')
    gender = PetGender.Male
    age = factory.Faker('pyint')
    weight = factory.Faker('pyint')
    size = PetSize.Medium
    desexed = factory.Faker('boolean')


class TeamMemberFactory(factory.DjangoModelFactory):
    class Meta:
        model = TeamMember

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    role = factory.Faker('sentence')

    email = factory.Faker('email')
    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')


class MentorFactory(factory.DjangoModelFactory):
    class Meta:
        model = Mentor

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    description = factory.Faker('sentence')

    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')