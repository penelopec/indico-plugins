# copy file under:
#   /opt/indico/.venv/lib/python2.7/site-packages/indico/web
# to test the schema use this URLs:
#   https://<indicoserver>/schema-test/event/<event id>/
#   https://<indicoserver>/schema-test/attachment/<attachment id>/
#   https://<indicoserver>/schema-test/contribution/<contribution id>/
#   https://<indicoserver>/schema-test/subcontribution/<subcontribution id>/
#   https://<indicoserver>/schema-test/note/<note id>/

from __future__ import unicode_literals

import itertools
from marshmallow_enum import EnumField

from indico.core.db.sqlalchemy.principals import PrincipalType
from indico.core.db.sqlalchemy.protection import ProtectionMode
from indico.core.db.sqlalchemy.links import LinkType
from indico.core.marshmallow import mm
from indico.modules.attachments.models.attachments import Attachment, AttachmentType
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote
from indico.modules.events.sessions.models.sessions import Session
from indico.modules.events import Event
from indico.modules.events.models.events import EventType
from indico.modules.events.models.persons import EventPersonLink
from indico.web.flask.util import url_for

from tika import parser


def _get_location(obj):
    if obj.venue_name and obj.room_name:
        return '{}: {}'.format(obj.venue_name, obj.room_name)
    elif obj.venue_name or obj.room_name:
        return obj.venue_name or obj.room_name
    else:
        return None


def _get_location_subcontribution(subcontribution):
    contribution_id = subcontribution.contribution.id
    obj = Contribution.get_one(contribution_id)
    return _get_location(obj)


def _get_identifiers(principal):
    if principal.principal_type == PrincipalType.user:
        # Instead of using the email this uses `User:ID`.
        # Since the user can change the email this is better as
        # it will ensure that only this given Indico user has access.
        # If you want to stick with email, simply replace it with
        # 'User:{}'.format(principal.email)
        yield principal.identifier
        yield '{}'.format(principal.email)
    elif principal.principal_type == PrincipalType.event_role:
        for user in principal.members:
            # same thing here
            yield user.identifier
            yield '{}'.format(principal.email)
    elif principal.is_group:
        yield principal.identifier


def _get_category_path(obj):
    if isinstance(obj, Event):
        event_id = obj.id
    elif isinstance(obj, Attachment):
        event_id = obj.folder.event.id
    else:
        event_id = obj.event.id
    event = Event.get_one(event_id)
    return event.category.chain_titles[1:]


def _get_event_acl(event):
    if event.effective_protection_mode == ProtectionMode.public:
        acl = ['']
    else:
        acl = set(itertools.chain.from_iterable(_get_identifiers(x.principal) for x in event.acl_entries))
    return {'read': sorted(acl), 'owner': [''], 'update': [''], 'delete': ['']}


def _get_attachment_acl(attachment):
    linked_object = attachment.folder.object

    if attachment.is_self_protected:
        principals = {p for p in attachment.acl} | set(linked_object.get_manager_list(recursive=True))
    elif attachment.is_inheriting and attachment.folder.is_self_protected:
        principals = {p for p in attachment.folder.acl} | set(linked_object.get_manager_list(recursive=True))
    else:
        principals = linked_object.get_access_list()

    acl = set(itertools.chain.from_iterable(_get_identifiers(x) for x in principals))
    if not len(acl):
         acl.add('')
    return {'read': sorted(acl), 'owner': [''], 'update': [''], 'delete': ['']}


def _get_obj_acl(obj):
    if obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    elif obj.is_inheriting and obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    else:
        principals = obj.get_access_list()

    acl = set(itertools.chain.from_iterable(_get_identifiers(x) for x in principals))
    if not len(acl):
         acl.add('')
    return {'read': sorted(acl), 'owner': [''], 'update': [''], 'delete': ['']}


def _get_subcontribution_acl(subcontribution):
    contribution_id = subcontribution.contribution.id
    obj = Contribution.get_one(contribution_id)
    return  _get_obj_acl(obj)


