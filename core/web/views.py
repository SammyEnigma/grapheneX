#!/usr/bin/python3.7
# -*- coding: utf-8 -*-

from core.web import app, logger, socketio
from core.utils.helpers import check_os, get_os_info, get_modules
from flask import render_template
from flask_socketio import emit

module_dict = get_modules()
current_namespace = list(module_dict.keys())[0]
length_list = [len(value) for key, value in module_dict.items()]

@app.route('/')
def main():
    return render_template(
        'index.html',
        title="grapheneX [Web]",
        sys_info=get_os_info(),
        mod_count=sum(length_list))

@socketio.on('get_namespaces')
def send_namespaces(data):
    emit('get_namespaces', {'namespaces': list(module_dict.keys())})

@socketio.on('get_current_namespace')
def send_current_namespace(data):
    emit('get_current_namespace', {'current_namespace': current_namespace})

@socketio.on('send_current_namespace')
def get_current_namespace(data):
    modules = list()
    mod_dict = module_dict.get(data)
    if mod_dict == None:
        logger.warn(f"Non-existent namespace: {data}.")
    else:
        current_namespace = data
        for name, mod in mod_dict.items():
            modules.append({
                'name': name,
                'desc': mod.desc,
                'source': mod.command
            })
        logger.info(f'Sending modules of {data}.')
        emit('get_module', modules)

@socketio.on('search_module')
def search_module(data):
    result = {name: mod for name, mod in module_dict.get(
        current_namespace).items() if data["query"].lower() in name.lower()}
    payload = list()
    for name, mod in result.items():
        payload.append({
            'name': name,
            'desc': mod.desc,
            'source': mod.command
        })
    emit('search_module', {'result': payload})

@socketio.on('harden')
def hardening_exec(data):
    try:
        logger.info("Executing the hardening command of " + current_namespace + "/" + data)
        hrd = module_dict[current_namespace][data]
        out = hrd.execute_command()
        print(out)
        emit(data + "_log", {"msg": out, "state":"output"})
        success_msg = "Hardening command executed successfully."
        emit(data + "_log", {"msg": success_msg, "state":"success"})
        logger.info(success_msg)
    except PermissionError:
        err_msg = "Insufficient permissions for hardening."
        if check_os():
            err_msg += " Get admin rights and rerun the grapheneX."                    
        else:
            err_msg += " Try running the grapheneX with sudo."
        emit(data + "_log", {"msg": err_msg, "state":"error"})
        logger.error(err_msg)
    except Exception as e:
        fail_msg = "Failed to execute hardening command. " + str(e)
        emit(data + "_log", {"msg": fail_msg, "state":"error"})
        logger.error(fail_msg)