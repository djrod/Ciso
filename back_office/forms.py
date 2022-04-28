from django.forms import CharField, CheckboxInput, DateInput, DateTimeInput, EmailInput, HiddenInput, ModelForm, NullBooleanSelect, NumberInput, PasswordInput, Select, SelectMultiple, TextInput, Textarea, TimeInput, URLInput, widgets

from django.contrib.auth.models import User, Group
from core.models import Analysis, Mitigation, RiskAcceptance, RiskInstance
from general.models import ParentRisk, Project, ProjectsGroup, Solution

class StyledModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        text_inputs = (TextInput, NumberInput, EmailInput, URLInput, PasswordInput, HiddenInput, DateInput, DateTimeInput, TimeInput, Textarea)
        select_inputs = (Select, SelectMultiple, NullBooleanSelect)
        for fname, f in self.fields.items():
            input_type = f.widget.__class__
            # input_type = str(f.widget.__class__).split('.')[-1].strip("'>")
            if input_type in text_inputs or input_type in select_inputs:
                f.widget.attrs['class'] = 'w-full rounded-md'

class RiskAnalysisCreateForm(StyledModelForm):
    class Meta:
        model = Analysis
        fields = ['project', 'auditor', 'is_draft', 'rating_matrix', 'comments']

class MeasureCreateForm(StyledModelForm):
    class Meta:
        model = Mitigation
        fields = '__all__'
        labels = {
            'risk_instance': 'Risk Scenario',
            'solution': 'Security Function',
        }
        
class SecurityFunctionCreateForm(StyledModelForm):
    class Meta:
        model = Solution
        fields = '__all__'

class ThreatCreateForm(StyledModelForm):
    class Meta:
        model = ParentRisk
        fields = '__all__'

class UserCreateForm(StyledModelForm):
    class Meta:
        model = User
        fields = '__all__'

class RiskAnalysisUpdateForm(StyledModelForm):
    class Meta:
        model = Analysis
        fields = ['project', 'auditor', 'version', 'is_draft', 'rating_matrix', 'comments']

class RiskInstanceCreateForm(StyledModelForm):
    class Meta:
        model = RiskInstance
        exclude = ['analysis', 'residual_level', 'current_level']

class RiskInstanceUpdateForm(StyledModelForm):
    class Meta:
        model = RiskInstance
        fields = '__all__'
        exclude = ['current_level', 'residual_level']

class MitigationUpdateForm(StyledModelForm):
    class Meta:
        model = Mitigation
        exclude = ['risk_instance']

class ProjectsGroupUpdateForm(StyledModelForm):
    class Meta:
        model = ProjectsGroup
        fields = '__all__'

class ProjectUpdateForm(StyledModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class SecurityFunctionUpdateForm(StyledModelForm):
    class Meta:
        model = Solution
        fields = '__all__'

class ThreatUpdateForm(StyledModelForm):
    class Meta:
        model = ParentRisk
        fields = '__all__'

class RiskAcceptanceCreateUpdateForm(StyledModelForm):
    class Meta:
        model = RiskAcceptance
        fields = '__all__'

class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = '__all__'