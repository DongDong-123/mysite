import time
from django.core.cache import cache
import redis
from django.utils.deprecation import MiddlewareMixin
from collections import Counter
from django.http import HttpResponseForbidden
from timeit import timeit
from django.conf import settings


class StatFlowMiddleware(object):
    """ 流量统计 """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_meta = request.META
        response = self.get_response(request)
        # print('流量统计')

        if request_meta.get("HTTP_X_FORWARDED_FOR"):
            HTTP_X_FORWARDED_FOR_ip = request_meta["HTTP_X_FORWARDED_FOR"]
        else:
            HTTP_X_FORWARDED_FOR_ip = False

        if request_meta.get('REMOTE_ADDR'):
            REMOTE_ADDR_ip = request_meta.get('REMOTE_ADDR')
        else:
            REMOTE_ADDR_ip = False

        # print(request_meta,type(request_meta))
        if request_meta.get('HTTP_VIA'):
            HTTP_VIA = request_meta.get('HTTP_VIA')
        else:
            HTTP_VIA = False

        if request_meta.get('HTTP_REFERER'):
            HTTP_REFERER = request_meta['HTTP_REFERER']
            if len(HTTP_REFERER)>1000:
                HTTP_REFERER = HTTP_REFERER[:1000]
        else:
            HTTP_REFERER = False

        if request_meta.get('PATH_INFO'):
            PATH_INFO = request_meta['PATH_INFO']
        else:
            PATH_INFO = False
        if request_meta.get('HTTP_USER_AGENT'):
            HTTP_USER_AGENT = request_meta['HTTP_USER_AGENT']
        else:
            HTTP_USER_AGENT = False

        if request_meta.get('REQUEST_METHOD'):
            REQUEST_METHOD = request_meta['REQUEST_METHOD']
        else:
            REQUEST_METHOD = False

        if request_meta.get('HTTP_CONNECTION'):
            HTTP_CONNECTION = request_meta['HTTP_CONNECTION']
        else:
            HTTP_CONNECTION = False

        info_list = {
            'IP1': REMOTE_ADDR_ip,
            'IP2': HTTP_VIA,
            'IP3': HTTP_X_FORWARDED_FOR_ip,
            'Begin_path': HTTP_REFERER,
            'End_path': PATH_INFO,
            'User_agent': HTTP_USER_AGENT,
            'Request_method': REQUEST_METHOD,
            'Connection': HTTP_CONNECTION,
            'Response_code': response.status_code,
            'Visit_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        num = self.save_to_redis(info_list)
        request_meta.update({'visit_num': num})
        # visit_num = cache.get_or_set('visit_num', num)
        if request_meta.get('visit_num'):
            pass
            # print('添加成功')
        else:
            print('添加失败')

        return response

    def save_to_redis(self, result):
        """
        保存至Redis数据库
        :paramresult:数据字典
        :return:
        """
        num = 1
        try:
            conn = redis.Redis(connection_pool=settings.POOL)
            if conn.get('number'):
                num = int(conn.get('number'))

        except ConnectionError as e:
            print(e, '连接redis数据库失败')
        try:
            conn.hmset('visit_info{}'.format(num), result)
            num += 1
            conn.set('number', num)
            # print('成功存入redis数据库')
        except Exception as e:
            print(e, '储存redis数据库失败')

        return num


class FilterUserAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_meta = request.META
        user_agent = request_meta.get('HTTP_USER_AGENT')
        # print(user_agent)
        if not user_agent:
            return HttpResponseForbidden('非法访问')
        import re
        patt = re.compile('python', re.I)
        craweler = patt.search(user_agent)
        if craweler:
            return HttpResponseForbidden('非法访问')



# MAX_REQUEST_PER_SECOND=2 #每秒访问次数
#
# class RequestBlockingMiddleware(MiddlewareMixin):
#
#     def process_request(self,request):
#         # now=time.time()
#         request_queue = request.session.get('request_queue',[])
#         print('----------')
#         request_queue.append(request.META.get('REMOTE_ADDR'))
#         print(request_queue)
#         now = str(time.time())
#         print(request.session,type(request.session))
#         request.session['time'] = now
#         # for i in request.session:
#         #     print(i)
#
#         print(now,type(now))
#
#         take_time = time.time() - float(request.session.get('time'))
#         print(take_time)
#
#         if take_time >60:
#             rote = self.process_ip(request_queue)
#             if rote:
#                 now = time.time()
#                 return HttpResponseForbidden('<h1 style="text-align:center;margin-top:20px;">不好意思，</h1>')
#                 # 禁止访问
#
#
#         request.session['request_queue']=request_queue[1:]
#
#     def process_ip(self,ip_list):
#         # 统计ip次数
#         ip_num = Counter(ip_list)
#         more_ip = []
#         # 筛选大于20的ip
#         for elem in ip_num:
#             if ip_num[elem] > 5:
#                 more_ip.append(elem)
#
#         return more_ip



