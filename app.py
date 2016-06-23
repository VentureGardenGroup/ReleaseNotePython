from flask import Flask, render_template, request, jsonify, url_for, redirect, abort, flash
import os
from api_helpers import *
from redis import StrictRedis

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


redis = StrictRedis()


@app.route('/index')
@app.route('/', methods=['GET'])
def index():
    projects = get_octopus_dashboard()
    projects = sorted(projects, key=lambda x: x['name'])
    return render_template('index.html', projects=projects)


@app.route('/project/<string:project_id>', methods=['GET'])
def get_project(project_id):
    releases = get_octopus_project_releases(project_id)
    project = get_octopus_project(project_id)
    return render_template('project.html', project=project)


@app.route('/project/releases/<string:project_id>', methods=['GET'])
def get_releases_for_project(project_id):
    releases = get_octopus_project_releases(project_id)
    return jsonify(releases=releases)


@app.route('/release/<string:release_id>', methods=['GET'])
def get_release(release_id):
    release = get_octopus_release(release_id)
    return render_template('release.html', release=release, releasenote='')


@app.route('/release/<string:release_id>', methods=['POST'])
def update_release_note(release_id):
    form = request.form
    print(form)
    if 'id' in form and 'version' in form:
        release_id = form['id']
        version = form['version']
        release_note = form['releaseNote']
        channel_id = form['channelId']
        release_note = release_note.strip()
        issues = release_note.split("||")
        selected_packages = form['selectedPackages']
        selected_packages = selected_packages.split("||")
        packages = []
        for package in selected_packages:
            packages.append({"StepName": package,
                             "Version": version})
        release_note = ''
        for issue in issues:
            release_note += issue
        result = edit_octopus_release_note(release_id=release_id, version=version, channel_id=channel_id,
                                           release_notes=release_note, selected_packages=packages)
        print release_note
        if result:
            flash("Release note updated successfully", 'right')
        else:
            flash('We could not update the release note', 'wrong')
    else:
        flash("Invalid form submitted", 'wrong')
    return redirect(url_for('get_release', release_id=release_id))


@app.route('/issues/<string:project_id>', methods=['GET'])
def get_issues(project_id):
    jira_id = get_jira_project_id_or_slug(project_id)
    tickets = get_jira_project_issues(jira_id)
    return jsonify(tickets=tickets)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0'
    )
