def format_schedule(self, conditions, days, teachers, classrooms, classes_id,
                    classes_start_hour_index, days_ordered):
    if self.valid is False:
        return self

    return self.update_min_day_len(
        conditions,
        days,
        teachers,
    ).add_classrooms(
        classrooms,
        teachers,
        days
    )
