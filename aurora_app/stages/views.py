from flask import (Blueprint, render_template, request, redirect, url_for,
                   Response)

from ..decorators import must_be_able_to
from ..extensions import db
from ..utils import get_or_404, notify
from ..projects.models import Project
from ..deployments.models import Deployment

from .forms import StageForm
from .models import Stage

stages = Blueprint('stages', __name__, url_prefix='/stages')


@stages.route('/create', methods=['GET', 'POST'])
@must_be_able_to('create_stage')
def create():
    project_id = request.args.get('project_id', None)
    project = get_or_404(Project, id=project_id) if project_id else None
    form = StageForm(project=project)

    if form.validate_on_submit():
        stage = Stage()
        form.populate_obj(stage)
        db.session.add(stage)
        db.session.commit()

        notify(u'Stage "{0}" has been created.'.format(stage),
               category='success', action='create_stage')
        return redirect(url_for('stages.view', id=stage.id))

    return render_template('stages/create.html', form=form, id=project_id)


@stages.route('/view/<int:id>')
def view(id):
    stage = get_or_404(Stage, id=id)
    return render_template('stages/view.html', stage=stage)


@stages.route('/edit/<int:id>', methods=['GET', 'POST'])
@must_be_able_to('edit_stage')
def edit(id):
    stage = get_or_404(Stage, id=id)
    form = StageForm(request.form, stage)

    if form.validate_on_submit():
        # Since we don't show deployments in form, we need to set them here.
        form.deployments.data = stage.deployments
        form.populate_obj(stage)
        db.session.add(stage)
        db.session.commit()

        notify(u'Stage "{0}" has been updated.'.format(stage),
               category='success', action='edit_stage')
        return redirect(url_for('stages.view', id=stage.id))

    return render_template('stages/edit.html', stage=stage, form=form)


@stages.route('/delete/<int:id>')
@must_be_able_to('delete_stage')
def delete(id):
    stage = get_or_404(Stage, id=id)

    project_id = stage.project.id if stage.project else None

    notify(u'Stage "{0}" has been deleted.'.format(stage),
           category='success', action='delete_stage')

    db.session.delete(stage)
    db.session.commit()

    if project_id:
        return redirect(url_for('projects.view', id=project_id))

    return redirect(request.args.get('next')
                    or url_for('frontend.index'))


@stages.route('/')
def all():
    stages = Stage.query.all()
    return render_template('stages/all.html', stages=stages)


@stages.route('/export/<int:id>/fabfile.py')
def export(id):
    stage = get_or_404(Stage, id=id)

    deployment = Deployment(stage=stage, tasks=stage.tasks)
    return Response(deployment.code, mimetype='application/python')
