from django.urls import path
from django.urls.conf import include
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.index), name='index'),
    path('i18n/', include('django.conf.urls.i18n')),

    path('quick-start', login_required(views.QuickStartView.as_view()), name='quick_start'),
    path('scoring-assistant', login_required(views.scoring_assistant), name='scoring_bo'),

    # LIST VIEWS
    path('risk-analyses/', login_required(views.RiskAnalysisListView.as_view()), name='ra-list'),
    path('risk-scenarios/', login_required(views.RiskScenarioListView.as_view()), name='ri-list'),
    path('security-measures/', login_required(views.SecurityMeasureListView.as_view()), name='mtg-list'),
    path('risk-acceptances/', login_required(views.RiskAcceptanceListView.as_view()), name='acceptance-list'),

    path('projects-domains/', login_required(views.FolderListView.as_view()), name='pd-list'),
    path('projects/', login_required(views.ProjectListView.as_view()), name='project-list'),
    path('assets/', login_required(views.AssetListView.as_view()), name='asset-list'),
    path('threats/', login_required(views.ThreatListView.as_view()), name='threat-list'),
    path('security-functions/', login_required(views.SecurityFunctionListView.as_view()), name='security-function-list'),

    path('users/', login_required(views.UserListView.as_view()), name='user-list'),
    path('user_groups/', login_required(views.UserGroupListView.as_view()), name='user_group-list'),
    path('roles/', login_required(views.RoleAssignmentListView.as_view()), name='role-list'),
    path('matrices/', login_required(views.RiskMatrixListView.as_view()), name='matrix-list'),
    path('matrices/<str:pk>', login_required(views.RiskMatrixDetailedView.as_view()), name='matrix-detailed'),
    path('profile', login_required(views.MyProfileDetailedView.as_view()), name='user-detailed'),

    # CREATE VIEWS
    path('risk-analyses/create', login_required(views.RiskAnalysisCreateView.as_view()), name='analysis-create'),
    path('risk-analyses/create-modal/', login_required(views.RiskAnalysisCreateView.as_view()), name='analysis-create-modal'),
    
    path('security-measures/create-modal/', login_required(views.SecurityMeasureCreateViewModal.as_view()), name='measure-create-modal'),
    
    path('risk_acceptances/create-modal/', login_required(views.RiskAcceptanceCreateViewModal.as_view()), name='acceptance-create-modal'),
    
    path('security-functions/create-modal/', login_required(views.SecurityFunctionCreateViewModal.as_view()), name='security-function-create-modal'),
    
    path('threats/create-modal/', login_required(views.ThreatCreateViewModal.as_view()), name='threat-create-modal'),

    path('risk-analyses/<int:parent_analysis>/risk_scenario/create', login_required(views.RiskScenarioCreateView.as_view()), name='risk-scenario-create'),
    path('risk-scenarios/create', login_required(views.RiskScenarioCreateViewModal.as_view()), name='risk-scenario-create-modal'),

    path('projects-domains/create', login_required(views.FolderCreateView.as_view()), name='pd-create'),
    path('projects-domains/create_modal/', login_required(views.FolderCreateViewModal.as_view()), name='pd-create-modal'),

    path('projects/create', login_required(views.ProjectCreateView.as_view()), name='project-create'),
    path('projects/create_modal/', login_required(views.ProjectCreateViewModal.as_view()), name='project-create-modal'),
    
    path('assets/create/', login_required(views.AssetCreateView.as_view()), name='asset-create'),
    path('assets/create_modal/', login_required(views.AssetCreateViewModal.as_view()), name='asset-create-modal'),

    
    path('users/create', login_required(views.UserCreateView.as_view()), name='user-create'),
    path('user-groups/create', login_required(views.UserGroupCreateView.as_view()), name='user_group-create'),

    path('role-assignments/create', login_required(views.RoleAssignmentCreateView.as_view()), name='role-assignment-create'),
    
    # path('risk_scenario/create-modal', login_required(views.RiskScenarioCreateViewModal.as_view()), name='ri-create-modal'),
    
    # UPDATE VIEWS
    path('risk-analyses/<str:pk>', login_required(views.RiskAnalysisUpdateView.as_view()), name='ra-update'),
    path('risk-scenarios/<str:pk>', login_required(views.RiskScenarioUpdateView.as_view()), name='ri-update'),
    path('risk-scenarios/update_modal', login_required(views.RiskScenarioUpdateViewModal.as_view()), name='ri-update-modal'),
    path('security-measures/<str:pk>', login_required(views.SecurityMeasureUpdateView.as_view()), name='mtg-update'),
    path('risk-acceptances/<str:pk>', login_required(views.RiskAcceptanceUpdateView.as_view()), name='acceptance-update'),
    path('threats/<str:pk>', login_required(views.ThreatUpdateView.as_view()), name='threat-update'),
    path('security-functions/<str:pk>', login_required(views.SecurityFunctionUpdateView.as_view()), name='security-function-update'),

    path('projects-domains/<str:pk>', login_required(views.FolderUpdateView.as_view()), name='pd-update'),
    path('projects/<str:pk>', login_required(views.ProjectUpdateView.as_view()), name='project-update'),
    path('assets/<str:pk>', login_required(views.AssetUpdateView.as_view()), name='asset-update'),

    path('users/<str:pk>', login_required(views.UserUpdateView.as_view()), name='user-update'),
    path('my-profile/<str:pk>', login_required(views.MyProfileUpdateView.as_view()), name='me-update'),
    path('users/<str:pk>/password', login_required(views.UserPasswordChangeView.as_view()), name='password-change'),
    path('user-groups/<str:pk>', login_required(views.UserGroupUpdateView.as_view()), name='user_group-update'),
    path('role-assignments/<str:pk>', login_required(views.RoleAssignmentUpdateView.as_view()), name='role-assignment-update'),
    
    # DELETE VIEWS
    path('risk-analyses/<str:pk>/delete/', login_required(views.RiskAnalysisDeleteView.as_view()), name='analysis-delete'),
    path('risk-scenarios/<str:pk>/delete/', login_required(views.RiskScenarioDeleteView.as_view()), name='risk-scenario-delete'),
    path('risk-acceptances/<str:pk>/delete/', login_required(views.RiskAcceptanceDeleteView.as_view()), name='risk-acceptance-delete'),
    path('security-measures/<str:pk>/delete/', login_required(views.SecurityMeasureDeleteView.as_view()), name='measure-delete'),
    path('projects/<str:pk>/delete/', login_required(views.ProjectDeleteView.as_view()), name='project-delete'),
    path('assets/<str:pk>/delete/', login_required(views.AssetDeleteView.as_view()), name='asset-delete'),
    path('security-functions/<str:pk>/delete/', login_required(views.SecurityFunctionDeleteView.as_view()), name='security-function-delete'),
    path('projects-domains/<str:pk>/delete/', login_required(views.FolderDeleteView.as_view()), name='pd-delete'),
    path('threats/<str:pk>/delete/', login_required(views.ThreatDeleteView.as_view()), name='threat-delete'),

    path('users/<str:pk>/delete', login_required(views.UserDeleteView.as_view()), name='user-delete'),
    path('user-groups/<str:pk>/delete', login_required(views.UserGroupDeleteView.as_view()), name='user_group-delete'),

    path('role-assignments/<str:pk>/delete', login_required(views.RoleAssignmentDeleteView.as_view()), name='role-assignment-delete'),
]