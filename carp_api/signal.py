from flask import signals

namespace = signals.Namespace()

app_shutdown = namespace.signal('app_shutdown')
