from rest_framework.throttling import AnonRateThrottle


class ContactMessageThrottle(AnonRateThrottle):
    scope = "contact"