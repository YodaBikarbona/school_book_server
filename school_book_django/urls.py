"""school_book_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from school_book import views as school_book_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('school_book/users/', school_book_views.get_users),
    path('school_book/users/user/<int:user_id>', school_book_views.get_user_by_id),
    path('school_book/users/user/<int:user_id>/delete', school_book_views.delete_user),
    path('school_book/users/user/<int:user_id>/activate', school_book_views.activate_or_deactivate_user),
    path('school_book/users/user/<int:user_id>/deactivate', school_book_views.activate_or_deactivate_user),
    path('school_book/login', school_book_views.login_user),
    path('school_book/users/user/activate', school_book_views.activate_user),
    path('school_book/parent/children', school_book_views.get_children_by_parent_id),
    path('school_book/school_subjects', school_book_views.get_all_school_subjects),
    # path('school_book/child/<int:user_id>/school_subject/<int:school_subject_id>/grades',
    #      school_book_views.get_all_student_grades),
    path('school_book/school_class/<int:school_class_id>/child/<int:user_id>/school_subject/<int:school_subject_id>/grades',
         school_book_views.get_all_student_grades),
    path('school_book/parent/events', school_book_views.get_all_events_by_parent_id),
    path('school_book/school_class/<int:school_class_id>/child/<int:user_id>/school_subject/<int:school_subject_id>/isJustified/<str:is_justified>/absences',
         school_book_views.get_all_student_absences),
    path('school_book/school_class/<int:school_class_id>/child/<int:user_id>/school_subject/<int:school_subject_id>/absences',
         school_book_views.get_all_student_absences_number),
    path('school_book/admin/roles', school_book_views.get_all_roles),
    path('school_book/admin/roles/new', school_book_views.add_new_role),
    path('school_book/admin/roles/role/<int:role_id>/delete', school_book_views.delete_role),
    path('school_book/admin/genders', school_book_views.get_all_genders),
    path('school_book/admin/users/add', school_book_views.add_new_user),
    path('school_book/admin/users/user/<int:user_id>/edit', school_book_views.edit_user),
    path('school_book/admin/users/user/<int:user_id>/change_password', school_book_views.change_user_password),
    path('school_book/admin/roles/role/<int:role_id>/edit', school_book_views.edit_role),
    path('school_book/admin/school_subjects/add', school_book_views.add_school_subject),
    path('school_book/admin/school_subjects/school_subject/<int:school_subject_id>/delete',
         school_book_views.delete_school_subject),
    path('school_book/admin/school_subjects/school_subject/<int:school_subject_id>/edit',
         school_book_views.edit_school_subject),
    path('school_book/school_classes', school_book_views.get_all_school_classes),
    path('school_book/school_classes/<int:student_id>', school_book_views.get_all_school_classes_by_student_id),
    path('school_book/school_classes/school_class/<int:school_class_id>/members',
         school_book_views.get_school_class_members),
    path('school_book/admin/school_classes/school_class/<int:school_class_id>/delete',
         school_book_views.delete_school_class),
    path('school_book/admin/school_classes/add', school_book_views.add_school_class),
    path('school_book/admin/school_classes/school_class/<int:school_class_id>/edit',
         school_book_views.edit_school_class),
    path('school_book/admin/school_classes/school_class/members/add', school_book_views.add_school_class_member),
    path('school_book/admin/school_classes/school_class/members/member/<int:member_id>/activate_or_deactivate',
         school_book_views.activate_or_deactivate_school_class_member),
    path('school_book/admin/school_classes/school_class/role_name/<str:role_name>/members/member/<int:member_id>/delete',
         school_book_views.delete_school_class_member),
    path('school_book/school_classes/school_class/<int:school_class_id>/school_subjects',
         school_book_views.get_school_class_subjects),
    path('school_book/admin/school_class_subjects/school_class_subject/<int:school_class_subject_id>/delete',
         school_book_views.delete_school_class_subject),
    path('school_book/admin/school_class_subjects/school_class_subject/<int:school_class_subject_id>/activate_or_deactivate',
         school_book_views.activate_or_deactivate_school_class_subject),
    path('school_book/admin/school_class_subjects/school_class_subject/add',
         school_book_views.add_school_class_subject),
    path('school_book/professors/professor/school_classes',
         school_book_views.get_all_school_classes_by_professor_id),
    path('school_book/school_classes/<int:class_room_id>/information',
         school_book_views.get_all_school_room_information),
    path('school_book/school_classes/new_grade', school_book_views.add_new_grade),
    path('school_book/school_classes/absences/edit_absence', school_book_views.edit_absence),
    path('school_book/school_classes/absences/new_absence', school_book_views.add_absence),
    path('school_book/professor/events', school_book_views.get_all_events_by_professor_id),
    path('school_book/professor/events/event/<int:event_id>/delete', school_book_views.delete_event),
    path('school_book/professor/events/add', school_book_views.add_event)
]
