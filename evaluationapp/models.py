from django.db import models
from .grade_data import start_grade
from django.urls import reverse
from datetime import date

# Create your models here.

# Constant for academic qualifications
ACADEMIC_QUALIFICATIONS = (
    ("None", "None"),
    ("National diploma", "National diploma"),
    ("Certificate", "Certificate"),
    ("O level", "O level"),
    ("Bachelor's degree", "Bachelor's degree"),
    ("A level", "A level"),
    ("Training/Experience", "Training/Experience"),
    ("Master's degree", "Master's degree")
)


class GradedOrganization(models.Model):
    """_Model containing data on the company being graded_
    """
    company_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.company_name


class JobDescription(models.Model):
    """Job description model
    """
    company_name = models.ForeignKey(
        GradedOrganization, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    purpose = models.CharField(max_length=12000)
    main_duties = models.CharField(max_length=12000)
    planning_required = models.CharField(max_length=10000)
    min_prof_qualifications = models.CharField(max_length=12000)
    technical_competence_required = models.CharField(max_length=6000)
    key_decisions = models.CharField(max_length=10000)
    academic_qualifications = models.CharField(
        max_length=20, choices=ACADEMIC_QUALIFICATIONS)
    experience_in_years = models.FloatField()
    grade = models.CharField(max_length=5, null=True, blank=True)
    is_grade_correct = models.BooleanField(default=False)
    correct_grade = models.CharField(max_length=5, null=True, blank=True)
    date_graded = models.DateField()

    def __str__(self):
        return self.job_title

    def save(self, *args, **kwargs):
        """method that grades the job description before saving the information to the database
        """
        self.grade = start_grade(self.purpose, self.main_duties, self.planning_required, self.min_prof_qualifications,
                                 self.technical_competence_required, self.key_decisions, self.academic_qualifications, self.experience_in_years)
        if self.is_grade_correct == True:
            self.correct_grade = self.grade

        self.date_graded = date.today()
        super(JobDescription, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("job-description-detail", kwargs={"pk": self.pk})
