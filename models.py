from django.db import models
from django.contrib.auth.models import User
# Create your models here.


def get_first_name(self):
    return str(self.username) + " " + self.first_name + " " + self.last_name


User.add_to_class("__str__", get_first_name)


class Membership(models.Model):
    RoleType = models.TextChoices('RoleType', 'Student Lecturer HOD SENATE CSIS')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(blank=True, choices=RoleType.choices, max_length=10)

    def __str__(self):
        return str(self.user.username) + " " + str(self.user.last_name) + " " + str(self.user.first_name)


class Department(models.Model):
    BuildingName = models.TextChoices('BuildingName', 'CST CEDS CBSS COE')
    name = models.CharField(max_length=200)
    building = models.CharField(blank=True, choices=BuildingName.choices, max_length=10)

    def __str__(self):
        return str(self.name) + " (" + str(self.building) + ") "


class Student(models.Model):
    matriculation_number = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=200)
    program = models.CharField(max_length=200)
    LevelChoices = models.TextChoices('LevelChoices', '100 200 300 400')
    level = models.CharField(blank=True, choices=LevelChoices.choices, max_length=10)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.matriculation_number) + " " + str(self.program)


class Lecturer(models.Model):
    registration_number = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    RoleChoices = models.TextChoices('RoleChoices', 'HOD Lecturer')
    role = models.CharField(default='Lecturer', choices=RoleChoices.choices, max_length=10)

    def __str__(self):
        return str(self.registration_number) + " " + str(self.role) + " (" + str(self.department) + ")"


class Course(models.Model):
    course_code = models.CharField(max_length=10, primary_key=True)
    course_name = models.CharField(max_length=200)
    course_info = models.CharField(max_length=500, null=True)
    semester_session = models.CharField(max_length=15)
    LevelChoices = models.TextChoices('LevelChoices', '100 200 300 400')
    level = models.CharField(blank=True, choices=LevelChoices.choices, max_length=10)
    lecturers = models.ManyToManyField(User, related_name='courses')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.course_code) + " " + str(self.course_name)


class StudentCourses(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_taken = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.student_id) + " is taking " + str(self.course_taken)


class LecturerCourses(models.Model):
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    courses_teaching = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.lecturer) + " is teaching " + str(self.courses_teaching)


class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    created_by = models.DateTimeField(auto_now_add=True)
    requesting_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    request_text = models.CharField(max_length=500)
    supporting_documents = models.FileField(upload_to=None, max_length=254, blank=True)
    ca_score = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    responding_lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True)
    time_responded = models.DateTimeField(null=True)
    lecturer_response = models.CharField(max_length=500, null=True)
    StatusChoices = models.TextChoices('StatusChoices', 'un_concluded in-process concluded')
    status = models.CharField(default='un_concluded', max_length=30)
    status_time = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.request_id) + " " + str(self. requesting_student) + " " + str(self.course)


class ForwardedRequestsHod(models.Model):
    hod = models.ForeignKey(Lecturer, on_delete=models.CASCADE, null=True)
    request_id = models.OneToOneField(Request, on_delete=models.CASCADE, null=True, unique=True)
    time_forwarded = models.DateTimeField(auto_now_add=True)
    ResponseChoices = models.TextChoices('ResponseChoices', 'YetToBeApproved Approved')
    response = models.CharField(default='YetToBeApproved', choices=ResponseChoices.choices, max_length=30)
    time_responded = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.request_id) + " forwarded to " + str(self.hod)


class ForwardedRequestsSenate(models.Model):
    hod_forwarded_request = models.OneToOneField(ForwardedRequestsHod, on_delete=models.CASCADE, null=True, unique=True)
    time_forwarded = models.DateTimeField(auto_now_add=True)
    ResponseChoices = models.TextChoices('ResponseChoices', 'YetToBeApproved Approved')
    response = models.CharField(default='YetToBeApproved', choices=ResponseChoices.choices, max_length=30)
    time_responded = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.hod_forwarded_request)


class ForwardedRequestsCSIS(models.Model):
    senate_request = models.OneToOneField(ForwardedRequestsSenate, on_delete=models.CASCADE, null=True, unique=True)
    time_responded = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.senate_request)


class Notification(models.Model):
    receiving_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    request_concerned = models.ForeignKey(Request, on_delete=models.CASCADE, null=True)
    notification_text = models.CharField(max_length=100)
    notification_time = models.DateTimeField(null=True)
    student_seen = models.BooleanField(default=False)
