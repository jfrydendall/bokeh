''' Provides the ``ServerSession`` class.

'''
from __future__ import absolute_import

class ServerConnection(object):
    ''' Wraps a websocket connection to a client.
    '''

    def __init__(self, protocol, tornado_app, socket, application):
        self._protocol = protocol
        self._tornado_app = tornado_app
        self._socket = socket
        self._application = application
        self._subscribed_sessions = set()

    @property
    def subscribed_sessions(self):
        return self._subscribed_sessions

    @property
    def application(self):
        return self._application

    def subscribe_session(self, session):
        """Keep alive the given session and get document change notifications from it"""
        self._subscribed_sessions.add(session)
        session.subscribe(self)

    def unsubscribe_session(self, session):
        """Allow the session to be discarded and don't get change notifications from it anymore"""
        self._subscribed_sessions.discard(session)
        session.unsubscribe(self)

    def ok(self, message):
        return self.protocol.create('OK', message.header['msgid'])

    def error(self, message, text):
        return self.protocol.create('ERROR', message.header['msgid'], text)

    def send_patch_document(self, session_id, event):
        msg = self.protocol.create('PATCH-DOC', session_id, [event])
        self._socket.send_message(msg)

    def create_session_if_needed(self, session_id):
        return self._tornado_app.create_session_if_needed(self._application, session_id)

    def get_session(self, session_id):
        return self._tornado_app.get_session(session_id)

    @property
    def protocol(self):
        return self._protocol