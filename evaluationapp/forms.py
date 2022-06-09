from django import forms
from .models import JobDescription


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


class JobDescriptionForm(forms.ModelForm):
    job_title = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Job Title'}), label='')
    purpose = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Enter Purpose'}), label='')
    main_duties = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Enter Main Duties'}), label='')
    planning_required = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Enter Planning Required'}), label='')
    min_prof_qualifications = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Minimum Professional Qualifications'}), label='')
    technical_competence_required = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Enter Technical Competence Required'}), label='')
    key_decisions = forms.CharField(required=True, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Enter Key Decisions'}), label='')
    academic_qualifications = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'form-select form-control', 'placeholder': 'Enter Academic Qualifications'}), label='', choices=ACADEMIC_QUALIFICATIONS)
    experience_in_years = forms.IntegerField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Experience In Years'}), label='')
    grade = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter Grade'}), label='')

    class Meta:
        model = JobDescription
        exclude = ('grade', 'company_name')


class UploadFileForm(forms.Form):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}))
