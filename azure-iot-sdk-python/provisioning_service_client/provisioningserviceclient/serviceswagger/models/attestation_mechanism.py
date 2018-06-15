# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class AttestationMechanism(Model):
    """Device attestation method.

    :param type: Possible values include: 'none', 'tpm', 'x509'
    :type type: str or ~serviceswagger.models.enum
    :param tpm:
    :type tpm: ~serviceswagger.models.TpmAttestation
    :param x509:
    :type x509: ~serviceswagger.models.X509Attestation
    """

    _validation = {
        'type': {'required': True},
    }

    _attribute_map = {
        'type': {'key': 'type', 'type': 'str'},
        'tpm': {'key': 'tpm', 'type': 'TpmAttestation'},
        'x509': {'key': 'x509', 'type': 'X509Attestation'},
    }

    def __init__(self, type, tpm=None, x509=None):
        self.type = type
        self.tpm = tpm
        self.x509 = x509
