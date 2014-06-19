import colander

from deform.widget import SelectWidget

from composting import security
from composting.models.municipality import Municipality


@colander.deferred
def user_role_widget(node, kw):
    return SelectWidget(
        values=[(g.key, g.label) for g in security.GROUPS])


@colander.deferred
def municipality_widget(node, kw):
    # start with a blank
    municipalities = [('', '')]
    municipalities.extend([(m.id, m.name) for m in Municipality.all()])
    return SelectWidget(values=municipalities)


class UserForm(colander.MappingSchema):
    group = colander.SchemaNode(
        colander.String(encoding='utf-8'), title="Role",
        widget=user_role_widget)
    municipality_id = colander.SchemaNode(
        colander.String(), title="Municipality",
        widget=municipality_widget, missing=None)

    def validator(self, node, value):
        exc = colander.Invalid(node, "")
        valid = True
        if value['municipality_id'] is None and value['group']\
                in [security.ENV_OFFICER.key, security.SITE_MANAGER.key]:
            valid = False
            exc['municipality_id'] = "You must specify the municipality for" \
                                     " site managers and environmental" \
                                     " officers"
        if not valid:
            raise exc