def _get_eventnote_acl(eventnote):
    event_id = eventnote.event.id
    session_id = eventnote.session.id if eventnote.session else None
    contribution_id =  None
    if eventnote.contribution or eventnote.subcontribution:
        contribution_id = eventnote.subcontribution.contribution.id if eventnote.subcontribution else eventnote.contribution.id

    if contribution_id:
        obj = Contribution.get_one(contribution_id)
        return  _get_obj_acl(obj)
    elif session_id:
        obj = Session.get_one(session_id)
        return  _get_obj_acl(obj)
    else:
        obj = Event.get_one(event_id)
        return  _get_event_acl(obj)


def _get_attachment_content(attachment):
    if attachment.type == AttachmentType.file:
        import tika    # for test purposes
        ##from indico_livesync_json.plugin import JsonLiveSyncPlugin
        tika.initVM()   # for test purposes
        parsedfile = parser.from_file(attachment.absolute_download_url)['content']
        ##parsedfile = parser.from_file(attachment.absolute_download_url, LivesyncJsonPlugin.settings.get('tika_server'))['content']
        return parsedfile
    else:
        return None


def _get_attachment_contributionid(attachment):
    return attachment.folder.contribution.id if attachment.folder.link_type == LinkType.contribution else None


def _get_attachment_subcontributionid(attachment):
    return attachment.folder.subcontribution.id if attachment.folder.link_type == LinkType.subcontribution else None


def _get_eventnote_contributionid(eventnote):
    contribution_id =  None
    if eventnote.contribution or eventnote.subcontribution:
        contribution_id =  eventnote.subcontribution.contribution.id if eventnote.subcontribution else eventnote.contribution.id
    return contribution_id


def _get_contribution_url(obj):
    return url_for('contributions.display_contribution', obj, _external=True)


def _get_subcontribution_url(obj):
    return url_for('contributions.display_subcontribution', obj, _external=True)


def _get_eventnote_url(obj):
    return url_for('event_notes.view', obj, _external=True)
    

def _get_people_list(obj):
    return [
        '{} ({})'.format(pl.full_name, pl.affiliation) if pl.affiliation else pl.full_name
        for pl in obj.person_links
    ]


class PersonLinkSchema(mm.Schema):
    # Not using a ModelSchema here so this can be used for contribution person links etc. as well!
    name = mm.String(attribute='full_name')
    affiliation = mm.String()

    class Meta:
        model = EventPersonLink
        fields = ('name', 'affiliation')


def _get_event_data(event):
    id = event.id
    category_path = _get_category_path(event)
    event_type = event.type_.title
    title = event.title
    description = event.description
    location = _get_location(event)
    speakers_chairs = _get_people_list(event)
    url = event.external_url
    return {'id':id, 'category_path':category_path, 'event_type':event_type, 'title':title, 'description':description,
            'location':location, 'speakers_chairs':speakers_chairs, 'url':url}

class EventSchema(mm.ModelSchema):
    _access = mm.Function(_get_event_acl)
    _data = mm.Function(_get_event_data)
    creation_date = mm.DateTime(attribute='created_dt')
    start_date = mm.DateTime(attribute='start_dt')
    end_date = mm.DateTime(attribute='end_dt')

    class Meta:
        model = Event
        fields = ('_access', '_data', 'creation_date', 'start_date', 'end_date')


def _get_attachment_data(attachment):
    id = attachment.id
    category_path = _get_category_path(attachment)
    event_id = attachment.folder.event.id
    contribution_id = _get_attachment_contributionid(attachment)
    subcontribution_id =_get_attachment_subcontributionid(attachment)
    filename = attachment.file.filename
    content = _get_attachment_content(attachment)
    url = attachment.absolute_download_url
    
    return {'id':id, 'category_path':category_path, 'event_id':event_id, 'contribution_id':contribution_id,
            'subcontribution_id':subcontribution_id, 'filename':filename, 'content':content, 'url':url}

class AttachmentSchema(mm.ModelSchema):
    _access = mm.Function(_get_attachment_acl)
    _data = mm.Function(_get_attachment_data)
    creation_date = mm.DateTime(attribute='modified_dt')

    class Meta:
        model = Event
        fields = ('_access', '_data', 'creation_date')


