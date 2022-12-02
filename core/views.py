from uuid import UUID
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied

from django.views.generic import ListView
from core.models import Analysis, RiskScenario, SecurityMeasure, RiskMatrix
from back_office.models import Project
from iam.models import Folder, RoleAssignment, User

from django.contrib.auth.views import LoginView
from .forms import LoginForm

from django.db.models import Q

from django.utils.translation import gettext_lazy as _

from .helpers import *

from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import logging
import csv


class AnalysisListView(ListView):
    template_name = 'core/index.html'
    context_object_name = 'context'

    ordering = 'id'
    paginate_by = 10
    model = Analysis

    def get_queryset(self):
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
        qs = self.model.objects.filter(id__in=object_ids_view).order_by(self.ordering)
        return qs


class UserLogin(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm


@method_decorator(login_required, name='dispatch')
class SecurityMeasurePlanView(UserPassesTestMixin, ListView):
    template_name = 'core/mp.html'
    context_object_name = 'context'

    ordering = 'id'
    model = RiskScenario

    def get_queryset(self):
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, RiskScenario)
        qs = self.model.objects.filter(id__in=object_ids_view).order_by(self.ordering)
        return qs
    
    def test_func(self):
        return RoleAssignment.is_access_allowed(user=self.request.user, perm=Permission.objects.get(codename="view_securitymeasure"), folder=get_object_or_404(Project, id=self.kwargs['project']).folder)


def build_ri_clusters(analysis: Analysis):
    matrix = analysis.rating_matrix.parse_json()
    grid = matrix['grid']
    matrix_current = [[set() for _ in range(len(grid[0]))] for _ in range(len(grid))]
    matrix_residual = [[set() for _ in range(len(grid[0]))] for _ in range(len(grid))]

    for ri in RiskScenario.objects.filter(analysis=analysis).order_by('created_at'):
        if ri.current_level >= 0:
            matrix_current[ri.current_proba][ri.current_impact].add(ri.rid)
        if ri.residual_level >=0:
            matrix_residual[ri.residual_proba][ri.residual_impact].add(ri.rid)

    return {'current': matrix_current, 'residual': matrix_residual}


@method_decorator(login_required, name='dispatch')
class RiskAnalysisView(UserPassesTestMixin, ListView):
    template_name = 'core/ra.html'
    context_object_name = 'context'

    model = RiskScenario
    ordering = 'created_at'

    def get_queryset(self):
        self.analysis = get_object_or_404(Analysis, id=self.kwargs['analysis'])
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, RiskScenario)
        qs = self.model.objects.filter(id__in=object_ids_view).filter(analysis=self.analysis).order_by(self.ordering)
        return qs 

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # then Add in
        context['analysis'] = self.analysis
        context['ri_clusters'] = build_ri_clusters(self.analysis)
        context['matrix'] = self.analysis.rating_matrix
        (context['object_ids_view'], context['object_ids_change'], context['object_ids_delete']) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
        return context
    
    def test_func(self):
        return RoleAssignment.is_access_allowed(user=self.request.user, perm=Permission.objects.get(codename="view_analysis"), folder= get_object_or_404(Analysis, id=self.kwargs['analysis']).project.folder)

@login_required
def generate_ra_pdf(request, analysis: Analysis): # analysis parameter is the id of the choosen Analysis
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, Analysis)
    if UUID(analysis) in object_ids_view:
        ra = get_object_or_404(Analysis, pk=analysis)
        context = RiskScenario.objects.filter(analysis=analysis).order_by('id')
        data = {'context': context, 'analysis': ra, 'ri_clusters': build_ri_clusters(ra), 'matrix': ra.rating_matrix}
        html = render_to_string('core/ra_pdf.html', data)
        pdf_file = HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="RA-{ra.id}-{ra.project}-v-{ra.version}.pdf"'
        return response
    else:
        raise PermissionDenied()


@login_required
def generate_mp_pdf(request, analysis): # analysis parameter is the id of the choosen Analysis
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, Analysis)
    if UUID(analysis) in object_ids_view:
        ra = get_object_or_404(Analysis, pk=analysis)
        context = RiskScenario.objects.filter(analysis=analysis).order_by('id')
        data = {'context': context, 'analysis': ra}
        html = render_to_string('core/mp_pdf.html', data)
        pdf_file = HTML(string=html).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="MP-{ra.id}-{ra.project}-v-{ra.version}.pdf"'
        return response
    else:
        raise PermissionDenied()


