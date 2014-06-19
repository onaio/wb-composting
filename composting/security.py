from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext


pwd_context = CryptContext()


class KeyValue(object):

    def __init__(self, name, label):
        self.t = (name, label,)

    @property
    def key(self):
        return self.t[0]

    @property
    def label(self):
        return self.t[1]


MUNICIPALITY_MANAGE_ALL = KeyValue(
    'p:municipality-manage', "List All Municipalities")
MUNICIPALITY_SHOW_ANY = KeyValue(
    'p:municipality-show', "Access Any Municipality")
MUNICIPALITY_SHOW_OWN = KeyValue(
    'p:municipality-show:{}', "Only Access Their Own Municipality")
MUNICIPALITY_EDIT_ANY = KeyValue(
    'p:municipality-edit', "Edit Any Municipality's Details")
MUNICIPALITY_EDIT_OWN = KeyValue(
    'p:municipality-edit:{}',
    "Only Edit Their Own Municipality's Details")

# User Permissions
USER_MANAGE_ALL = KeyValue(
    'p:user-manage', "Manage All Users")


NEMA = KeyValue('nema', "NEMA")
WB = KeyValue('wb', "World Bank")
ENV_OFFICER = KeyValue('env_officer', "Environmental Officer")
SITE_MANAGER = KeyValue('sm', "Site Manager")

GROUPS = [NEMA, WB, ENV_OFFICER, SITE_MANAGER]


GROUP_PERMISSIONS = {
    WB.key: [MUNICIPALITY_MANAGE_ALL.key, MUNICIPALITY_SHOW_ANY.key,
             MUNICIPALITY_EDIT_ANY.key],
    NEMA.key: [MUNICIPALITY_MANAGE_ALL.key, MUNICIPALITY_SHOW_ANY.key,
               MUNICIPALITY_EDIT_ANY.key, USER_MANAGE_ALL.key],
    ENV_OFFICER.key: [MUNICIPALITY_SHOW_OWN.key, MUNICIPALITY_EDIT_OWN.key],
    SITE_MANAGER.key: [MUNICIPALITY_SHOW_OWN.key, MUNICIPALITY_EDIT_OWN.key]
}


def group_finder(user_id, request):
    from composting.models.user import User
    try:
        user = User.get(User.id == user_id)
    except NoResultFound:
        return None
    else:
        municipality_id = user.municipality_id

        effective_principals = []

        # determine the user's permissions and extend effective_principals
        # with the those
        permissions = GROUP_PERMISSIONS.get(user.group, [])

        # if the user has municipality-edit permissions and also belongs to a
        # municipality, add a 'p:municipality-edit:1' permission
        if municipality_id is not None:
            permissions = [p.format(municipality_id) for p in
                           GROUP_PERMISSIONS.get(user.group, [])]

        effective_principals.extend(permissions)

        return effective_principals


def friendly_group_name(group_key, request):
    group = filter(lambda g: g.key == group_key, GROUPS)[0]
    return group.label
