import colander
from deform.widget import TextInputWidget


MIN_VOLUME = 0.01


class SiteProfileForm(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.Str(), title="Municipality Name",
        widget=TextInputWidget(size=30))
    box_volume = colander.SchemaNode(
        colander.Float(), title="Standard Box's Volume",
        validator=colander.Range(
            min=MIN_VOLUME, min_err="The length must be greater than 0"))
    wheelbarrow_volume = colander.SchemaNode(
        colander.Float(), title="Wheelbarrow's Volume",
        validator=colander.Range(
            min=MIN_VOLUME, min_err="The length must be greater than 0"))
    leachete_tank_length = colander.SchemaNode(
        colander.Float(), title="Leachete Tank's Length",
        validator=colander.Range(
            min=MIN_VOLUME, min_err="The length must be greater than 0"))
    leachete_tank_width = colander.SchemaNode(
        colander.Float(), title="Leachete Tank's Width",
        validator=colander.Range(
            min=MIN_VOLUME, min_err="The length must be greater than 0"))