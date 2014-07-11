import datetime

from pyramid import testing

from composting.models.municipality import Municipality
from composting.tests.test_base import TestBase
from composting.views.renderers import TablibXLSXRenderer


class TestTablibXLSXRenderer(TestBase):

    def test_renderer_output(self):
        self.setup_test_data()
        request = testing.DummyRequest()
        renderer = TablibXLSXRenderer({})
        municipality = Municipality.all()[0]

        data = {'municipality': municipality,
                'start': datetime.date(2014, 6, 1),
                'end': datetime.date(2014, 6, 30)}

        renderer(data, {'request': request})
        self.assertEqual(
            request.response.content_type,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
