from .._json import error_envelope

NO_TAP_TOKEN = error_envelope(
    "not_configured",
    "No Proofpoint TAP credentials. Send the X-Proofpoint-Tap-Service-Principal "
    "and X-Proofpoint-Tap-Service-Secret headers.",
    False,
)
NO_ESSENTIALS_TOKEN = error_envelope(
    "not_configured",
    "No Proofpoint Essentials credentials. Send the X-Proofpoint-Essentials-Username, "
    "X-Proofpoint-Essentials-Password, and X-Proofpoint-Essentials-Base-Url headers.",
    False,
)
