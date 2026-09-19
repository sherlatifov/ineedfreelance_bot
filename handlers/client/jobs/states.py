from aiogram.fsm.state import State, StatesGroup


class CreateJobStates(StatesGroup):
    choosing_category = State()
    entering_title = State()
    entering_description = State()
    entering_budget = State()
    choosing_currency = State()
    choosing_deadline = State()
    uploading_files = State()
    preview = State()