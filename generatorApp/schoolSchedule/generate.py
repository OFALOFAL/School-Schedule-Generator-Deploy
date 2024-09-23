import os.path
from itertools import product
from .schedule_conditions import *
from .school_class import *
from .schedule import *
from .classroom import *
from .subject import *
from .teacher import *
from .tkinter_schedule_vis import *
import os
import shutil


def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)


def generate_schedule(data, schedule_settings):
    """
    :param data: list of data in strict order of: [lesson_hours_df, subject_names_df, subjects_df, teachers_df, classes_df, classrooms_df]
    :param schedule_settings: dictionary of settings for schedule
    :return: generates a full schedule for all the classes where none of the same elements (teachers/clasrooms) appears
    in the same time
    """

    min_lessons_per_day, max_lessons_per_day = schedule_settings["min_lessons_per_day"], schedule_settings["max_lessons_per_day"]
    days = schedule_settings["days"]

    # Creating global schedule conditions
    conditions = ScheduleConditions(min_lessons_per_day=min_lessons_per_day, max_lessons_per_day=max_lessons_per_day)

    schedule = False
    for i, days_order in enumerate(permutations(days, len(days))):
        version = i

        # splitting data to separate dataframes
        [
            _,
            _,
            subjects_df,
            teachers_df,
            classes_df,
            classrooms_df,
            _
        ] = copy.deepcopy(data)

        # gathering basic information from dataframes
        classes_id, classes_start_hour_index = SchoolClass.get_classes_data(classes_df)
        teachers = create_teachers(teachers_df)
        subjects = split_subjects(subjects_df, teachers, classes_id)
        classrooms = create_classrooms(classrooms_df)

        # TODO: fix; somhere schedule is not validating, check if settings are correct, they aren't saved rn
        schedule = Schedule(version=version).create(
            classes_id=classes_id,
            classes_start_hour_index=classes_start_hour_index,
            conditions=conditions,
            days=days,
            days_ordered=days_order,
            subjects=subjects,
            teachers=teachers,
        ).split_to_groups(
            days,
            conditions,

        ).format_schedule(
            conditions,
            days=days,
            teachers=teachers,
            classrooms=classrooms,
            classes_id=classes_id,
            classes_start_hour_index=classes_start_hour_index,
            days_ordered=days_order,
        )

        if schedule.valid:
            break

    if schedule.valid:
        return schedule.data
    else:
        return None
