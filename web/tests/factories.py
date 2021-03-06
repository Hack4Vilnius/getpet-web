import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from factory.django import DjangoModelFactory
from faker import Factory, Faker
from faker.providers import BaseProvider

from web.models import Cat, Country, Dog, Mentor, Pet, PetGender, PetSize, PetStatus, Region, Shelter, TeamMember

faker_factory = Factory.create()
faker = Faker()

class DjangoGeoPointProvider(BaseProvider):

    def geo_point(self, **kwargs):
        kwargs['coords_only'] = True
        lat_lng = faker.latlng()
        return Point(x=float(lat_lng[0]), y=float(lat_lng[1]))


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = factory.Faker('user_name')


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('code',)

    name = 'Lithuania'
    code = 'lt'


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ('code',)

    name = factory.Faker('city')
    code = name
    country = factory.SubFactory(CountryFactory)


class ShelterFactory(DjangoModelFactory):
    factory.Faker.add_provider(DjangoGeoPointProvider)

    class Meta:
        model = Shelter

    name = factory.Faker('company')
    is_published = True
    square_logo = factory.django.ImageField(color='green')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')
    address = factory.Faker('address')
    location = factory.Faker('geo_point', country_code='LT')
    region = factory.SubFactory(RegionFactory)

    @factory.post_generation
    def authenticated_users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for user in extracted:
                self.authenticated_users.add(user)


class PetFactory(DjangoModelFactory):
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
    desexed = factory.Faker('boolean')


class DogFactory(PetFactory):
    class Meta:
        model = Dog

    size = PetSize.Medium


class CatFactory(PetFactory):
    class Meta:
        model = Cat


class TeamMemberFactory(DjangoModelFactory):
    class Meta:
        model = TeamMember

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    role = factory.Faker('sentence')

    email = factory.Faker('email')
    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')


class MentorFactory(DjangoModelFactory):
    class Meta:
        model = Mentor

    name = factory.Faker('name')
    photo = factory.django.ImageField(color='blue')
    description = factory.Faker('sentence')

    facebook = factory.Faker('url')
    linkedin = factory.Faker('url')
    instagram = factory.Faker('url')
