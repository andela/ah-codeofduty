from rest_framework.exceptions import APIException


class ArticleDoesNotExist(APIException):
    status_code = 400
    default_detail = 'An article with this slug was not found.'