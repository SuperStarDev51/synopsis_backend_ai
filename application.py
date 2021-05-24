
from flask import Flask, abort, request, jsonify, url_for, render_template
import flask
import os
import threading
import json
from ScriptPreProcessDocx import script_breakdown
from ScriptPreProcessPdf import script_breakdown_pdf
from ScenesGrouping import scenes_grouping
from BuildDocx import build_docx

script_breakdown_lock = threading.Lock()

application = app = Flask(__name__)

# Only enable Flask debugging if an env var is set to true
application.debug = os.environ.get('FLASK_DEBUG') in ['true', 'True']

# Get application version from env
app_version = os.environ.get('APP_VERSION')

# Get cool new feature flag from env
enable_cool_new_feature = os.environ.get('ENABLE_COOL_NEW_FEATURE') in ['true', 'True']


@application.route('/')
def root():
    return("root")

@application.route('/script-breakdown/', methods=['POST'])
def script_breakdown_api():

    data = request.data
    json1 = request.json
    form = request.form

    if not form:
        abort(400)
    print (form)
    #file_path = form.get('data[local_path]')
    file_path = form.get('data[file_path]')
    folder = form.get('data[folder]')
    file_name = form.get('data[file_name]')

    scene_location_bank = form.get('data[scene_location_bank]')
    scene_time_bank = form.get('data[scene_time_bank]')

    #print(scene_location_bank)
    #print(scene_time_bank)

    #with open(json_dest, "w", encoding="utf8") as json_file:
    #    json_file.write(json_data.decode())
    #    json_file.close()

    print ('script-breakdown api')

    with script_breakdown_lock:
        print('script_breakdown start')
        result = script_breakdown(file_path, folder, file_name, scene_location_bank, scene_time_bank, True);
        result_ret = json.loads(result);
        print('script_breakdown end')
        #result2 = build_docx(result_ret, scene_location_bank, scene_time_bank, True);
        #return (result_ret);
        return (json.dumps(result_ret));

@application.route('/script-breakdown-pdf/', methods=['POST'])
def script_breakdown_pdf_api():

    data = request.data
    json1 = request.json
    form = request.form

    if not form:
        abort(400)
    print(form)
    data = form.get('data[data]')
    file_path = form.get('data[file_path]')
    file_path_json = form.get('data[file_path_json]')
    folder = form.get('data[folder]')
    file_name = form.get('data[file_name]')
    file_name_json = form.get('data[file_name_json]')
    scene_location_bank = form.get('data[scene_location_bank]')
    scene_time_bank = form.get('data[scene_time_bank]')

    print ('script-breakdown-pdf api')

    with script_breakdown_lock:
        print('script_breakdown_pdf start')
        result = script_breakdown_pdf(data, file_path, file_path_json, folder, file_name, file_name_json, scene_location_bank, scene_time_bank, True);
        result_ret = json.loads(result);
        print('script_breakdown_pdf end')
        #result2 = build_docx(result_ret, scene_location_bank, scene_time_bank, True);
        #return (result_ret);
        return (json.dumps(result_ret));

@application.route('/scenes-grouping/', methods=['POST'])
def scenes_grouping_api():

    print ('scenes-grouping api')

    data = request.data
    json1 = request.json
    form = request.form

    if not form:
        abort(400)
    print(form)

    file_path_json = form.get('data[file_path_json]')
    folder = form.get('data[folder]')
    file_name_json = form.get('data[file_name_json]')
    file_path_json_ret = form.get('data[file_path_json_ret]')
    file_name_json_ret = form.get('data[file_name_json_ret]')

    with script_breakdown_lock:
        print('scenes_grouping start')
        result = scenes_grouping(file_path_json, folder, file_name_json, file_path_json_ret, file_name_json_ret);
        #result_ret = json.loads(result);
        res_ret = {'seccess': True}
        print('scenes_grouping end')
        return (json.dumps(res_ret));
        #return (json.dumps(result_ret));

@application.route('/build-docx/', methods=['POST'])
def build_docx_api():

    data = request.data
    json1 = request.json
    form = request.form

    if not form:
        abort(400)
    print (form)
    json_script = form.get('data[json_script]')

    print ('build-docx api')

    with script_breakdown_lock:
        print('build_docx start')
        result = build_docx(json_script);
        result_ret = json.loads(result);
        print('build_docx end')
        #return (result_ret);
        return (json.dumps(result_ret));

if __name__ == '__main__':
    #application.run(host='0.0.0.0')
    application.run(host="0.0.0.0", port=8000, debug=True)
