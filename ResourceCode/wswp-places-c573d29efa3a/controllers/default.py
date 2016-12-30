# -*- coding: utf-8 -*-


def index():
    """Index of locations
    """
    page = common.get_id(request.args)
    page_size = 10
    limitby = (page * page_size, (page + 1) * page_size)
    records = places.search(limitby=limitby)
    result = common.format_records(records)
    return dict(result=result, num_records=len(records), page=page, page_size=page_size)


def view():
    """View a location
    """
    place_id = common.get_id(request.args)
    record = places.get(place_id)
    form = SQLFORM(db.places, record, readonly=True, showid=False)
    return dict(form=form)


def iso():
    """Redirect from ISO to country view
    """
    if request.args:
        record = places.get(iso=request.args(0))
        if record:
            redirect(record.pretty_url)
    redirect(URL(f='index'))


def continent():
    """Show countries in this continent
    """
    if request.args:
        logic = db.places.continent == request.args(0)
        records = places.search(logic=logic)
        result = common.format_records(records)
        continent_name = {'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America', 'SA': 'South America', 'AF': 'Africa', 'AN': 'Antractica', 'OC': 'Oceania'}.get(request.args(0), request.args(0))
        return dict(continent_name=continent_name, result=result)
    redirect(URL(f='index'))


@auth.requires_login()
def edit():
    """Edit a location
    """
    place_id = common.get_id(request.args)
    record = places.get(place_id)
    form = SQLFORM(db.places, record, showid=False, submit_button='Update')
    if form.process().accepted:
        session.flash = 'Place updated'
        redirect(URL(f='view', args=request.args))
    elif form.errors:
        response.flash = 'Form has errors'
    return dict(form=form)


def search():
    """Search interface
    """
    return dict()



def sitemap():
    return dict(records=places.search())


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    if request.args(0) == 'register' and not request.args(1):
        captcha = local_import('captcha', reload=REFRESH)
        auth.settings.register_captcha = captcha.Captcha(request, session)
    return dict(form=auth())


def trap():
    ban_client()
    return ''


def dynamic():
    return dict()