@method_decorator(login_required, name='dispatch')
class SearchResults(ListView):
    context_object_name = 'context'
    template_name = 'core/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, RiskScenario)
        ri_list = RiskScenario.objects.filter(Q(name__icontains=query) | Q(threat__name__icontains=query)).filter(id__in=object_ids_view)[:10]
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, SecurityMeasure)
        mtg_list = SecurityMeasure.objects.filter(Q(name__icontains=query) | Q(security_function__name__icontains=query)).filter(id__in=object_ids_view)[:10]
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
        ra_list = Analysis.objects.filter(Q(project__name__icontains=query)).filter(id__in=object_ids_view)[:10]
        return {"Analysis": ra_list, "RiskScenario": ri_list, "SecurityMeasure": mtg_list}


@method_decorator(login_required, name='dispatch')
class Browser(ListView):
    context_object_name = 'context'
    template_name = 'core/browser.html'

    map_rsk = {'0': "open", '1': "mitigated", '2': "accepted", '3': "blocker", '4': "transferred"}
    map_mtg = {'0': "open", '1': "in_progress", '2': "on_hold", '3': "done"}

    def get_queryset(self):

        rsk = self.request.GET.get('rsk')
        mtg = self.request.GET.get('mtg')
        if rsk:
            (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, RiskScenario)
            return {"type": "Risk scenarios", "filter": self.map_rsk[rsk], "items": RiskScenario.objects.filter(treatment=self.map_rsk[rsk]).filter(id__in=object_ids_view)}
        if mtg:
            (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, SecurityMeasure)
            return {"type": "SecurityMeasures", "filter": self.map_mtg[mtg], "items": SecurityMeasure.objects.filter(status=self.map_mtg[mtg]).filter(id__in=object_ids_view)}



@login_required
def global_analytics(request):
    template = 'core/analytics.html'

    context = {
        "break_by_p_risks": p_risks(request.user),
        "rose": p_risks_2(request.user),
        "risks_level": risks_count_per_level(request.user),
        "risk_colors": list(get_risk_color_map(request.user).values()),
        "risk_status": risk_per_status(request.user),
        "security_measure_status": security_measure_per_status(request.user),
        "security_measure_per_cur_risk": security_measure_per_cur_risk(request.user),
        "security_measure_per_security_function": security_measure_per_security_function(request.user),
        "security_measure_priority": security_measure_priority(request.user),
        "risk_matrix": risk_matrix(request.user),
        "risks_per_project_groups": risks_per_project_groups(request.user),
        "extra": risks_levels_per_prj_grp(request.user),
        "counters": get_counters(request.user),
    }

    return render(request, template, context)


@method_decorator(login_required, name='dispatch')
class MyProjectsListView(ListView):
    template_name = 'core/my_projects.html'
    context_object_name = 'context'
    model = SecurityMeasure

    def get_queryset(self):
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
        agg_data = risk_status(self.request.user, Analysis.objects.filter(id__in=object_ids_view).filter(auditor=self.request.user))
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, SecurityMeasure)
        _tmp = SecurityMeasure.objects.filter(id__in=object_ids_view).filter(riskscenario__analysis__auditor=self.request.user).exclude(status='done').order_by('eta')
        ord_security_measures = sorted(_tmp, key=lambda mtg: mtg.get_ranking_score(), reverse=True)
        # TODO: add date sorting as well
        return {'agg_data': agg_data,
                'security_measures': ord_security_measures}
        # for UI debug use:
        # return risk_status(Analysis.objects.all())


def compile_analysis_for_composer(user: User, analysis_list: list):
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), user, Analysis)
    analysis_objects = Analysis.objects.filter(id__in=object_ids_view).filter(id__in=analysis_list)

    current_level = list()
    residual_level = list()
    agg_risks = list()

    for lvl in get_rating_options(user):
        count_c = RiskScenario.objects.filter(current_level=lvl[0]).filter(analysis__in=analysis_list).count()
        count_r = RiskScenario.objects.filter(residual_level=lvl[0]).filter(analysis__in=analysis_list).count()
        current_level.append({'name': lvl[1], 'value': count_c})
        residual_level.append({'name': lvl[1], 'value': count_r})

    untreated = RiskScenario.objects.filter(analysis__in=analysis_list).exclude(
        treatment__in=['mitigated', 'accepted']).count()
    untreated_h_vh = RiskScenario.objects.filter(analysis__in=analysis_list).exclude(
        treatment__in=['mitigated', 'accepted']).filter(current_level__gte=2).count()
    accepted = RiskScenario.objects.filter(analysis__in=analysis_list).filter(treatment='accepted').count()

    values = list()
    labels = list()
    color_map = {"open": "#fac858", "in_progress": "#5470c6", "on_hold": "#ee6666", "done": "#91cc75"}
    for st in SecurityMeasure.MITIGATION_STATUS:
        count = SecurityMeasure.objects.filter(status=st[0]).filter(riskscenario__analysis__in=analysis_list).count()
        v = {
            "value": count,
            "itemStyle": {"color": color_map[st[0]]}
        }
        values.append(v)
        labels.append(st[1])

    analysis_objects = list()

    for _ra in analysis_list:
        synth_table = list()
        for lvl in get_rating_options(user):
            count_c = RiskScenario.objects.filter(current_level=lvl[0]).filter(analysis__id=_ra).count()
            count_r = RiskScenario.objects.filter(residual_level=lvl[0]).filter(analysis__id=_ra).count()
            synth_table.append({"lvl": lvl[1], "current": count_c, "residual": count_r})
        hvh_risks = RiskScenario.objects.filter(analysis__id=_ra).filter(current_level__gte=2)
        analysis_objects.append(
            {"analysis": get_object_or_404(Analysis, pk=_ra), "synth_table": synth_table, "hvh_risks": hvh_risks}
        )

    return {
        "analysis_objects": analysis_objects,
        "current_level": current_level,
        "residual_level": residual_level,
        "counters": {"untreated": untreated, "untreated_h_vh": untreated_h_vh, "accepted": accepted},
        "security_measure_status": {"labels": labels, "values": values},
    }


