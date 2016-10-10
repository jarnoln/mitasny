from .models import Phase


def check_phase(name):
    if Phase.objects.filter(name=name).count() == 0:
       return 'Phase %s not defined' % name
    if Phase.objects.filter(name=name).count() > 1:
        return 'Multiple phases with name: %s' % name
    return ''


def check_validity():
    invalidities = []
    phase_names = ['pending', 'ongoing', 'continuing', 'finished', 'done', 'blocked', 'impediment']
    for phase_name in phase_names:
        msg = check_phase(phase_name)
        if msg:
            invalidities.append(msg)
    return invalidities
