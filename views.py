from django.shortcuts import render, redirect, HttpResponseRedirect, reverse, HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from .models import Membership, Request, StudentCourses, Student, Course, LecturerCourses, Lecturer, Department, \
    ForwardedRequestsHod, ForwardedRequestsSenate, ForwardedRequestsCSIS, Notification



# Create your views here.


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['idno'], password=request.POST['password'])
        if user is not None and Membership.objects.filter(user=user, role='Student'):
            auth.login(request, user)
            return redirect('studentdashboard')
        elif user is not None and Membership.objects.filter(user=user, role='Lecturer'):
            auth.login(request, user)
            return redirect('lecturerdashboard')
        elif user is not None and Membership.objects.filter(user=user, role='HOD'):
            auth.login(request, user)
            return redirect('hoddashboard')
        elif user is not None and Membership.objects.filter(user=user, role='SENATE'):
            auth.login(request, user)
            return redirect('senatedashboard')
        elif user is not None and Membership.objects.filter(user=user, role='CSIS'):
            auth.login(request, user)
            return redirect('csisdashboard')
        else:
            return render(request, 'RevalidationSystem/login.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'RevalidationSystem/login.html')


@login_required(login_url='login')
def student_dashboard(request):
    user = Membership.objects.get(user=request.user)
    student_name = Student.objects.get(matriculation_number=user)
    courses_list = StudentCourses.objects.filter(student_id=student_name)
    request_list = Request.objects.filter(requesting_student=student_name)
    student_notifications = Notification.objects.filter(receiving_student=student_name)
    if request.method == "POST":

        course = request.POST.get('course_dropdown')
        course_picked = Course.objects.get(course_code=course)
        text = request.POST.get('request-reason')
        docs = request.POST.get('supporting-docs')
        score = request.POST.get('test-score')

        revalidation_request = Request(requesting_student=student_name, course=course_picked, request_text=text,
                                       supporting_documents=docs, ca_score=score)
        revalidation_request.save()
        return HttpResponseRedirect(reverse('studentdashboard'))
        messages.success(request, "Your request has been sent!")
    else:
        return render(request, 'RevalidationSystem/studentdash.html', context={'username': user, 'courses': courses_list,
                                                                           'request_records': request_list,
                                                                           'notifications': student_notifications,
                                                                           # 'seected':request_selection
                                                                          })


@login_required(login_url='login')
def lecturer_dashboard(request):
    user = Membership.objects.get(user=request.user)
    lecturer_name = Lecturer.objects.get(registration_number=user)
    courses_taught = Course.objects.filter(lecturers=request.user)
    num_dict = {}
    request_groups = {}
    for x in courses_taught:
        course_request = Request.objects.filter(course=Course.objects.get(course_code=x.course_code))
        not_concluded = Request.objects.filter(course=Course.objects.get(course_code=x.course_code), status='un_concluded')
        not_concluded_num = Request.objects.filter(course=Course.objects.get(course_code=x.course_code),
                                               status="un_concluded").count()
        in_process = Request.objects.filter(course=Course.objects.get(course_code=x.course_code),
                                               status="in-process")
        concluded = Request.objects.filter(course=Course.objects.get(course_code=x.course_code),
                                               status="concluded")
        request_groups["un-concluded"] = not_concluded
        request_groups["in-process"] = in_process
        request_groups["concluded"] = concluded
        num_dict[x.course_code] = not_concluded_num

    print(request_groups)
    return render(request, 'RevalidationSystem/lecturerdash.html', context={'username': user,
                                                                            'courses_taught': courses_taught,
                                                                            "request_groups": request_groups,
                                                                            "course_requests": course_request,
                                                                            'num_dict':num_dict})
@login_required(login_url='login')
def hod_dashboard(request):
    user = Lecturer.objects.get(registration_number=Membership.objects.get(user=request.user))
    forwarded_requests = ForwardedRequestsHod.objects.filter(hod=user)
    request_groups = {}

    yet_to_be_approved = ForwardedRequestsHod.objects.filter(response='YetToBeApproved')
    yet_to_be_approved_num = ForwardedRequestsHod.objects.filter(response='YetToBeApproved').count()
    approved = ForwardedRequestsHod.objects.filter(response='Approved')

    request_groups["YetToBeApproved"] = yet_to_be_approved
    request_groups["Approved"] = approved
    print(request_groups)
    return render(request, 'RevalidationSystem/hoddash.html', context={'username': user,
                                                                       'requests': forwarded_requests,
                                                                       'request_groups': request_groups,
                                                                       'request_num': yet_to_be_approved_num
                                                                      })


@login_required(login_url='login')
def csis_dashboard(request):
    user = Membership.objects.get(user=request.user)
    forwarded_requests = ForwardedRequestsCSIS.objects.all()
    return render(request, 'RevalidationSystem/csisdash.html', context={'username': user,
                                                                        'requests': forwarded_requests})


@login_required(login_url='login')
def senate_dashboard(request):
    user = Membership.objects.get(user=request.user)
    forwarded_requests = ForwardedRequestsSenate.objects.all()

    return render(request, 'RevalidationSystem/senatedash.html', context={'username': user,
                                                                          'requests': forwarded_requests
                                                                          })


def json(request):
    if request.method == "POST":
        request_data = Request.objects.filter(request_id=request.POST['request_id'])
        request_ser_model = serializers.serialize("json", request_data)

    return JsonResponse(request_ser_model, safe=False)


def json_lecturer(request):
    if request.method == "POST":

        course_requests = Request.objects.filter(course=Course.objects.get(course_code=request.POST['course_code']))
        num = 0
        course_requests_ser_model = {'num':num}
        for foo in course_requests:
            course_dataDB = {'id': foo.request_id, 'course': foo.course.course_code, 'date': foo.created_by.strftime("%b %d %Y"),
                              'user': foo.requesting_student.matriculation_number.user.username}
            course_requests_ser_model[num]=course_dataDB
            num = num + 1
        course_requests_ser_model ['num'] = num

    return JsonResponse(course_requests_ser_model,safe=False)


def lecturer_single(request):
    if request.method == "POST":
        request_data = Request.objects.filter(request_id=request.POST['request_id'])
        num = 0
        requests_ser_model = {'num': num}
        for foo in request_data:
            course_dataDB = {'id': foo.request_id, 'course': foo.course.course_code,
                             'date_sent': foo.created_by.strftime("%d/%m/%Y, %H:%M"),
                             'user_matric_number': foo.requesting_student.matriculation_number.user.username,
                             'user_fullname': foo.requesting_student.full_name,
                             'request_text': foo.request_text,
                             'lecturer_response': foo.lecturer_response,
                             'lecturer_response_time':foo.time_responded,
                             'status': foo.status,
                             'status_time': foo.status_time,
                             'ca': foo.ca_score}
            requests_ser_model[num] = course_dataDB
            num = num + 1
        requests_ser_model['num'] = num

    return JsonResponse(requests_ser_model, safe=False)


def lecturer_message(request):
    user = Membership.objects.get(user=request.user)
    lecturer_name = Lecturer.objects.get(registration_number=user)
    request_data = Request.objects.filter(request_id=request.POST['request_id'])
    request_ser_model = serializers.serialize("json", request_data)
    lect_msg = request.POST['lecturer_response']
    if request.method == 'POST':

        request_data.update(lecturer_response=lect_msg)
        request_data.update(responding_lecturer=lecturer_name)
        request_data.update(time_responded=timezone.now())

    notification = 'You have a message from ' + str(request_data[0].course.course_code)
    Notification.objects.create(receiving_student=request_data[0].requesting_student, notification_text=notification,
                                notification_time=timezone.now())

        # You have a message from Request.course  -- 23:43 PM
    return JsonResponse(request_ser_model, safe=False)

def hod_json(request):

    if request.method == "POST":
        request_data = Request.objects.filter(request_id=request.POST['request_id'])
        num = 0
        requests_ser_model = {'num': num}
        for foo in request_data:
            course_dataDB = {'id': foo.request_id, 'course': foo.course.course_code,
                             'date_sent': foo.created_by.strftime("%d/%m/%Y, %H:%M"),
                             'user_matric_number': foo.requesting_student.matriculation_number.user.username,
                             'user_fullname': foo.requesting_student.full_name,
                             'request_text': foo.request_text,
                             'lecturer_response': foo.lecturer_response,
                             'lecturer_response_time':foo.time_responded.strftime("%d/%m/%Y, %H:%M"),
                             'status': foo.status,
                             'status_time': foo.status_time,
                             'ca': foo.ca_score}
            requests_ser_model[num] = course_dataDB
            num = num + 1
        requests_ser_model['num'] = num

    return JsonResponse(requests_ser_model, safe=False)


def forward_HOD(request):
    user = Membership.objects.get(user=request.user)
    user_dept = Lecturer.objects.get(registration_number=user).department
    user_hod = Lecturer.objects.get(role='HOD', department=user_dept)
    request_forwarded = Request.objects.get(request_id=request.POST['request_id'])

    new_fwrd_req = ForwardedRequestsHod.objects.create(hod=user_hod, request_id=request_forwarded, time_forwarded=timezone.now())
    new_fwrd_req.save()

    request_forwarded = Request.objects.filter(request_id=request.POST['request_id'])

    request_forwarded.update(status_time=timezone.now())
    request_forwarded.update(status="in_process")

    notification = 'Your ' + str(request_forwarded[0].course.course_code) + ' request has been forwarded to your HOD'
    Notification.objects.create(receiving_student=request_forwarded[0].requesting_student, notification_text=notification,
                                notification_time=timezone.now())
    # Your request.course request has been forwarded to your HOD

    fwrd_requests = ForwardedRequestsHod.objects.all()
    request_ser_model = serializers.serialize("json", fwrd_requests)


    return JsonResponse(request_ser_model, safe=False)


def forward_SENATE(request):
    user = Membership.objects.get(user=request.user)
    #user_hod = Lecturer.objects.get(registration_number=user)

    request_forwarded = ForwardedRequestsHod.objects.get(request_id=request.POST['request_id'])

    new_fwrd_req = ForwardedRequestsSenate.objects.create(hod_forwarded_request=request_forwarded,
                                                       time_forwarded=request_forwarded.time_responded)
    new_fwrd_req.save()

    request_forwarded = Request.objects.filter(request_id=request.POST['request_id'])

    request_forwarded.update(status="in-process")

    notification = 'Your ' + str(request_forwarded.request_id.course.course_code) + ' request has been approved and forwarded to SENATE'
    Notification.objects.create(receiving_student=request_forwarded.request_id.requesting_student, notification_text=notification,
                                notification_time=timezone.now())
    # Your request.course request has been approved and forwarded to SENATE

    fwrd_requests = ForwardedRequestsSenate.objects.all()
    request_ser_model = serializers.serialize("json", fwrd_requests)

    return JsonResponse(request_ser_model, safe=False)


def senate_json(request):

    if request.method == "POST":
        request_data = Request.objects.filter(request_id=request.POST['request_id'])
        num = 0
        requests_ser_model = {'num': num}
        for foo in request_data:
            course_dataDB = {'id': foo.request_id, 'course': foo.course.course_code,
                             'date': foo.created_by.strftime("%b %d %Y"),
                             'user_matric_number': foo.requesting_student.matriculation_number.user.username,
                             'user_fullname': foo.requesting_student.full_name,
                             'request_text': foo.request_text,
                             'lecturer_response': foo.lecturer_response,
                             'ca': foo.ca_score}
            requests_ser_model[num] = course_dataDB
            num = num + 1
        requests_ser_model['num'] = num

    return JsonResponse(requests_ser_model, safe=False)


def forward_CSIS(request):
    user = Membership.objects.get(user=request.user)
    # user_hod = Lecturer.objects.get(registration_number=user)

    hod_request_forwarded = ForwardedRequestsHod.objects.get(request_id=request.POST['request_id'])
    senate_request_forwarded = ForwardedRequestsSenate.objects.get(hod_forwarded_request=hod_request_forwarded)

    new_fwrd_req = ForwardedRequestsCSIS.objects.create(senate_request=senate_request_forwarded)
    new_fwrd_req.save()

    request_forwarded = Request.objects.filter(request_id=hod_request_forwarded.request_id.request_id)

    request_forwarded.update(status="in-process")
    # Your request.course request has been approved and forwarded to CSIS to effect changes

    notification = 'Your ' + str(hod_request_forwarded.request_id.course.course_code) + ' request has been approved and forwarded to SENATE'
    Notification.objects.create(receiving_student=hod_request_forwarded.request_id.requesting_student, notification_text=notification,
                                notification_time=timezone.now())

    fwrd_requests = ForwardedRequestsCSIS.objects.all()
    request_ser_model = serializers.serialize("json", fwrd_requests)

    return JsonResponse(request_ser_model, safe=False)


def markasC(request):
    if request.method == "POST":
        request_forwarded = Request.objects.get(request_id=request.POST['request_id'])
        request_forwarded = Request.objects.filter(request_id=request.POST['request_id'])
        # print(request_forwarded)
        request_forwarded.update(status="concluded")
        request_forwarded.update(status_time=timezone.now())
        request_ser_model = serializers.serialize("json", request_forwarded)

    return JsonResponse(request_ser_model, safe=False)

def csis_json(request):
    if request.method == "POST":
        request_data = Request.objects.filter(request_id=request.POST['request_id'])
        num = 0
        requests_ser_model = {'num': num}
        for foo in request_data:
            course_dataDB = {'id': foo.request_id, 'course': foo.course.course_code,
                             'date': foo.created_by.strftime("%b %d %Y"),
                             'user_matric_number': foo.requesting_student.matriculation_number.user.username,
                             'user_fullname': foo.requesting_student.full_name,
                             'request_text': foo.request_text,
                             'lecturer_response': foo.lecturer_response,
                             'ca': foo.ca_score}
            requests_ser_model[num] = course_dataDB
            num = num + 1
        requests_ser_model['num'] = num

    return JsonResponse(requests_ser_model, safe=False)


def logout(request):
    django_logout(request)
    return redirect('login')