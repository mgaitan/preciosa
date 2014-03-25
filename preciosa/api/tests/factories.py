import factory
from preciosa.precios.tests.factories import UserFactory
from preciosa.api.models import MovilInfo


class MovilInfoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = MovilInfo
    user = factory.SubFactory(UserFactory)
    uuid = factory.Sequence(lambda n: u'uuid_{0}'.format(n))
