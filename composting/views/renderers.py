import tablib


class TablibRenderer(object):

    def __init__(self, info):  # noqa
        pass

    def initialize_dataset(self, value, system):  # noqa
        headers = None
        rows = None

        municipality = value.get('municipality')
        start_date = value.get('start')
        end_date = value.get('end')

        headers, rows = municipality.report(start_date, end_date)

        dataset = tablib.Dataset(headers)
        dataset.title = municipality.name

        for row in rows:
            dataset.append(row)
        return dataset


class TablibXLSXRenderer(TablibRenderer):
    extension = 'xlsx'

    def __call__(self, value, system):
        dataset = self.initialize_dataset(value, system)
        request = system['request']
        response = request.response
        response.content_type = \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.content_disposition = "attachment; filename={}.{}".format(
            dataset.title, self.extension)
        return dataset.xlsx
