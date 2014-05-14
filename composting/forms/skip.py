import colander

from sqlalchemy.orm.exc import NoResultFound

from composting.models.base import DBSession
from composting.models import Skip


SKIP_TYPE_RE = "^[A-Z]{1}$"
skip_type_validator = colander.Regex(
    SKIP_TYPE_RE, "The skip type must be single uppercase letter")


class UniqueSkipTypeValidator():
    def __init__(self, municipality_id, skip_id=None, msg=None):
        self.municipality_id = municipality_id
        self.skip_id = skip_id
        self.msg = msg or "The skip type '{skip_type}' already exists in " \
                          "this municipality"

    def __call__(self, node, value):
        try:
            skip = DBSession.query(Skip)\
                .filter(
                    Skip.municipality_id == self.municipality_id,
                    Skip.skip_type == value)\
                .one()
        except NoResultFound:
            # no match
            pass
        else:
            if (self.skip_id is None
               or (self.skip_id is not None and self.skip_id != skip.id)):
                raise colander.Invalid(node, self.msg.format(skip_type=value))


@colander.deferred
def deferred_skip_type_validator(node, kw):
    return colander.All(
        skip_type_validator,
        UniqueSkipTypeValidator(kw['municipality_id'], kw.get('skip_id')))


class SkipForm(colander.MappingSchema):
    skip_type = colander.SchemaNode(
        colander.String(encoding='utf-8'),
        title="Skip Type", description="A to Z",
        validator=deferred_skip_type_validator)
    small_length = colander.SchemaNode(
        colander.Float(), title="Small Length")
    large_length = colander.SchemaNode(
        colander.Float(), title="Large Length")
    small_breadth = colander.SchemaNode(
        colander.Float(), title="Small Breadth")
    large_breadth = colander.SchemaNode(
        colander.Float(), title="Large Breadth")

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['small_length'] > value['large_length']:
            valid = False
        exc['small_length'] = "The small length must be less than the " \
                              "large length"

        if value['small_breadth'] > value['large_breadth']:
            valid = False
            exc['small_breadth'] = "The small breadth must be less than the " \
                                   "large breadth"

        # check that skip type is unique for this municipality


        if not valid:
            raise exc