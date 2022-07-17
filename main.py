import datetime
import json
import os

import requests

DIDA365_COOKIE = os.environ["DIDA365_COOKIE"]
CORPID = os.environ["CORPID"]
CORPSECRET = os.environ["CORPSECRET"]
AGENTID = os.environ["AGENTID"]


def get_dida365_data(cookie):
    """ 获dida365日程数据
    params:
      cookie 滴答清单的cookie
    return:
      滴答清单数据
    """
    def handle_detail(task):
        """ 处理具体任务数据
        params:
          task dida365的任务数据
        return：
          需要展示的数据信息
        """
        utc_before = datetime.datetime.utcnow()+datetime.timedelta(days=7)
        utc_time = datetime.datetime.fromisoformat(task["startDate"][:-5])
        local_time = utc_time+datetime.timedelta(hours=8)
        if utc_before >= utc_time:
            return "  {}({})\n".format(task["title"], local_time.strftime("%m-%d"))
        else:
            return ""
    url = "https://api.dida365.com/api/v2/batch/check/0"
    headers = {
        'cookie': cookie,
        'user-agent': '',
    }
    response = requests.request("GET", url, headers=headers)
    details = json.loads(response.text)
    # 数据加工
    res = ""
    # 将指定日期前的任务提取出来
    for detail in details["syncTaskBean"]["update"]:
        if "startDate" in detail.keys():
            res += handle_detail(detail)
    return res


def send(corpid, agentid, corpsecret, content):
    """ 通过企业微信途径完成信息发送
    param:
      corpid      企业id
      agentid     应用id
      corpsecret  应用secret
      content     信息内容
    return:
      信息发送结果
    """
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    payload = {
        "corpid": corpid,
        "corpsecret": corpsecret,
    }
    response = requests.request("GET", url, params=payload)
    token = json.loads(response.text)
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(
        token["access_token"])
    payload = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": content
        }
    }

    response = requests.request(
        "POST", url, json=payload)
    return json.loads(response.text)


if __name__ == '__main__':
    res = "最近七日工作：\n"
    res += get_dida365_data(cookie=DIDA365_COOKIE)
    send(corpid=CORPID,
         agentid=AGENTID,
         corpsecret=CORPSECRET,
         content=res)