class ComposerListView(ListView):

    def get(self, request, *args, **kwargs):
        v = request.GET.get('analysis')
        if v:
            request_list = request.GET.getlist('analysis')[0]
            data = [item for item in request_list.split(',')]
            # debug print(f"got {len(data)} analysis in {data}")
            context = {'context': compile_analysis_for_composer(self.request.user, data)}
            return render(request, 'core/composer.html', context)
        else:
            (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
            context = {'context': Analysis.objects.filter(id__in=object_ids_view)}
            return render(request, 'core/project_select.html', context)


def index(request):
    return HttpResponse("Hello, world. You're at the core index.")


@login_required
def export_risks_csv(request, analysis):
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, Analysis)
    if UUID(analysis) in object_ids_view:
        ra = get_object_or_404(Analysis, pk=analysis)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="RA-{ra.id}-{ra.project}-v-{ra.version}.csv"'

        writer = csv.writer(response, delimiter=';')
        columns = ['rid', 'threat', 'name', 'scenario',
                'existing_measures', 'current_level', 'measures', 'residual_level',
                'treatment']
        writer.writerow(columns)

        for ri in ra.riskscenario_set.all():
            security_measures = ''
            for mtg in ri.security_measures.all():
                security_measures += f"[{mtg.status}]{mtg.name} \n"
            row = [ri.rid, ri.threat, ri.name, ri.description,
                ri.existing_measures, ri.get_current_risk()['name'],
                security_measures, ri.get_residual_risk()['name'], ri.treatment,
                ]
            writer.writerow(row)

        return response
    else:
        raise PermissionDenied()


@login_required
def export_mp_csv(request, analysis):
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, Analysis)
    if UUID(analysis) in object_ids_view:
        ra = get_object_or_404(Analysis, pk=analysis)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="MP-{ra.id}-{ra.project}-v-{ra.version}.csv"'

        writer = csv.writer(response, delimiter=';')
        columns = ['risk_scenario',
                'measure_id', 'measure_name', 'measure_desc', 'type', 'security_function', 'eta', 'effort', 'link', 'status',
                ]
        writer.writerow(columns)
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, SecurityMeasure)
        for mtg in SecurityMeasure.objects.filter(id__in=object_ids_view).filter(riskscenario__analysis=analysis):
            risk_scenarios = []
            for rs in mtg.riskscenario_set.all():
                risk_scenarios.append(str(rs.rid) + ": " + rs.name)
            row = [risk_scenarios,
                mtg.id, mtg.name, mtg.description, mtg.type, mtg.security_function, mtg.eta, mtg.effort, mtg.link, mtg.status,
                ]
            writer.writerow(row)

        return response
    else:
        raise PermissionDenied()


def scoring_assistant(request):
    template = 'core/scoring.html'
    context = {}
    (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), request.user, RiskMatrix)
    context['matrices'] = list(RiskMatrix.objects.all().values_list('json_definition', flat=True))
    return render(request, template, context)


def show_risk_matrix(request):
    template = 'core/risk_matrix.html'
    context = {}
    return render(request, template, context)


class ReviewView(ListView):
    template_name = 'core/review.html'
    context_object_name = 'context'
    model = Analysis
    ordering = 'id'

    def get_queryset(self):
        (object_ids_view, object_ids_change, object_ids_delete) = RoleAssignment.get_accessible_object_ids(
            Folder.objects.get(content_type=Folder.ContentType.ROOT), self.request.user, Analysis)
        mode = self.request.GET.get('mode')
        if mode == "all":
            return Analysis.objects.filter(id__in=object_ids_view)
        return Analysis.objects.filter(id__in=object_ids_view).filter(auditor=self.request.user)
