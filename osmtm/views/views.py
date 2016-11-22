from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized

import re
import sqlalchemy
from sqlalchemy import (
    desc,
    or_,
    and_,
)

from ..models import (
    DBSession,
    FrontProjects,
    Project,
    ProjectTranslation,
    User,
    TaskLock,
    Tag,
)

from webhelpers.paginate import (
    PageURL_WebOb,
    Page
)

from geojson import (
    FeatureCollection
)

from .project import check_project_expiration

from pyramid.security import authenticated_userid

from sqlalchemy.orm import joinedload


@view_config(route_name='home', renderer='home.mako')
def home(request):
    check_project_expiration()

    # no user in the DB yet
    if DBSession.query(User).filter(User.role == User.role_admin) \
                .count() == 0:   # pragma: no cover
        request.override_renderer = 'start.mako'
        return dict(page_id="start")

    front_tags = DBSession.query(FrontProjects).all()
    wells = []
    for ii in range(3):
      try:
        the_tag = front_tags[ii]
        query = DBSession.query(Project).filter(Project.tags.any(id=the_tag.tag)).order_by(Project.priority.asc()).all()
        wells.append(query)
      except:
        wells.append(None)

    names = []
    for tag in front_tags:
      try:
        names.append(DBSession.query(Tag.name).filter(Tag.id == tag.tag).one()[0])
      except:
        names.append(None)

    return dict(page_id="home", well1=wells[0], well2=wells[1], well3=wells[2], front_tags=names)


@view_config(route_name='front_tags', renderer='front_tags.mako')
def front_tag(request):
    tags = DBSession.query(Tag).all()

    if 'form.submitted' in request.params:
      front_tags = [x[4:] for x in request.params if 'tag_' in x]
      for i in range(3):
        if len(front_tags) > i:
          t = DBSession.query(FrontProjects).filter(FrontProjects.well == i).one()
          t.tag = front_tags[i]
          DBSession.add(t)
          DBSession.flush()
        else:
          t = DBSession.query(FrontProjects).filter(FrontProjects.well == i).one()
          t.tag = None
          DBSession.add(t)
          DBSession.flush()

    front_tags = DBSession.query(FrontProjects).all()

    if len(front_tags) != 3:
      f1 = FrontProjects(0, None)
      f2 = FrontProjects(1, None)
      f3 = FrontProjects(2, None)
      DBSession.add(f1)
      DBSession.add(f2)
      DBSession.add(f3)
    DBSession.flush()

    front_tags = DBSession.query(FrontProjects).all()

    return dict(page_id="front_tags", tags=tags, front_tags=front_tags)


@view_config(route_name='list', renderer='list.mako')
def list_of_projects(request):
    check_project_expiration()

    # no user in the DB yet
    if DBSession.query(User).filter(User.role == User.role_admin) \
                .count() == 0:   # pragma: no cover
        request.override_renderer = 'start.mako'
        return dict(page_id="start")

    paginator, tags = get_projects(request, 10)

    return dict(page_id="list", paginator=paginator, tags=tags)


@view_config(route_name='home_json', renderer='json')
def home_json(request):
    if not request.is_xhr:
        request.response.content_disposition = \
            'attachment; filename="hot_osmtm.json"'
    paginator, _ = get_projects(request, 100)
    request.response.headerlist.append(('Access-Control-Allow-Origin', '*'))
    return FeatureCollection([project.to_feature() for project in paginator])


def get_projects(request, items_per_page):
    query = DBSession.query(Project) \
        .options(joinedload(Project.translations['en'])) \
        .options(joinedload(Project.translations[request.locale_name])) \
        .options(joinedload(Project.author)) \
        .options(joinedload(Project.area))

    user_id = authenticated_userid(request)
    user = None
    if user_id is not None:
        user = DBSession.query(User).get(user_id)

    if not user:
        filter = Project.private == False  # noqa
    elif not user.is_admin and not user.is_project_manager:
        query = query.outerjoin(Project.allowed_users)
        filter = or_(Project.private == False,  # noqa
                     User.id == user_id)
    else:
        filter = True  # make it work with an and_ filter

    if not user or (not user.is_admin and not user.is_project_manager):
        filter = and_(Project.status == Project.status_published, filter)

    if 'search' in request.params:
        s = request.params.get('search')
        PT = ProjectTranslation

        '''This pulls out search strings with "tag:" from the query
           and searches for project tags that match those strings.'''
        t = re.findall('tag:\S+', s)
        if t:
            s = re.sub('tag:\S+', '', s)
            tags = DBSession.query(Tag) \
                            .filter(or_(*[Tag.name.ilike('%%%s%%' % tag[4:])
                                          for tag in t])).all()
            if len(tags) > 0:
                tag_ids = DBSession.query(Project.id) \
                          .filter(and_(*[Project.tags.any(id=tag.id)
                                         for tag in tags])).all()
                filter = and_(Project.id.in_(tag_ids), filter)
        else:
            tags = None

        search_filter = or_(PT.name.ilike('%%%s%%' % s),
                            PT.short_description.ilike('%%%s%%' % s),
                            PT.description.ilike('%%%s%%' % s),)
        '''The below code extracts all the numerals in the
           search string as a list, if there are some it
           joins that list of number characters into a string,
           casts it as an integer and searchs to see if there
           is a project with that id. If there is, it adds
           it to the search results.'''
        digits = re.findall('\d+', s)
        if digits:
            search_filter = or_(
                ProjectTranslation.id == (int(''.join(digits))),
                search_filter)
        ids = DBSession.query(ProjectTranslation.id) \
                       .filter(search_filter) \
                       .all()
        filter = and_(Project.id.in_(ids), filter)

    else:
        tags = None

    # filter projects on which the current user worked on
    if request.params.get('my_projects', '') == 'on':
        ids = DBSession.query(TaskLock.project_id) \
                       .filter(TaskLock.user_id == user_id) \
                       .all()

        if len(ids) > 0:
            filter = and_(Project.id.in_(ids), filter)
        else:
            # IN-predicate  with emty sequence can be expensive
            filter = and_(False == True)  # noqa

    if (request.params.get('show_archived', '') != 'on'):
        filter = and_(Project.status != Project.status_archived, filter)

    sort_by = 'project.%s' % request.params.get('sort_by', 'priority')
    direction = request.params.get('direction', 'asc')
    direction_func = getattr(sqlalchemy, direction, None)
    sort_by = direction_func(sort_by)

    query = query.order_by(sort_by, desc(Project.id))

    query = query.filter(filter)

    page = int(request.params.get('page', 1))
    page_url = PageURL_WebOb(request)
    paginator = Page(query, page, url=page_url, items_per_page=items_per_page)

    return paginator, tags


@view_config(route_name='about', renderer='about.mako')
def about(request):
    return dict(page_id="about")


@view_config(route_name="user_prefered_editor", renderer='json')
def user_prefered_editor(request):
    editor = request.matchdict['editor']
    request.response.set_cookie('prefered_editor', value=editor,
                                max_age=20 * 7 * 24 * 60 * 60)

    return dict()


@view_config(route_name="user_prefered_language", renderer='json')
def user_prefered_language(request):
    language = request.matchdict['language']
    request.response.set_cookie('_LOCALE_', value=language,
                                max_age=20 * 7 * 24 * 60 * 60)
    return dict()


@view_config(context='pyramid.httpexceptions.HTTPUnauthorized')
def unauthorized(request):
    if request.is_xhr:
        return HTTPUnauthorized()
    return HTTPFound(request.route_path('login',
                                        _query=[('came_from', request.url)]))
