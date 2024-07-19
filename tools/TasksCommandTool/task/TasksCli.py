import cmd
import json
import os

from .Task import Task, _ALL_TASKS, _ORIGINAL_TASKS, InterpretedTask, _TASK_PIPELINE_INFO_FIELDS
from .TaskField import TaskFieldEnum, get_fields_with_algorithm, get_fields
from .TaskType import AlgorithmType, ActionType
from .TemplateGUI import show_template
from .TaskUtils import project_root_path

json_path = project_root_path / 'resource' / 'tasks.json'


# noinspection PyMethodMayBeStatic
class TasksCommandTool(cmd.Cmd):
    prompt = 'tasks> '
    use_template_gui = True

    def disable_gui(self):
        self.use_template_gui = False

    def get_task(self, arg):
        task = Task.get(arg)
        if task is None:
            raise ValueError(f"Task {arg} not found.")
        return task

    def do_load(self, arg):
        """Load tasks from a json file."""
        global json_path
        if arg:
            json_path = os.path.abspath(arg)
        print(f"Loading tasks from {json_path}")
        success_count = 0
        fail_count = 0
        with open(json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            for name, task_dict in tasks.items():
                try:
                    Task(name, task_dict).define()
                    success_count += 1
                except Exception as e:
                    print(f"Error loading task {name}: {e}")
                    fail_count += 1
        print(f"Loaded {success_count} tasks, {fail_count} failed.")

    def do_find(self, arg):
        """Find a task by name."""
        self.print_task(self.get_task(arg))

    def complete_find(self, text, line, begidx, endidx):
        return [name for name in _ORIGINAL_TASKS if name.startswith(text)]

    def choices(self, text, choices):
        for i, choice in enumerate(choices):
            print(f"({i}) {choice}")
        input_choice = -1
        while input_choice < 0 or input_choice >= len(choices):
            try:
                input_choice = int(input(text))
            except KeyboardInterrupt:
                return None
            except ValueError:
                pass
        return choices[input_choice]

    def do_create(self, arg):
        """Create a task."""
        task_name = input("Task name:")
        task_algorithm = self.choices("Please choose an algorithm:\n", [a.value for a in AlgorithmType])
        task_dict = {TaskFieldEnum.ALGORITHM.value.field_name: task_algorithm}
        for field in get_fields_with_algorithm(task_algorithm):
            if field == TaskFieldEnum.ALGORITHM.value:
                continue
            if field == TaskFieldEnum.ACTION.value:
                value = self.choices("Please choose an action:\n", [a.value for a in ActionType])
            else:
                value = input(f"{field.field_name} ({field.field_doc}):")
            if ',' in value:
                value = value.split()
            if not value:
                value = field.field_default
            if value:
                task_dict[field.field_name] = value
        print(task_dict)

    def print_task(self, task: Task):
        print(f"Task {task.name}:")
        for key, value in task.to_task_dict().items():
            print(f"{key}: {value}")
        if self.use_template_gui and task.algorithm == AlgorithmType.MatchTemplate:
            show_template(task.template)

    def do_exec(self, arg):
        """Execute a task by name."""
        self.print_task(self.get_task(arg).interpret())

    def show_task(self, task: InterpretedTask):
        for field in get_fields(lambda x: x in _TASK_PIPELINE_INFO_FIELDS):
            if task.to_task_dict():
                print(field.field_name)
                if getattr(task, field.python_field_name) is not None:
                    print(' -> '.join(['   |', *getattr(task, field.python_field_name)]))

    def do_show(self, arg):
        """Show all tasks."""
        self.show_task(self.get_task(arg).interpret())

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except Exception as e:
            print(e)
