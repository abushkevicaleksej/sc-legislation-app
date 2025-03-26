from marshmallow import Schema, fields, validate

from service.agents.abstract.auth_agent import AuthStatus, RegStatus


class AuthSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf([e for e in AuthStatus]))
    message = fields.Str(required=False)


class RegSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf([e for e in RegStatus]))
    message = fields.Str(required=False)