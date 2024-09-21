from .settings import settings


def tkinter_schedule_vis(schedule, days, capture_name='tkCapture', dir_name='log_0', capture=True):

    if not (settings.TKCAPTURE and capture and settings.DEBUG):
        return False

    return True
