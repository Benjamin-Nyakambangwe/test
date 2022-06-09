import io
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import JobDescription, GradedOrganization
from django.views import generic
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .serializers import JobDescriptionSerializer
from .forms import JobDescriptionForm, UploadFileForm
from . import extract_docx, extract_pdf
from .generate_report import Report


@login_required
def dashboard(request):
    queryset = GradedOrganization.objects.annotate(
        number_of_jds=Count('jobdescription'))

    paginator = Paginator(queryset, 10)

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    return render(request, 'evaluationapp/index.html', {'queryset': queryset})


@login_required
def job_list(request):
    job_desc = JobDescription.objects.all().order_by('grade', 'job_title')
    last_job_desc = JobDescription.objects.all().last()
    return render(request, 'evaluationapp/description_list.html', {'job_desc': job_desc, 'last_job_added': last_job_desc})


@login_required
def grade_evaluation_manually(request):
    context = {}
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('list')
    else:
        form = JobDescriptionForm()
    context['form'] = form
    return render(request, 'evaluationapp/grade_manually.html', context)


@api_view(['GET'])
def jobdecription_list(request):
    job_descriptions = JobDescription.objects.all()
    serializer = JobDescriptionSerializer(job_descriptions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def jobdecription_detail(request, pk):
    job_description = JobDescription.objects.get(id=pk)
    serializer = JobDescriptionSerializer(job_description, many=False)
    return Response(serializer.data)


@api_view(['DELETE'])
def jobdecription_delete(request, pk):
    job_description = JobDescription.objects.get(id=pk)
    job_description.delete()
    return Response("Item Deleted Successfully")


@login_required
def upload_multiple_files(request):
    available_clients = GradedOrganization.objects.all()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        print(files)
        if form.is_valid():
            # check if there is either a client selected or intending to be created
            if request.POST.get('client-select') != 'none':
                client = request.POST.get('client-select')
                new_client = GradedOrganization.objects.get(
                    company_name=client)
            elif request.POST.get('add-client-input') != '':
                client = request.POST.get('add-client-input')
                print(client)
                GradedOrganization.objects.get_or_create(
                    company_name=client)
                new_client = GradedOrganization.objects.get(
                    company_name=client)

            else:
                messages.error(
                    request, 'Please select Client or add new one.')

                return render(request, 'evaluationapp/simple_upload.html', {'form': form, 'available_clients': available_clients})

            result = None

            dict_ = []
            for a_file in files:
                if word_or_pdf(a_file) == 'word':
                    try:
                        result = extract_docx.ExtractText(
                            a_file).process_files()
                    except Exception as e:
                        print(e)

                        # dict_.append(str(e))
                        dict_.append({'file': str(a_file), 'error': str(e)})
                        print(a_file)
                        print('Error while uploading file')
                        continue
                elif word_or_pdf(a_file) == 'pdf':
                    try:
                        result = extract_pdf.ExtractText(
                            a_file).process_files()
                    except Exception as e:
                        print(e)
                        continue
                else:
                    print("Not word or pdf document.")

                if result != None:
                    try:

                        if type(result) == dict:
                            JobDescription.objects.create(
                                company_name=new_client,
                                job_title=result["job_title"],
                                purpose=result["purpose"],
                                main_duties=result["main_duties"],
                                experience_in_years=result["experience"],
                                key_decisions=result["decisions_made"],
                                min_prof_qualifications=result["minimum_professional_qualification"],
                                academic_qualifications=result["academic_qualifications"],
                                planning_required=result["planning_required"],
                                technical_competence_required=result["technical_compentence"],
                            )
                        context = {'msg': 'success'}

                    except Exception as e:
                        context = {'msg': 'error'}
                        print(e)

            request.session['log'] = dict_
            return HttpResponseRedirect(reverse('graded-description-list', kwargs={'pk': new_client.id}))
        else:
            print(form.errors)
    else:
        form = UploadFileForm()
    return render(request, 'evaluationapp/simple_upload.html', {'form': form, 'available_clients': available_clients})


def word_or_pdf(filename):
    """Determines whether the given document is a word document, pdf or not

    Args:
        filename (_type_): Path to the file

    Returns:
        _str_: _String declaring whether the given document is pdf or word_
        _bool_: _Boolean showing the document is neither word nor pdf_

    """
    if str(filename).endswith('docx'):
        return 'word'
    elif str(filename).endswith('pdf'):
        return 'pdf'
    else:
        return False


class GradedOrganizationListView(LoginRequiredMixin, generic.ListView):
    """View that will generate the list of graded organizations
    """
    paginate_by = 10

    def get_queryset(self):
        """Will get the list of companies and their respective job descriptions
        """
        queryset = GradedOrganization.objects.annotate(
            number_of_jds=Count('jobdescription')).order_by('-id')
        return queryset


class GradedOrganizationDetailView(LoginRequiredMixin, generic.DetailView, generic.list.MultipleObjectMixin):
    """_View to display the graded description from a particular company
    """
    model = GradedOrganization
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = JobDescription.objects.filter(
            company_name=self.object)
        test = 'test'
        context = super().get_context_data(object_list=object_list, **kwargs)

        # context['job_descriptions'] = JobDescription.objects.filter(
        #     company_name=self.object)

        self.request.session['query_list'] = [
            [jd.job_title, jd.grade, jd.purpose] for jd in object_list]

        # self.request.session['query_list'] = [
        #     [jd.job_title, jd.grade, jd.purpose] for jd in context['job_descriptions']]

        self.request.session['comp_name'] = self.object.company_name

        context['log'] = self.request.session['log']

        return context


class JobDescriptionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = JobDescription
    success_url = reverse_lazy('graded-organizations')


class JobDescriptionDetailView(LoginRequiredMixin, generic.DetailView):
    model = JobDescription


class JobDescriptionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = JobDescription
    fields = ['job_title', 'grade', 'is_grade_correct', 'correct_grade']


class SearchResultsView(LoginRequiredMixin, generic.ListView):
    model = GradedOrganization
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('search')
        object_list = GradedOrganization.objects.filter(
            Q(company_name__icontains=query)
        )

        return object_list


class SearchJDResultsView(LoginRequiredMixin, generic.ListView):
    model = JobDescription
    template_name = 'evaluationapp/jd_search_results.html'

    def get_queryset(self):
        query = self.request.GET.getlist('filter-select')
        company_name = self.request.GET.get('company-hidden')
        from_date = self.request.GET.get('from-date')
        to_date = self.request.GET.get('to-date')

        # query = set([i.lower() for i in query])
        # print(query)

        if from_date and to_date and query:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")

            object_list = JobDescription.objects.filter(
                Q(job_title__in=query) & Q(
                    date_graded__range=[from_date, to_date]) & Q(company_name__company_name=company_name)
            )

        elif from_date and query:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            object_list = JobDescription.objects.filter(
                Q(job_title__in=query) & Q(date_graded__gte=from_date) & Q(
                    company_name__company_name=company_name)
            )

        elif from_date and to_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")

            object_list = JobDescription.objects.filter(
                Q(
                    date_graded__range=[from_date, to_date]) & Q(company_name__company_name=company_name)
            )

        else:
            object_list = JobDescription.objects.filter(
                Q(job_title__in=query) & Q(
                    company_name__company_name=company_name)
            )

        self.request.session['query_list'] = [
            [jd.job_title, jd.grade, jd.purpose] for jd in object_list]

        self.request.session['comp_name'] = company_name

        return object_list


def download_word_doc(request):
    buffer = io.BytesIO()
    document = Report(
        request.session['comp_name'], request.session['query_list']).generate_report()

    document.save(buffer)  # save your memory stream
    buffer.seek(0)  # rewind the stream

    # put them to streaming content response
    # within docx content_type
    response = StreamingHttpResponse(
        streaming_content=buffer,  # use the stream's content
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

    response['Content-Disposition'] = f"attachment;filename={request.session['comp_name']} job description results.docx"
    response["Content-Encoding"] = 'UTF-8'

    return response
