import copy
from ..subject import Subject
from ..debug_log import *


def create_class_schedule(days):
    """
    :param days: list of days that the lessons can be in
    :return: empty schedule of passed in days
    """
    new_class_schedule = {}
    for day in days:
        new_class_schedule[day] = []
    return new_class_schedule


def move_subject_to_day(self, class_id, day_to, day_from, subject_position,
                        subject_to_position=-1, group=None):
    try:
        old = self.data[class_id][day_from][subject_position]
    except IndexError:
        raise BaseException

    if old[0].is_empty:
        return False

    first_lesson = find_first_lesson_index(self.data[class_id][day_from])

    if subject_position == first_lesson:
        self.data[class_id][day_from][first_lesson] = [Subject(
            is_empty=True,
            lesson_hour_id=first_lesson,
        )]
    elif subject_position == -1:
        self.data[class_id][day_from].pop()
    else:
        if group is None:
            return False

        old = self.data[class_id][day_from][subject_position][group - 1]
        try:
            self.data[class_id][day_from][subject_position][group - 1] = Subject(
                is_empty=True,
                lesson_hour_id=subject_position,
                group=group
            )
        except IndexError:
            return False

    if subject_to_position == -1:
        self.data[class_id][day_to].append(old)

        if len(self.data[class_id][day_to]) > 1:
            if subject_position == first_lesson:
                for subject in self.data[class_id][day_to][-1]:
                    subject.lesson_hour_id = (len(self.data[class_id][day_to]) - 1)

            else:
                for subject in self.data[class_id][day_to][-1]:
                    subject.lesson_hour_id = \
                        self.data[class_id][day_to][subject_position - 1][0].lesson_hour_id + 1

        elif len(self.data[class_id][day_to]) == 1:
            for subject in self.data[class_id][day_to][-1]:
                subject.lesson_hour_id = 1

        else:
            for subject in self.data[class_id][day_to][-1]:
                subject.lesson_hour_id = 0
    else:
        if not len(self.data[class_id][day_to][subject_to_position]):
            self.data[class_id][day_to][subject_to_position] = [old]
        elif self.data[class_id][day_to][subject_to_position][0].is_empty:
            self.data[class_id][day_to][subject_to_position] = [old]
        else:
            self.data[class_id][day_to][subject_to_position].append(old)

        try:
            self.data[class_id][day_to][subject_to_position][-1].lesson_hour_id = subject_to_position
        except AttributeError:
           pass

    return True


def swap_subject_in_groups(self, group, subjects_list_x, subjects_list_y):
    group -= 1
    (
        subjects_list_x[group].lesson_hour_id,
        subjects_list_y[group].lesson_hour_id
    ) = (
        subjects_list_y[group].lesson_hour_id,
        subjects_list_x[group].lesson_hour_id
    )

    (
        subjects_list_x[group],
        subjects_list_y[group]
    ) = (
        subjects_list_y[group],
        subjects_list_x[group]
    )


def safe_move(self, teachers_id, day_from, day_to, subject_position, subject_new_position, class_id,
              days, teachers, group=None):
    """
    :param self: class schedule
    :param teachers_id: ids of teachers to check
    :param day_from: day which we take subject from
    :param day_to: day which we add subject to
    :param subject_position: old position of subject
    :param subject_new_position: new position to add subject to
    :param class_id: class of subject moved
    :param days: list of days
    :param teachers: list of all teachers
    :param group: class group to move
    :description: before trying to move using move_subject_to_day(), function checks if action is possible
    and notifies program
    :return: was operation successful
    """

    subject_to_position = lesson_index = None
    if subject_new_position == 0:
        first_lesson_index = find_first_lesson_index(self.data[class_id][day_to])

        if first_lesson_index is None:
            subject_to_position = -1
            lesson_index = 0
        elif first_lesson_index != 0:
            if self.data[class_id][day_to][first_lesson_index - 1][0].movable:
                subject_to_position = lesson_index = first_lesson_index - 1
            else:
                return False
        else:
            return False

    elif subject_new_position == -1:
        subject_to_position = -1
        lesson_index = len(self.data[class_id][day_to])

    elif subject_new_position < find_first_lesson_index(
            self.data[class_id][day_from]
    ):
        raise BaseException

    old_schedule = copy.deepcopy(self.data)

    if not self.are_teachers_taken(
        teachers_id=teachers_id,
        day=day_to,
        lesson_index=lesson_index,
    ) and self.check_teacher_conditions(
        teachers_id=teachers_id,
        day=day_to,
        days=days,
        lesson_index=lesson_index,
        teachers=teachers
    ):
        if not self.move_subject_to_day(
                class_id=class_id,
                day_to=day_to,
                day_from=day_from,
                subject_position=subject_position,
                subject_to_position=subject_to_position,
                group=group,
        ):
            raise BaseException
        return True
    return False


def get_same_time_teacher(self, day_to, lesson_index):
    same_time_teachers = []
    for class_schedule_id in self.data:
        try:
            subjects_list = self.data[class_schedule_id][day_to][lesson_index]
            for subject in subjects_list:
                for teacher_id in subject.teachers_id:
                    same_time_teachers.append(teacher_id)
        except IndexError:
            pass
    return same_time_teachers


def get_same_time_classrooms(self, day, lesson_index):
    same_time_classrooms = []
    for class_schedule_id in self.data:
        try:
            subjects_list = self.data[class_schedule_id][day][lesson_index]
            for subject in subjects_list:
                if subject.classroom_id is not None:
                    same_time_classrooms.append(subject.classroom_id)
        except IndexError:
            pass
    return same_time_classrooms


def get_stacked_lessons(self, class_id, day, group, lesson_index=0):
    class_schedule = self.data[class_id][day]

    if lesson_index == 0:
        lesson_index = self.find_first_lesson_index(class_schedule)

    subject = class_schedule[lesson_index][group-1]
    stacked_subjects = [subject]

    if lesson_index == class_schedule[-1][0].lesson_hour_id:
        return stacked_subjects, stacked_subjects[-1].lesson_hour_id

    for subject_list in class_schedule[lesson_index+1:]:
        for current_subject in subject_list:
            if current_subject.group != group or current_subject.subject_id != subject.subject_id:
                return stacked_subjects, stacked_subjects[-1].lesson_hour_id

            stacked_subjects.append(current_subject)

    return stacked_subjects, stacked_subjects[-1].lesson_hour_id


def find_another_grouped_lessons(self, class_id, lesson_day, lesson_index, number_of_groups, days):
    class_schedule = self.data[class_id]
    possibilities = []
    for day in days:
        class_schedule_at_day = class_schedule[day]
        for subjects_list in class_schedule_at_day:
            if (
                    (
                            lesson_day == day
                            and lesson_index == subjects_list[0].lesson_hour_id
                            and subjects_list[0].number_of_groups != number_of_groups
                    )
                    or len(subjects_list) <= 1
            ):
                continue
            else:
                possibilities.append([day, subjects_list[0].lesson_hour_id, subjects_list])

    return possibilities


def find_first_lesson_index(schedule_at_day):
    for i, subjects in enumerate(schedule_at_day):
        for subject in subjects:
            if not subject.is_empty:
                return i
    return None


def get_num_of_lessons(schedule_at_day):
    first_lesson_index = find_first_lesson_index(schedule_at_day)
    return len(schedule_at_day[first_lesson_index:])
