from rest_framework.response import Response

from common.utils.constants import ResponseCode


def handle_api_call_result(rs):
    if rs["result"]:
        return Success(rs.get("data"))
    else:
        return Fail(rs.get("message"))


class Success(Response):
    def __init__(
            self,
            data=None,
            code=ResponseCode.HTTP_200,
            status=None,
            template_name=None,
            headers=None,
            exception=False,
            content_type=None,
            count=0,
    ):
        format_data = {"result": True, "message": "success", "code": code, "data": data}
        if isinstance(data, list):
            format_data["count"] = count or len(data)
        super(Success, self).__init__(
            data=format_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )


class Fail(Response):
    def __init__(
            self,
            message=None,
            code=ResponseCode.HTTP_200,
            data=None,
            status=None,
            template_name=None,
            headers=None,
            exception=False,
            content_type=None,
    ):
        message_list = []
        if isinstance(message, dict):
            for (k, v) in message.items():
                if isinstance(v, list):
                    message_list.extend(["{}:{}".format(k, i) for i in v])
                else:
                    message_list.append(str(v))
        elif isinstance(message, (list, tuple)):
            message_list.extend(message)
        else:
            message_list.append(str(message))
        format_data = {"result": False, "message": ",".join(message_list), "code": code, "data": data}
        super(Fail, self).__init__(
            data=format_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )


def fail(message=""):
    return {"result": False, "message": message}


def success(data=""):
    return {"result": True, "data": data}
