from .forms import AppealForm


def inject_form(request):
    return {'appeal_form': AppealForm()}
