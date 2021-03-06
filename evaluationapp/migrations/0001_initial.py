# Generated by Django 4.0.2 on 2022-04-11 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GradedOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=200)),
                ('purpose', models.CharField(max_length=12000)),
                ('main_duties', models.CharField(max_length=12000)),
                ('planning_required', models.CharField(max_length=10000)),
                ('min_prof_qualifications', models.CharField(max_length=12000)),
                ('technical_competence_required', models.CharField(max_length=6000)),
                ('key_decisions', models.CharField(max_length=10000)),
                ('academic_qualifications', models.CharField(choices=[('None', 'None'), ('National diploma', 'National diploma'), ('Certificate', 'Certificate'), ('O level', 'O level'), ("Bachelor's degree", "Bachelor's degree"), ('A level', 'A level'), ('Training/Experience', 'Training/Experience'), ("Master's degree", "Master's degree")], max_length=20)),
                ('experience_in_years', models.IntegerField()),
                ('grade', models.CharField(blank=True, max_length=5, null=True)),
                ('is_grade_correct', models.BooleanField(default=False)),
                ('correct_grade', models.CharField(blank=True, max_length=5, null=True)),
                ('date_graded', models.DateField()),
                ('company_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluationapp.gradedorganization')),
            ],
        ),
    ]
