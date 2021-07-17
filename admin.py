from django.contrib import admin
from .models import Membership, Course, Department, Lecturer, Student, StudentCourses, LecturerCourses,  Request, \
    ForwardedRequestsHod, ForwardedRequestsSenate, ForwardedRequestsCSIS, Notification
# Register your models here.

admin.site.register(Membership)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Lecturer)
admin.site.register(Student)
admin.site.register(StudentCourses)
admin.site.register(LecturerCourses)
admin.site.register(Request)
admin.site.register(ForwardedRequestsHod)
admin.site.register(ForwardedRequestsSenate)
admin.site.register(ForwardedRequestsCSIS)
admin.site.register(Notification)
