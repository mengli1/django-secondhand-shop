from django.core.paginator import Paginator
from django.shortcuts import render
#公共分页函数
def public_page(data,page,number):
    # 分页
    paginator = Paginator(data, number)
    try:
        page = int(page)
    except Exception as e:
        page = 1
    if page > paginator.num_pages:
        page = 1
    # 获取第page页的Page实例对象
    data_page = paginator.page(page)
    # todo: 进行页码的控制，页面上最多显示5个页码
    # 1.总页数小于5页，页面上显示所有页码
    # 2.如果当前页是前3页，显示1-5页
    # 3.如果当前页是后3页，显示后5页
    # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
    num_pages = paginator.num_pages
    if num_pages < 5:
        pages = range(1, num_pages + 1)
    elif page <= 3:
        pages = range(1, 6)
    elif num_pages - page <= 2:
        pages = range(num_pages - 4, num_pages + 1)
    else:
        pages = range(page - 2, page + 3)
    context = {
        'data_page': data_page,
        'pages': pages,
        'length': len(data_page)
    }
    return context

# 用户匹配
def public_user_match(id,data,request):
    '''匹配用户'''
    if not id:
        return render(request, 'skippage.html', {'msg': '违法操作！'})
    if not data:
        return render(request, 'skippage.html', {'msg': '数据已经删除，无需重复操作！'})
    if data.user.id != request.user.id:
        return render(request, 'skippage.html', {'msg': '违法操作！'})