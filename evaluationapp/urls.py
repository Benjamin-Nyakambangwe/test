from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.GradedOrganizationListView.as_view(),
         name="graded-organizations"),
    path('grade-manually/', views.grade_evaluation_manually, name='grade-manually'),
    path('list/', views.job_list, name='list'),

    path('graded-orgs-list/<int:pk>', views.GradedOrganizationDetailView.as_view(),
         name="graded-description-list"),
    path('upload-files/', views.upload_multiple_files, name='upload-files'),
    path('job-description-delete/<int:pk>/',
         views.JobDescriptionDeleteView.as_view(), name='delete-jd'),

    path('job-description/<int:pk>/', views.JobDescriptionDetailView.as_view(),
         name="job-description-detail"),

    path('job-description-update/<int:pk>/', views.JobDescriptionUpdateView.as_view(),
         name='job-description-update'),

    path('search-company', views.SearchResultsView.as_view(), name='search-company'),
    path('filter-job-descriptions', views.SearchJDResultsView.as_view(),
         name='filter-description'),

    path('file-upload/', views.download_word_doc, name='file-download'),




    #     path('api/descriptions', views.jobdecription_list,
    #          name='job-description-list'),
    #     path('api/job-description-detail/<str:pk>',
    #          views.jobdecription_detail, name='job-description-detail'),
    #     path('api/delete-job-description/<str:pk>',
    #          views.jobdecription_delete, name='job-description-delete'),

]
