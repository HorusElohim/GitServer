from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import os
from GitServer import PackageName
from GitServer.util import get_logger
from GitServer.path import get_home_path
from GitServer.git import GitRepo, create_git_dict
from datetime import datetime

# Logger
Logger = get_logger('Server', get_home_path(PackageName))

# GitRepo
gr = GitRepo(**create_git_dict(name='develop', path='/data/projects/adcc_developer_pc_profile', auto_clone=False))
# Open Repo
gr.open()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def clean_submodule_info(raw_status, raw_tag_commit):
    submodule_status = dict()
    # Clean submodule status
    for sub_raw in raw_status.split('Entering'):
        if sub_raw != '':
            sub_temp = sub_raw.split('\t')
            sub_raw_status = sub_temp[0].split("\'")
            sub_name = sub_raw_status[1]
            sub_branch = sub_raw_status[3]
            # Check if there are modifications
            sub_modification = []
            if len(sub_temp) > 1:
                for x in sub_temp[1:]:
                    sub_modification.append(x)
            submodule_status.update({sub_name: {
                'branch': sub_branch,
                'changes': sub_modification
            }})
    # Clean submodule tag and commit
    raw_tag_commit = raw_tag_commit.split()
    for i in range(0, len(raw_tag_commit), 3):
        submodule_status[raw_tag_commit[i + 1]].update({
            'tag': raw_tag_commit[i + 2].replace("(", "").replace(")", ""),
            'id': raw_tag_commit[i]
        })
    return submodule_status


def background_thread():
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(3)
        # Dict submodule
        #      module_name:
        #                 tag:
        #                 branch:
        #                 commit id:
        #                 changes:
        submodule = clean_submodule_info(
            gr.git_action('submodule', 'foreach', '--recursive', 'git status'),
            gr.git_action('submodule', 'status')
        )

        data = {'time': f'{datetime.now()}', 'submodule_status': submodule}
        socketio.emit('git_submodule_status', data)
        Logger.info('Server update')


@app.route('/')
def index():
    return render_template('main.html',
                           async_mode=socketio.async_mode,
                           vehicle_name=os.getenv('VEHICLE_NAME'),
                           git_profile_path=gr.params.git.path)


@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']}, broadcast=True)


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
        Logger.info('disconnected')

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response', {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})
    Logger.info('new connection')


@socketio.on('disconnect')
def test_disconnect():
    Logger.info('Client disconnected', request.sid)


def main():
    Logger.info('Server has started.')
    socketio.run(app, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
