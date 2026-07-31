# request_started / request_finished

- **ID:** `signals-request`
- **Category:** signals
- **Source:** §3.3 Signals
- **Tags:** `signals`, `instrumentation`, `request`

## Canonical pattern (Django / HTMX / Hyperscript way)
request_started and request_finished fire at the boundaries of the HTTP handling cycle and exist for instrumentation: metrics, tracing, debug tooling. They carry no business meaning.

## Laravel / MVC default (what AI typically generates)
Laravel: equivalent is middleware/terminating callbacks or event listeners on RequestHandled; AI sometimes tries to do per-request app logic (logging user activity) in such hooks where middleware or an explicit call is clearer.

## Why Django differs
Django reserves request-level signals for framework instrumentation because they fire for every request (including static/admin) and lack view context. Real per-request logic belongs in middleware where ordering and short-circuiting are explicit.

## Example
from django.core.signals import request_started, request_finished
from django.dispatch import receiver
import time

@receiver(request_started)
def start_timer(sender, environ, **kwargs):
    environ['request_start'] = time.monotonic()

@receiver(request_finished)
def log_duration(sender, **kwargs):
    metrics.observe('request_finished')  # instrumentation only
