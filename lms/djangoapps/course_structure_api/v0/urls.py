"""
Courses Structure API v0 URI specification
"""
from django.conf import settings
from django.conf.urls import patterns, url, include

from course_structure_api.v0 import views


CONTENT_ID_PATTERN = settings.USAGE_ID_PATTERN.replace('usage_id', 'content_id')
COURSE_ID_PATTERN = settings.COURSE_ID_PATTERN

# pylint: disable=invalid-name
course_patterns = patterns(
    '',
    url(r'^$', views.CourseDetail.as_view(), name='detail'),
    url(r'^grading_policy/$', views.CourseGradingPolicy.as_view(), name='grading_policy'),
    url(r'^structure/$', views.CourseStructure.as_view(), name='structure'),
)

urlpatterns = patterns(
    '',
    url(r'^courses/$', views.CourseList.as_view(), name='list'),
    url(r'^courses/{}/'.format(COURSE_ID_PATTERN), include(course_patterns))
)