def _get_contribution_data(contribution):
    id = contribution.id
    category_path = _get_category_path(contribution)
    event_id = contribution.event_id
    title = contribution.title
    description = contribution.description
    location = _get_location(contribution)
    list_of_persons = _get_people_list(contribution)
    url = _get_contribution_url(contribution)
    
    return {'id':id, 'category_path':category_path, 'event_id':event_id,  'title':title, 'description':description,
            'location':location, 'list_of_persons':list_of_persons, 'url':url}

class ContributionSchema(mm.ModelSchema):
    _access = mm.Function(_get_obj_acl)
    _data = mm.Function(_get_contribution_data)
    start_date = mm.DateTime(attribute='start_dt')
    end_date = mm.DateTime(attribute='end_dt')

    class Meta:
        model = Event
        fields = ('_access', '_data', 'start_date', 'end_date')


def _get_subcontribution_data(subcontribution):
    id = subcontribution.id
    category_path = _get_category_path(subcontribution)
    event_id = subcontribution.event.id
    contribution_id = subcontribution.contribution_id
    title = subcontribution.title
    description = subcontribution.description
    location = _get_location_subcontribution(subcontribution)
    list_of_persons = _get_people_list(subcontribution)
    url = _get_subcontribution_url(subcontribution)
    
    return {'id':id, 'category_path':category_path, 'event_id':event_id, 'contribution_id':contribution_id,
             'title':title, 'description':description, 'location':location, 'list_of_persons':list_of_persons, 
             'url':url}

class SubContributionSchema(mm.ModelSchema):
    _access = mm.Function(_get_subcontribution_acl)
    _data = mm.Function(_get_subcontribution_data)

    class Meta:
        model = Event
        fields = ('_access', '_data')


def _get_eventnote_data(eventnote):
    id = eventnote.id
    category_path = _get_category_path(eventnote)
    event_id = eventnote.event_id
    contribution_id = _get_eventnote_contributionid(eventnote)
    subcontribution_id =eventnote.subcontribution_id
    content = eventnote.html
    url = _get_eventnote_url(eventnote)
    
    return {'id':id, 'category_path':category_path, 'event_id':event_id, 'contribution_id':contribution_id,
             'subcontribution_id':subcontribution_id, 'content':content, 'url':url}


class EventNoteSchema(mm.ModelSchema):
    _access = mm.Function(_get_eventnote_acl)
    _data = mm.Function(_get_eventnote_data)
    creation_date = mm.DateTime(attribute='current_revision.created_dt')

    class Meta:
        model = Event
        fields = ('_access', '_data', 'creation_date')




# If you want to test this quickly, keep the code below and the file as indico/web/blueprint.py
# and go to https://yourinstance/schema-test/event/EVENTID

from indico.web.flask.wrappers import IndicoBlueprint
import json
bp = IndicoBlueprint('test', __name__)

@bp.route('/schema-test/event/<int:event_id>/')
def event_test(event_id):
    event = Event.get_one(event_id)
    response = EventSchema().jsonify(event)
    data = response.get_json()

    test = 'This is the URL and rest for ES events.json'
    data['$schema'] = test
    response.data = json.dumps(data)
    return response     #(EventSchema().jsonify(event)).append({'$schema':test})

@bp.route('/schema-test/attachment/<int:attachment_id>/')
def attachment_test(attachment_id):
    attachment = Attachment.get_one(attachment_id)
    return AttachmentSchema().jsonify(attachment)

@bp.route('/schema-test/contribution/<int:contribution_id>/')
def contribution_test(contribution_id):
    contribution = Contribution.get_one(contribution_id)
    return ContributionSchema().jsonify(contribution)

@bp.route('/schema-test/subcontribution/<int:subcontribution_id>/')
def subcontribution_test(subcontribution_id):
    subcontribution = SubContribution.get_one(subcontribution_id)
    return SubContributionSchema().jsonify(subcontribution)

@bp.route('/schema-test/note/<int:note_id>/')
def note_test(note_id):
    note = EventNote.get_one(note_id)
    return EventNoteSchema().jsonify(note)

